#---------- Preference Settings --------------
forceTakePortOwnership = True
releasePortsWhenDone = False
# Console output verbosity: 'none'|'request'|'request_response'
debugMode = 'none'
logFile = 'restpy.log'


apiServerUsername = 'admin' # Only used for linux API server
apiServerPassword = 'admin' # Only used for linux API server

ixChassisIp = '10.36.237.196'
# [chassisIp, cardNumber, slotNumber]
portList = [[ixChassisIp, '5', '9'], [ixChassisIp, '5', '10']]
portMediaType = 'fiber' # copper, fiber or SGMII


# The IP address for your Ixia license server(s) in a list.
licenseServerIp = ['10.36.237.196']
# subscription, perpetual or mixed
licenseMode = 'perpetual'
# tier1, tier2, tier3, tier3-10g
licenseTier = 'tier3'

#---------- Preference Settings End --------------
