#Python Test to get Packet Loss Duration Statistics
# CLI arguments parsing

# USAGE
# 1. Update "Preference Settings" section below
# 2. Launch with desired traffic generation parameters
#    python <script>.py <frame rate percentage of line rate> <frame size> [api session id]

#---------- Preference Settings --------------
forceTakePortOwnership = True
releasePortsWhenDone = True
enableDebugTracing = False
logFile = False
deleteSessionAfterTest = True ;# For Windows Connection Mgr and Linux API server only

apiServerIp = '10.36.237.142'
apiServerTcpPort = '443'    # Use 443 for linux or 11009 for windows API server
apiServerUsername = 'admin' # Only used for linux API server
apiServerPassword = 'admin' # Only used for linux API server
osPlatform = 'linux'        # linux or windows
licenseServerIp = apiServerIp
licenseModel = 'perpetual'

ixChassisIp = apiServerIp
# [chassisIp, cardNumber, slotNumber]
portList = [[ixChassisIp, '1', '1'], [ixChassisIp, '1', '2']]

#---------- Preference Settings End --------------

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
if len(sys.argv) < 3:
    print("Usage: %s frame_rate_percent frame_size [api_session_id]" % (sys.argv[0]))
    sys.exit()
    
# Assemble an API URL base
frame_rate_percent = float(sys.argv[1])
frame_size  = int(sys.argv[2])
    
if len(sys.argv) > 3:
    api_session_id = sys.argv[3]
else:
    api_session_id = 0 # will create a new session

#Test Functions
 
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

try:
    if osPlatform == 'linux':
        mainObj = Connect(apiServerIp=apiServerIp,
                          serverIpPort=apiServerTcpPort,
                          username=apiServerUsername,
                          password=apiServerPassword,
                          deleteSessionAfterTest=deleteSessionAfterTest,
                          verifySslCert=False,
                          serverOs=osPlatform,
                          generateLogFile=logFile
                          )

    if osPlatform in ['windows', 'windowsConnectionMgr']:
        mainObj = Connect(apiServerIp=apiServerIp,
                          serverIpPort=apiServerTcpPort,
                          serverOs=osPlatform,
                          deleteSessionAfterTest=True,
                          generateLogFile=logFile
                          )
        
    # Only need to blank the config for Windows because osPlatforms such as Linux and
    # Windows Connection Mgr supports multiple sessions and a new session always come up as a blank config.
    if osPlatform == 'windows':
        mainObj.newBlankConfig() 

    mainObj.configLicenseServerDetails([licenseServerIp], licenseModel)

    portObj = PortMgmt(mainObj)
    portObj.assignPorts(portList, forceTakePortOwnership)
    portObj.modifyPortMediaType(portList, 'fiber')

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
                                                                    'frameRate': frame_rate_percent,
                                                                    'frameRateType': 'percentLineRate',
                                                                    'frameSize': frame_size}])
    
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

    print('Stopping traffic. Wait...')
    trafficObj.stopTraffic()
    protocolObj.stopAllProtocols()
    print('stopped')

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



