#Python Test to get Packet Loss Duration Statistics
# CLI arguments parsing

# USAGE
#    python <script>.py windows
#    python <script>.py linux

import sys, os, traceback
import json
import time, datetime
import csv

import requests
requests.packages.urllib3.disable_warnings()

from libixnscripts import *

sys.path.insert(0, (os.path.dirname(os.path.abspath(__file__).replace('ixnscripts', 'IxNetwork/RestApi/Python/Modules'))))
from IxNetRestApi import *
from IxNetRestApiPortMgmt import PortMgmt
from IxNetRestApiTraffic import Traffic
from IxNetRestApiProtocol import Protocol
from IxNetRestApiStatistics import Statistics

# Parse arguments
if len(sys.argv) < 4:
    print("Usage: %s api_host api_session_id api_tcp_port [api_platform]" % (sys.argv[0]))
    sys.exit()
    
# Assemble an API URL base
api_host = sys.argv[1]
api_session_id = sys.argv[2]
api_tcp_port = sys.argv[3]
    
url = 'http://' + api_host + ':' + api_tcp_port + '/api/v1/sessions/' + api_session_id
data = {'applicationType': 'ixnrest'}
jsonHeader = {'content-type': 'application/json'}

# Default the API server to either windows, windowsConnectionMgr or linux.
osPlatform = 'windows'

if len(sys.argv) > 4:
    if sys.argv[4] not in ['windows', 'windowsConnectionMgr', 'linux']:
        sys.exit("\nError: %s is not a known option. Choices are 'windows', 'windowsConnectionMgr or 'linux'." % sys.argv[4])
    osPlatform = sys.argv[4]

#Test Functions

def stopProto():
#from IxNetRestApiProtocol import Protocol
# protocolObj.stopAllProtocols()
    response = requests.post(url + '/ixnetwork/operations/stopallprotocols', data=json.dumps({}), headers={'content-type': 'application/json'}, verify=False)
    time.sleep(5)
    response.json()['state']
    return 0

def stopTraffic():
#from IxNetRestApiTraffic import Traffic
#    trafficObj.stopTraffic()
    response = requests.post(url + '/ixnetwork/traffic/operations/stop', data=json.dumps({'arg1': '/ixnetwork/traffic'}), headers={'content-type': 'application/json'}, verify=False)
    response.json()
    return 0

 
def getPackLossDuration():
    stats = statObj.getStats(viewName='Traffic Item Statistics')
    # DEBUG
    #print("DEBUG STATS JSON\n%s" % (stats))
    value_str = stats[1]["Packet Loss Duration (ms)"]
    print("Packet loss duration: %s ms" % (value_str))
    if isFloat(value_str):
        value = float(value_str)
    else:
        value = 0.0
    return value

def stopProtoAndTraffic():
    print('Stopping traffic. Wait...')
    stopTraffic()
    stopProto()
    print('stopped')

# Parse arguments
if len(sys.argv) < 4:
    print("Usage: %s api_host api_session_id api_tcp_port [api_platform]" % (sys.argv[0]))
    sys.exit()


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
        mainObj = Connect(apiServerIp=api_host,
                          serverIpPort=api_tcp_port,
                          username='admin',
                          password='admin',
                          deleteSessionAfterTest=deleteSessionAfterTest,
                          verifySslCert=False,
                          serverOs=osPlatform,
                          generateLogFile='ixiaDebug.log'
                          )

    if osPlatform in ['windows', 'windowsConnectionMgr']:
        mainObj = Connect(apiServerIp=api_host,
                          serverIpPort=api_tcp_port,
                          serverOs=osPlatform,
                          deleteSessionAfterTest=True,
                          generateLogFile='ixiaDebug.log'
                          )
        
    #---------- Preference Settings End --------------
    # Only need to blank the config for Windows because osPlatforms such as Linux and
    # Windows Connection Mgr supports multiple sessions and a new session always come up as a blank config.
    if osPlatform == 'windows':
        mainObj.newBlankConfig() 

    mainObj.configLicenseServerDetails([licenseServerIp], licenseModel)

    portObj = PortMgmt(mainObj)
    portObj.assignPorts(portList, forceTakePortOwnership)

    protocolObj = Protocol(mainObj)
    topologyObj1 = protocolObj.createTopologyNgpf(portList=[portList[0]],
                                              topologyName='Topo1')

    deviceGroupObj1 = protocolObj.createDeviceGroupNgpf(topologyObj1,
                                                    multiplier=1,
                                                    deviceGroupName='DG1')

    topologyObj2 = protocolObj.createTopologyNgpf(portList=[portList[1]],
                                              topologyName='Topo2')

    deviceGroupObj2 = protocolObj.createDeviceGroupNgpf(topologyObj2,
                                                    multiplier=1,
                                                    deviceGroupName='DG2')

    ethernetObj1 = protocolObj.configEthernetNgpf(deviceGroupObj1,
                                                  ethernetName='MyEth1',
                                                  macAddress={'start': '00:01:01:00:00:01',
                                                              'direction': 'increment',
                                                              'step': '00:00:00:00:00:01'},
                                                  macAddressPortStep='disabled',
                                                  vlanId={'start': 103,
                                                          'direction': 'increment',
                                                          'step':0})

    ethernetObj2 = protocolObj.configEthernetNgpf(deviceGroupObj2,
                                                  ethernetName='MyEth2',
                                                  macAddress={'start': '00:01:02:00:00:01',
                                                              'direction': 'increment',
                                                              'step': '00:00:00:00:00:01'},
                                                  macAddressPortStep='disabled',
                                                  vlanId={'start': 103,
                                                          'direction': 'increment',
                                                          'step':0})
    ipv4Obj1 = protocolObj.configIpv4Ngpf(ethernetObj1,
                                          ipv4Address={'start': '1.1.1.1',
                                                       'direction': 'increment',
                                                       'step': '0.0.0.1'},
                                          ipv4AddressPortStep='disabled',
                                          gateway={'start': '1.1.1.2',
                                                   'direction': 'increment',
                                                   'step': '0.0.0.0'},
                                          gatewayPortStep='disabled',
                                          prefix=24,
                                          resolveGateway=True)

    ipv4Obj2 = protocolObj.configIpv4Ngpf(ethernetObj2,
                                          ipv4Address={'start': '1.1.1.2',
                                                       'direction': 'increment',
                                                       'step': '0.0.0.1'},
                                          ipv4AddressPortStep='disabled',
                                          gateway={'start': '1.1.1.1',
                                                   'direction': 'increment',
                                                   'step': '0.0.0.0'},
                                          gatewayPortStep='disabled',
                                          prefix=24,
                                          resolveGateway=True)

    protocolObj.startAllProtocols()
    protocolObj.verifyProtocolSessionsUp()

    # For all parameter options, please go to the API configTrafficItem
    # mode = create or modify
    trafficObj = Traffic(mainObj)
    trafficStatus = trafficObj.configTrafficItem(mode='create',
                                                 trafficItem = {
                                                     'name':'Topo1 to Topo2',
                                                     'trafficType':'ipv4',
                                                     'biDirectional':True,
                                                     'srcDestMesh':'one-to-one',
                                                     'routeMesh':'oneToOne',
                                                     'allowSelfDestined':False,
                                                     'trackBy': ['flowGroup0', 'vlanVlanId0']},
                                                 endpoints = [{'name':'Flow-Group-1',
                                                                'sources': [topologyObj1],
                                                                'destinations': [topologyObj2]
                                                           }],
                                                 configElements = [{'transmissionType': 'continuous',
                                                                    'frameRate': 0.25,
                                                                    'frameRateType': 'percentLineRate',
                                                                    'frameSize': 512}])
    
    trafficItemObj   = trafficStatus[0]
    endpointObj      = trafficStatus[1][0]
    configElementObj = trafficStatus[2][0]
    
    # Enable tracking of packet loss duration
    trafficObj.enablePacketLossDuration()

    # Start traffic
    trafficObj.startTraffic(regenerateTraffic=True, applyTraffic=True)


    # Check the traffic state before getting stats.
    #    Use one of the below APIs based on what you expect the traffic state should be before calling stats.
    #    If you expect traffic to be stopped such as in fixedFrameCount and fixedDuration
    #    or do you expect traffic to be started such as in continuous mode
    #trafficObj.checkTrafficState(expectedState=['stopped'], timeout=45)
    trafficObj.checkTrafficState(expectedState=['started'], timeout=45)

    statObj = Statistics(mainObj)

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
                statObj.clearStats()
                input("Starting the iteration #%d for FAILURE... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_failure = getPackLossDuration()
                statObj.clearStats()
                input("Starting the iteration #%d for RECOVERY... press Enter when convergence is expected to be complete..." % (test_iterration))
                loss_duration_recovery = getPackLossDuration()
                testwriter.writerow([test_number, test_scope, test_iterration, loss_duration_failure, loss_duration_recovery])
            user_input = input("Another test? (Anything other than 'y' will kill it) ")
            if user_input != "y":
        	    break

    stopProtoAndTraffic()

    if releasePortsWhenDone == True:
        portObj.releasePorts(portList)

    if osPlatform == 'linux':
        mainObj.linuxServerStopAndDeleteSession()

    if osPlatform == 'windowsConnectionMgr':
        mainObj.deleteSession()

    print('Exiting...')

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



