#Python Test to get Packet Loss Duration Statistics
# CLI arguments parsing

# USAGE
#    python <script>.py windows
#    python <script>.py linux

import sys, os, traceback

sys.path.insert(0, (os.path.dirname(os.path.abspath(__file__).replace('ixnscripts', 'IxNetwork/RestApi/Python/Modules'))))
from IxNetRestApi import *
from IxNetRestApiPortMgmt import PortMgmt
from IxNetRestApiTraffic import Traffic
from IxNetRestApiProtocol import Protocol
from IxNetRestApiStatistics import Statistics

# Default the API server to either windows, windowsConnectionMgr or linux.
osPlatform = 'windows'

if len(sys.argv) > 1:
    if sys.argv[1] not in ['windows', 'windowsConnectionMgr', 'linux']:
        sys.exit("\nError: %s is not a known option. Choices are 'windows', 'windowsConnectionMgr or 'linux'." % sys.argv[1])
    osPlatform = sys.argv[1]

try:
    #---------- Preference Settings --------------
    forceTakePortOwnership = True
    releasePortsWhenDone = False
    enableDebugTracing = True
    deleteSessionAfterTest = False ;# For Windows Connection Mgr and Linux API server only

    licenseServerIp = '10.36.237.207'
    licenseModel = 'perpetual'

    ixChassisIp = '10.36.237.207'
    # [chassisIp, cardNumber, slotNumber]
    portList = [[ixChassisIp, '2', '9'], [ixChassisIp, '2', '10']]

    if osPlatform == 'linux':
        mainObj = Connect(apiServerIp='10.36.237.207',
                          serverIpPort='443',
                          username='admin',
                          password='admin',
                          deleteSessionAfterTest=deleteSessionAfterTest,
                          verifySslCert=False,
                          serverOs=osPlatform,
                          generateLogFile='ixiaDebug.log'
                          )

    if osPlatform in ['windows', 'windowsConnectionMgr']:
        mainObj = Connect(apiServerIp='10.211.55.3',
                          serverIpPort='11009',
                          serverOs=osPlatform,
                          deleteSessionAfterTest=True,
                          generateLogFile='ixiaDebug.log'
                          )
        
    #---------- Preference Settings End --------------
except (IxNetRestApiException, Exception, KeyboardInterrupt):
    if enableDebugTracing:
        if not bool(re.search('ConnectionError', traceback.format_exc())):
            print('\n%s' % traceback.format_exc())

    if 'mainObj' in locals() and osPlatform == 'linux':
        if deleteSessionAfterTest:
            mainObj.linuxServerStopAndDeleteSession()

    if 'mainObj' in locals() and osPlatform in ['windows', 'windowsConnectionMgr']:
        if releasePortsWhenDone and forceTakePortOwnership:
            portObj.releasePorts(portList)

        if osPlatform == 'windowsConnectionMgr':
            if deleteSessionAfterTest:
                mainObj.deleteSession()

import sys

import requests 
import json
import time
import os
import datetime

import csv

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

#Test Functions

def startProto():
#from IxNetRestApiProtocol import Protocol
#    protocolObj = Protocol(mainObj)
#    protocolObj.startAllProtocols()
#    protocolObj.verifyArp(ipType='ipv4')
#    protocolObj.verifyProtocolSessionsUp(protocolViewName='BGP Peer Per Port', timeout=120)

    response = requests.post(url + '/ixnetwork/operations/startallprotocols', data=json.dumps({}), headers={'content-type': 'application/json'}, verify=False)
    time.sleep(5)
    response.json()['state']
    return 0

def stopProto():
#from IxNetRestApiProtocol import Protocol
# protocolObj.stopAllProtocols()
    response = requests.post(url + '/ixnetwork/operations/stopallprotocols', data=json.dumps({}), headers={'content-type': 'application/json'}, verify=False)
    time.sleep(5)
    response.json()['state']
    return 0

def startTraffic():
#from IxNetRestApiTraffic import Traffic
#    trafficObj = Traffic(mainObj)
#    trafficObj.startTraffic(regenerateTraffic=True, applyTraffic=True)
    
    requests.post(url + '/ixnetwork/traffic/operations/generate', data=json.dumps({'arg1': url + '/ixnetwork/traffic/1'}), headers={'content-type': 'application/json'}, verify=False)
    response = requests.post(url + '/ixnetwork/traffic/operations/apply', data=json.dumps({'arg1': '/ixnetwork/traffic'}), headers={'content-type': 'application/json'}, verify=False)
    response = requests.post(url + '/ixnetwork/traffic/operations/start', data=json.dumps({'arg1': '/ixnetwork/traffic'}), headers={'content-type': 'application/json'}, verify=False)
    response.json()
    return 0

def stopTraffic():
#from IxNetRestApiTraffic import Traffic
#    trafficObj.stopTraffic()
    response = requests.post(url + '/ixnetwork/traffic/operations/stop', data=json.dumps({'arg1': '/ixnetwork/traffic'}), headers={'content-type': 'application/json'}, verify=False)
    response.json()
    return 0

 
def clearStats():
#from IxNetRestApiStatistics import Statistics
#    statObj = Statistics(mainObj)
#    stats = statObj.clearStats()
    response = requests.post(url + '/ixnetwork/operations/clearstats', headers=jsonHeader, verify=False)
    if response.status_code != 202:
        print('something went wrong')

def getStats(statName):
#    stats = statObj.getStats(viewName='Flow Statistics')    
    #Parse Through list of returned views and then pick the one that matches the caption to be used
    response = requests.get(url + '/ixnetwork/statistics/view', headers=jsonHeader, verify=False)
    for i in response.json():
        if (i['caption']) == 'Traffic Item Statistics':
            viewNum = i['id']
    if viewNum is None:
        print("Error getting response from the API server")
        sys.exit()
    view = ('%s%s%s%s' % (url, '/ixnetwork/statistics/view/', viewNum, '/page'))
    response = requests.get(view, headers=jsonHeader, verify=False)
    return response

def getPackLossDuration():
    view=getStats('Traffic Item Statistics')
    loss_duration_column = view.json()['columnCaptions'].index("Packet Loss Duration (ms)")
    # DEBUG
    #print("DEBUG STATS JSON\n%s" % (view.json()))
    #print("DEBUG LOSS DURATION INDEX\n%d" % (loss_duration_column))
    value_str = view.json()['pageValues'][0][0][loss_duration_column]
    print("Packet loss duration: %s ms" % (value_str))
    if isFloat(value_str):
        value = float(value_str)
    else:
        value = 0.0
    return value

def startProtoAndTraffic():
    stopProto()
    print('Starting protocol and traffic within 5 seconds...')
    startProto()
    time.sleep(5)
    startTraffic()

def stopProtoAndTraffic():
    print('Stopping traffic. Wait...')
    stopTraffic()
    stopProto()
    print('stopped')


# Parse arguments
if len(sys.argv) < 3:
    print("Usage: %s api_host api_session_id [api_tcp_port]" % (sys.argv[0]))
    sys.exit()
    
# Assemble an API URL base
api_host = sys.argv[1]
api_session_id = sys.argv[2]
if len(sys.argv) > 3:
    api_tcp_port = sys.argv[3]
else:
    api_tcp_port = '11009'
    
url = 'http://' + api_host + ':' + api_tcp_port + '/api/v1/sessions/' + api_session_id

data = {'applicationType': 'ixnrest'}
jsonHeader = {'content-type': 'application/json'}

# Initialize counters
test_number = 0
test_scope = ""
test_iterrations_str = ""
test_iterrations = 1
test_iterration = 0

user_input = input("Start traffic? (Anything other than 'y' will kill it) ")
if user_input == "y":
    requests.packages.urllib3.disable_warnings()
    startProtoAndTraffic()
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
                clearStats()
                input("Starting the iteration #%d for FAILURE... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_failure = getPackLossDuration()
                clearStats()
                input("Starting the iteration #%d for RECOVERY... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_recovery = getPackLossDuration()
                testwriter.writerow([test_number, test_scope, test_iterration, loss_duration_failure, loss_duration_recovery])
            user_input = input("Another test? (Anything other than 'y' will kill it) ")
            if user_input != "y":
        	    break

    stopProtoAndTraffic()

print('Exiting...')

