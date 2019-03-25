#Python Test to get Packet Loss Duration Statistics
# CLI arguments parsing

# USAGE
#    python <script>.py windows
#    python <script>.py linux

import sys, os, traceback
import requests, json
import time, datetime
import csv

from libixnscripts import *

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

