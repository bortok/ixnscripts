# IxNetRestApi-based IxNetwork automation scripts
## Overview
These scripts are based on IxNetRestApi framework.

## Installation
Prerequisites:

* Python 3

Create `ixnscripts` directory:

    mkdir ixnscripts; cd ixnscripts

Download https://github.com/OpenIxia/IxNetwork library:

    git clone https://github.com/OpenIxia/IxNetwork.git

Clone ixnscripts repository

    git clone https://github.com/bortok/ixnscripts.git

## Configuration
Put proper IP information for your IxNetwork environment in the following section in the script you are interested in running:

    #---------- Preference Settings --------------
    forceTakePortOwnership = True
    releasePortsWhenDone = False
    enableDebugTracing = False
    logFile = False

    apiServerIp = '10.x.x.x'
    apiServerTcpPort = '443'    # Use 443 for linux or 11009 for windows API server
    #apiServerTcpPort = '11009'    # Use 443 for linux or 11009 for windows API server
    apiServerUsername = 'admin' # Only used for linux API server
    apiServerPassword = 'admin' # Only used for linux API server
    osPlatform = 'linux'        # linux or windows
    #osPlatform = 'windows'        # linux or windows
    licenseServerIp = apiServerIp
    licenseModel = 'perpetual'

    ixChassisIp = '10.y.y.y'
    # [chassisIp, cardNumber, slotNumber]
    portList = [[ixChassisIp, '1', '1'], [ixChassisIp, '1', '2']]
    portMediaType = 'fiber' # copper, fiber or SGMII

    #---------- Preference Settings End --------------


## Usage

### Packet loss duration logging tool

PacketLossDuration_csv.py allows you to log packet loss duration measured during failover operations with multiple iterrations. Use arguments to specify desired traffic rate and frame size. For Linux API server a session can be re-used between multiple script runs to speed up testing. To keep the session open after the script is over, supply `keep` as a `api_session_id` parameter first time you ran it.

    python3 PacketLossDuration_csv.py frame_rate_percent frame_size [api_session_id api_session_key]
    
For example, generate 5% of line rate with 512 bytes frames and keep the API session open:

    python3 PacketLossDuration_csv.py 5 512 keep

# Copyright notice

Author: Alex Bortok (https://github.com/bortok)

COPYRIGHT 2018 - 2019 Keysight Technologies.

This code is provided under the MIT license.  
You can find the complete terms in LICENSE.txt
