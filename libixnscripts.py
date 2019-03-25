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
