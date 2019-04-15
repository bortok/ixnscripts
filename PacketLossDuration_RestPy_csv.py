#!/usr/bin/env python

###############################################################################
#
# IxNetwork Automation Script get Packet Loss Duration Statistics
#
# File: PacketLossDuration_RestPy_csv.py
# Author: Alex Bortok (https://github.com/bortok)
#
# Description: IxNetwork Automation Script get Packet Loss Duration Statistics
#
# COPYRIGHT 2019 Keysight Technologies.
#
# USAGE
# 1. Update "ixn_preferences.py" file
# 2. Launch with desired traffic generation parameters
#    python <script>.py <API server IP address> <API_server_platform: linux|windows> [api_session_id api_session_key]
#
###############################################################################

import sys, os, traceback
import subprocess
import json
import time, datetime
import csv

import requests
requests.packages.urllib3.disable_warnings()

from ixn_preferences import *

# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.files import Files
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant

# Helpers
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def isFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False

def usage():
    print("Usage: %s api_server_ip linux|windows ixn_config_file [api_session_id api_session_key]" % (sys.argv[0]))

# Parse arguments
if len(sys.argv) < 4:
    usage()
    sys.exit()

apiServerIp = sys.argv[1]
osPlatform  = sys.argv[2]
configFile  = sys.argv[3]

if osPlatform == 'windows':
    apiServerPort = '11009'
    deleteSessionAfterTest = False
else:
    apiServerPort = '443'
    deleteSessionAfterTest = True   # see below for 'keep' parameter to override this

if len(sys.argv) > 4:
    if sys.argv[4] == 'keep':   # the request is to create a new session and to keep it after the test is finished
        api_session_id = None # will create a new session
        api_session_key = None
    else:
        api_session_id = sys.argv[4]
        if len(sys.argv) != 6:
            print("Error: api_session_key is required if api_sesson_id is specified")
            usage()
            sys.exit()
        else:
            api_session_key = sys.argv[5]
    deleteSessionAfterTest = False
else:
    api_session_id = None # will create a new session
    api_session_key = None

#Test Functions
 
def getPackLossDuration():
    stats = trafficItemStatistics
    print("DEBUG STATS JSON\n%s" % (stats))
    value_str = stats.Rows[0]['Packet Loss Duration (ms)']
    print("Packet loss duration: %s ms" % (value_str))
    if isFloat(value_str):
        value = float(value_str)
    else:
        value = 0.0
    return value


# The traffic item name to get stats from for this sample script
trafficItemName = 'Topo-BGP'

try:
    testPlatform = TestPlatform(apiServerIp, rest_port=apiServerPort, platform=osPlatform, log_file_name=logFile)

    testPlatform.Trace = debugMode

    if osPlatform == 'linux':
        testPlatform.Authenticate(apiServerUsername, apiServerPassword)
        if api_session_id == None:
            session = testPlatform.Sessions.add()
        else:
            session = testPlatform.Sessions.find(Id=api_session_id)

    if osPlatform == 'windows':
        # Windows support only one session. Id is always equal 1.
        session = testPlatform.Sessions.find(Id=1)
        
    print("API Session ID: %d" % (session.Id))

    ixNetwork = session.Ixnetwork
    #if api_session_key != None:
    #    ixNetwork.ApiKey = api_session_key
    #else:
    #    api_session_key = ixNetwork.ApiKey
    #    print("API Session KEY: %s" % (api_session_key))

    ixNetwork.NewConfig()

    ixNetwork.Globals.Licensing.LicensingServers = licenseServerIp
    ixNetwork.Globals.Licensing.Mode = licenseMode
    ixNetwork.Globals.Licensing.Tier = licenseTier

    ixNetwork.info('Loading config file: {0}'.format(configFile))
    ixNetwork.LoadConfig(Files(configFile, local_file=True))

    # Assign ports
    testPorts = []
    vportList = [vport.href for vport in ixNetwork.Vport.find()]
    for port in portList:
        testPorts.append(dict(Arg1=port[0], Arg2=port[1], Arg3=port[2]))

    ixNetwork.AssignPorts(testPorts, [], vportList, forceTakePortOwnership)

    ixNetwork.StartAllProtocols(Arg1='sync')

    ixNetwork.info('Verify protocol sessions\n')
    protocolsSummary = StatViewAssistant(ixNetwork, 'Protocols Summary')
    protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
    protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
    ixNetwork.info(protocolsSummary)

    # Enable tracking of packet loss duration
    ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = True
    # Get the Traffic Item name for getting Traffic Item statistics.
    for trafficItem in ixNetwork.Traffic.TrafficItem.find():
        trafficItem.Generate()
        
    ixNetwork.Traffic.Apply()
    ixNetwork.Traffic.Start()

    # StatViewAssistant could also filter by regex, LESS_THAN, GREATER_THAN, EQUAL. 
    # Examples:
    #    flowStatistics.AddRowFilter('Port Name', StatViewAssistant.REGEX, '^Port 1$')
    #    flowStatistics.AddRowFilter('Tx Frames', StatViewAssistant.LESS_THAN, 50000)

    trafficItemStatistics = StatViewAssistant(ixNetwork, 'Traffic Item Statistics')
    ixNetwork.info('{}\n'.format(trafficItemStatistics))
    
    # Get the statistic values
    txFrames = trafficItemStatistics.Rows[0]['Tx Frames']
    rxFrames = trafficItemStatistics.Rows[0]['Rx Frames']
    ixNetwork.info('\nTraffic Item Stats:\n\tTxFrames: {}  RxFrames: {}\n'.format(txFrames, rxFrames))

    # Initialize counters
    test_number = 0
    test_scope = ""
    test_iterrations_str = ""
    test_iterrations = 1
    test_iterration = 0

    today = datetime.datetime.today()
    csv_filename = today.strftime('packet_loss_tests_%Y_%m%d_%H%M.csv')
    with open(csv_filename, 'w', newline='') as csvfile:
        testwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        testwriter.writerow(['Test #', 'Test scope', 'Iterration #', 'FAILURE Loss Duration (ms)', 'RECOVERY Loss Duration (ms)'])

        while True:
            test_number = test_number + 1
            test_iterration = 0
            test_scope = input("Enter description of your test: ")
            test_iterrations_str = input("How many iterrations: ")
            while True:
                if isInt(test_iterrations_str):
                    test_iterrations = int(test_iterrations_str)
                    break
                else:
                    test_iterrations_str = input("Please enter a number, how many iterrations: ")
            
            print("Test number %d: %s" % (test_number, test_scope))
            while test_iterration < test_iterrations:
                test_iterration = test_iterration + 1
                ixNetwork.ClearStats()
                input("Starting the iteration #%d for FAILURE... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_failure = getPackLossDuration()
                ixNetwork.ClearStats()
                input("Starting the iteration #%d for RECOVERY... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_recovery = getPackLossDuration()
                testwriter.writerow([test_number, test_scope, test_iterration, loss_duration_failure, loss_duration_recovery])
            user_input = input("Another test? (Anything other than 'y' will kill it) ")
            if user_input != "y":
        	    break

    print('Stopping traffic. Wait...')
    ixNetwork.Traffic.Stop()
    ixNetwork.StopAllProtocols()
    print('stopped')

    if releasePortsWhenDone == True:
        ixNetwork.ReleasePorts(portList)

    if osPlatform == 'linux':
        # For Linux and Windows Connection Manager only
        session.remove()

    print('Exiting, here are the results:')
    subprocess.call(["column", "-ts,", csv_filename])

except Exception as errMsg:
    print('\n%s' % traceback.format_exc())
    if debugMode and 'session' in locals():
        session.remove()
