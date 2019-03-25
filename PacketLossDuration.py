#Python Test to get Packet Loss Duration Statistics
import requests 
import json
import time
import os
session_url='http://10.219.112.65:11009/api/v1/sessions/1'
root=session_url+'/ixnetwork'
url='http://10.219.112.65:11009/api/v1/'
sessionid = '/1'
data = {'applicationType': 'ixnrest'}
jsonHeader = {'content-type': 'application/json'}

#Test Functions

def startProto():
    response = requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/operations/startallprotocols', data=json.dumps({}), headers={'content-type': 'application/json'})
    time.sleep(5)
    response.json()['state']
    return 0

def stopProto():
    response = requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/operations/stopallprotocols', data=json.dumps({}), headers={'content-type': 'application/json'})
    time.sleep(5)
    response.json()['state']
    return 0

def startTraffic():
    requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic/operations/generate', data=json.dumps({'arg1': 'http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic/1'}), headers={'content-type': 'application/json'})
    response = requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic/operations/apply', data=json.dumps({'arg1': 'http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic'}), headers={'content-type': 'application/json'})
    response = requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic/operations/start', data=json.dumps({'arg1': 'http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic'}), headers={'content-type': 'application/json'})
    response.json()
    return 0

def stopTraffic():
    response = requests.post('http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic/operations/stop', data=json.dumps({'arg1': 'http://10.219.112.65:11009/api/v1/sessions/1/ixnetwork/traffic'}), headers={'content-type': 'application/json'})
    response.json()
    return 0

 
def clearStats():
    response = requests.post(root+'/operations/clearstats', headers=jsonHeader)
    if response.status_code != 202:
        print('something went wrong')

def getStats(statName):
    #Parse Through list of returned views and then pick the one that matches the caption to be used
    response = requests.get(root+'/statistics/view', headers=jsonHeader)
    for i in response.json():
        if (i['caption']) == 'Traffic Item Statistics':
            viewNum = i['id']
    view = ('%s%s%s%s' % (root,'/statistics/view/',viewNum,'/page'))
    response = requests.get(view, headers=jsonHeader)
    return response

def getPackLossDuration():
    view=getStats('Traffic Item Statistics')
    #response = requests.get(view, headers=jsonHeader)
    #column = view.json()['columnCaptions'][5]
    value = view.json()['pageValues'][0][0][5]
    print('Packet Loss Duration Value is:', value, ' ms')

def run():
    os.system('clear')
    print('Starting the iteration...')
    stopProto()
    #time.sleep(3)
    os.system( 'clear' )
    print('Starting protocol and traffic within 5 seconds...')
    startProto()
    time.sleep(5)
    startTraffic()
    os.system('clear')
    input("Initiate failover, and press Enter when your convergence event is expected to be complete...")
    os.system( 'clear' )
    getPackLossDuration()
    print('stopping traffic. Wait...')
    time.sleep(3)
    stopTraffic()
    #stopProto()

while True:
    run()
    user_input = input("Another round? (Anything other than 'y' will kill it) ")
    if user_input != "y":
    	break
print('Exiting...')
stopTraffic()
stopProto()

	