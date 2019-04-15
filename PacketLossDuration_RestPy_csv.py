#Python Test to get Packet Loss Duration Statistics
# CLI arguments parsing

# USAGE
# 1. Update "Preference Settings" section below
# 2. Launch with desired traffic generation parameters
#    python <script>.py <frame rate percentage of line rate> <frame size> [api_session_id api_session_key]

#---------- Preference Settings --------------
forceTakePortOwnership = True
releasePortsWhenDone = False
debugMode = False
logFile = False

apiServerIp = '10.36.237.142'
#apiServerIp = '10.211.55.3'
apiServerPort = '443'    # Use 443 for linux or 11009 for windows API server
#apiServerPort = '11009'    # Use 443 for linux or 11009 for windows API server
apiServerUsername = 'admin' # Only used for linux API server
apiServerPassword = 'admin' # Only used for linux API server
osPlatform = 'linux'        # linux or windows
#osPlatform = 'windows'        # linux or windows

ixChassisIp = '10.36.237.142'
# [chassisIp, cardNumber, slotNumber]
portList = [[ixChassisIp, '1', '1'], [ixChassisIp, '1', '2']]
portMediaType = 'fiber' # copper, fiber or SGMII


# The IP address for your Ixia license server(s) in a list.
licenseServerIp = ['10.36.237.142']
# subscription, perpetual or mixed
licenseMode = 'perpetual'
# tier1, tier2, tier3, tier3-10g
licenseTier = 'tier3'

configFile = 'bgp_ngpf_8.30.ixncfg'

#---------- Preference Settings End --------------

import sys, os, traceback
import json
import time, datetime
import csv

import requests
requests.packages.urllib3.disable_warnings()

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
    print("Usage: %s frame_rate_percent frame_size [api_session_id api_session_key]" % (sys.argv[0]))

# Parse arguments
if len(sys.argv) < 3:
    usage()
    sys.exit()
    
# Assemble an API URL base
frame_rate_percent = float(sys.argv[1])
frame_size  = int(sys.argv[2])

if osPlatform == 'windows':
    deleteSessionAfterTest = False
else: 
    deleteSessionAfterTest = True   # see below for 'keep' parameter to override this
    
if len(sys.argv) > 3:
    if sys.argv[3] == 'keep':   # the request is to create a new session and to keep it after the test is finished
        api_session_id = None # will create a new session
        api_session_key = None
    else:
        api_session_id = sys.argv[3]
        if len(sys.argv) != 5:
            print("Error: api_session_key is required if api_sesson_id is specified")
            usage()
            sys.exit()
        else:
            api_session_key = sys.argv[4]
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
    testPlatform = TestPlatform(apiServerIp, rest_port=apiServerPort, platform=osPlatform, log_file_name='restpy.log')

    # Console output verbosity: None|request|'request response'
    testPlatform.Trace = 'request_response'

    testPlatform.Authenticate(apiServerUsername, apiServerPassword)
    session = testPlatform.Sessions.add()

    ixNetwork = session.Ixnetwork
    ixNetwork.NewConfig()

    ixNetwork.info('Loading config file: {0}'.format(configFile))
    ixNetwork.LoadConfig(Files(configFile, local_file=True))

    ixNetwork.Globals.Licensing.LicensingServers = licenseServerIp
    ixNetwork.Globals.Licensing.Mode = licenseMode
    ixNetwork.Globals.Licensing.Tier = licenseTier

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

    # Get the Traffic Item name for getting Traffic Item statistics.
    trafficItem = ixNetwork.Traffic.TrafficItem.find()[0]

    # Enable tracking of packet loss duration
    ixNetwork.Traffic.Statistics.PacketLossDuration.Enabled = True
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
        testwriter.writerow(['Test #', 'Test scope', 'Iterration #', 'FAILURE Loss Duration, ms', 'RECOVERY Loss Duration, ms'])

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

    #if osPlatform == 'linux':
    #    mainObj.linuxServerStopAndDeleteSession()

    #if osPlatform == 'windowsConnectionMgr':
    #    mainObj.deleteSession()

    print('Exiting...')

    if debugMode:
        # For Linux and Windows Connection Manager only
        session.remove()

except Exception as errMsg:
    print('\n%s' % traceback.format_exc())
    if debugMode and 'session' in locals():
        session.remove()
