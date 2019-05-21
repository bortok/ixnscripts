# RestPy-based IxNetwork automation scripts
## Overview
These scripts are based on RestPy framework, which is the most up-to-date for Ixia IxNetwork.

## Installation
Prerequisites:

* Python 3
* PIP
* virtualenv - optional, used in the examples here

### Linux or OS X

Create virtual environment called `ixnetwork` in a directory of your choice:

    export PYENV=ixnetwork
    virtualenv -p python3 $PYENV; cd $PYENV; export PYENV_DIR=`pwd`
    source "$PYENV_DIR/bin/activate"

Clone `ixnscripts` repository

    git clone https://github.com/bortok/ixnscripts.git

Install pre-requisite packages:

    pip install -r ixnscripts/requirements.txt

### Windows
Verify installed Python version, should be 3.+. Open a command prompt and run the following command:
   
    python -V

If you don't have Python 3 installed, download and install it from [https://www.python.org/downloads/](https://www.python.org/downloads/)

Download [`get-pip.py`](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer. Open a command prompt and navigate to the folder containing `get-pip.py`. Run the following command:

    python get-pip.py

Verify installed PIP version, should be 18+

    pip -V

Download and extract a ZIP archive with [`ixnscripts`](https://github.com/bortok/ixnscripts/archive/master.zip) repository. Open a command prompt and navigate to the folder `ixnscripts-master`.

Install pre-requisite packages:

    pip install -r requirements.txt


## Configuration

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
