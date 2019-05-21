# RestPy-based IxNetwork automation scripts
## Overview
These scripts are based on RestPy framework, which is the most up-to-date for Ixia IxNetwork.

## Required packages
Prerequisites:

* Python 3
* PIP
* virtualenv - optional, used in the examples here

Verify installed Python version, should be 3.+. Open a command prompt and run the following command:
   
    python -V

Use the steps below to install required components on Windows or Mac OS X. Use appropriate Linux package manager to install Python and PIP.

If you don't have Python 3 installed, download and install it from [https://www.python.org/downloads/](https://www.python.org/downloads/)

Download [`get-pip.py`](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer. Open a command prompt and navigate to the folder containing `get-pip.py`. Run the following command:

    python get-pip.py

Verify installed PIP version.

    pip -V

Install virtualenv:

    pip install virtualenv

## Installation on Linux

Create virtual environment called `ixnetwork` in a directory of your choice:

    export PYENV=ixnetwork
    virtualenv -p python3 $PYENV; cd $PYENV; export PYENV_DIR=`pwd`
    source "$PYENV_DIR/bin/activate"

Clone `ixnscripts` repository

    git clone https://github.com/bortok/ixnscripts.git

Install pre-requisite packages:

    pip install -r ixnscripts/requirements.txt

### Installation on Windows

Create virtual environment called `ixnetwork` in a directory of your choice:

    set PYENV=ixnetwork
    virtualenv -p python %PYENV%
    cd %PYENV%
    Scripts\activate.bat

Download a [ZIP archive](https://github.com/bortok/ixnscripts/archive/master.zip) with `ixnscripts` repository into `ixnetwork` folder and extract it.

Install pre-requisite packages:

    move ixnscripts-master ixnscripts
    pip install -r ixnscripts\requirements.txt


## Configuration
Open `ixn_preferences.py` file in a text editor. Update test chassis information for your IxNetwork environment:

    #---------- Preference Settings --------------
    
    forceTakePortOwnership = True
    releasePortsWhenDone = False
    # Console output verbosity: 'none'|'request'|'request_response'
    debugMode = 'none'
    logFile = 'restpy.log'
    
    apiServerUsername = 'admin' # Only used for linux API server
    apiServerPassword = 'admin' # Only used for linux API server
    
    ixChassisIp = '10.10.10.10'
    # [chassisIp, cardNumber, slotNumber]
    portList = [[ixChassisIp, '1', '1'], [ixChassisIp, '1', '2']]
    portMediaType = 'fiber' # copper, fiber or SGMII
    
    # The IP address for your Ixia license server(s) in a list.
    licenseServerIp = ['10.10.10.10']
    # subscription, perpetual or mixed
    licenseMode = 'perpetual'
    # tier1, tier2, tier3, tier3-10g
    licenseTier = 'tier3'
    
    #---------- Preference Settings End --------------

## Usage

### Packet loss duration logging tool

`PacketLossDuration_RestPy.py` allows you to log packet loss duration measured during failover operations with multiple iterrations. Use arguments to specify IxNetwork API server to connect to and a platform it is running on (linux or windows), plus IxNetwork configuration file to generate traffic.

    cd ixnscripts
    python PacketLossDuration_RestPy.py <api_server_ip> <linux|windows> <ixn_config_file>

For example, to connect to an API server running on Linux-based IxNetwork chassis with an IP address 10.10.10.10 using `ixnscripts_example.ixncfg` traffic configuration:

    python PacketLossDuration_RestPy.py 10.10.10.10 linux ixnscripts_example.ixncfg

# Copyright notice

Author: Alex Bortok (https://github.com/bortok)

COPYRIGHT 2018 - 2019 Keysight Technologies.

This code is provided under the MIT license.  
You can find the complete terms in LICENSE.txt
