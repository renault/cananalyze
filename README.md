# Introduction

 The automotive uses some normalized protocols like CAN, ISOTP, UDS, that why Renault & Thales have developed a framework to interact with
 ECU. The following framework makes easy to interact with automotive  ECU. The framework can be used in different scenarios:

* This framework can be used to interact with automotive protocols  like CAN/ISOTP/UDS, if you want to extract/change some ECU configurations.
* This framework can be used to detect if some UDS debug services are  still enabling like the readMemory service. Some UDS services can be used to reprogram the ECU.
* This framework is usefull to test gateway calibration.

# Installation & Configuration

This is a python3 framework. The framework was tested with an ubuntu 18.04 and a Windows 10 Pro (Build 18363) with a Vector driver in version 11.2.20.

## Prerequisite

### Python prerequisite

You need to install some python dependencies:

``` 
pip install -r requirements.txt 
```

### Komodo prerequisite

if you want to use komodo hardwear, you need to download komodo package (v1.40) on Totalphase website (https://www.totalphase.com/)
After downloading and extracting the komodo package, you need to copy "komodo_py.py" and "komodo.so" file inside the cananalyze folder.

## Installation

You can intall the framework with the following commandline
``` 
make install 
```

if you want use the framework without install it, you need to configure the PYTHONPATH variable.
``` 
export PYTHONPATH=__MY_PATH_TO_THE_PROJECT__:__MY_PATH_TO_THE_PROJECT__/cananalyze 
```

# Documentation 

To compile the documentation you need to install the sphinx package
(for us test we have used the version 1.6.7)

````
make doc
````

And open with your browser:

````
docs/build/html/index.html
````

# Tests

The framework comes with a set of unit tests.

````
make test
````


# Examples
## Detecting the UDS CAN ID service
This script can be used when we don't know the UDS CANid, this script tries to start an UDS session for each canid (no extended). The script prints all the CANids(received) that send an UDS answer

````
$ python3 scripts/id_uds.py A komodo
[Thread 95360 - 1582795920.230]km_init_channel: Acquired features: 38
[Thread 95360 - 1582795920.238]km_init_channel: bitrate set to 500000
[Thread 95360 - 1582795920.239]km_init_channel: timeout set to 0 ms
[Thread 95360 - 1582795973.957]Receive id 0x7da data 0x03,0x7f,0x10,0x78,0xff,0xff,0xff,0xff with canid 0x7cc
[Thread 95360 - 1582795975.224]UDS service detected (canid_send=7cc, canid_receive=7da)

````

## Detecting the UDS service
This script detect the UDS services (before executing the script you must change the CANid)
````
$ python3 scripts/nmap.py A komodo 0x7ca 0x7da services
[Thread 83456 - 1554369085.510]km_init_channel: Acquired features: 38
[Thread 83456 - 1554369085.511]km_init_channel: bitrate set to 500000
[Thread 83456 - 1554369085.511]km_init_channel: timeout set to 1 seconds
[Thread 83456 - 1554369093.514]scan.services discovered 10 Diagnostic Session Control
[Thread 83456 - 1554369093.514]scan.services discovered 11 ECU Reset  
[Thread 83456 - 1554369093.514]scan.services discovered 14 Clear Diagnostic Information
[Thread 83456 - 1554369093.515]scan.services discovered 19 Read DTC Information
[Thread 83456 - 1554369093.515]scan.services discovered 22 Read Data By Identifier
[Thread 83456 - 1554369093.515]scan.services discovered 27 Security Access
[Thread 83456 - 1554369093.515]scan.services discovered 2e Write Data By Identifier
[Thread 83456 - 1554369093.515]scan.services discovered 2f unknow
[Thread 83456 - 1554369093.515]scan.services discovered 31 Routine Controle
[Thread 83456 - 1554369093.515]scan.services discovered 3e Tester Present
````

## Virtual gateway
This script load a calibration file that defines the routing and
filtering rules of the gateway, and interface mapping file that
defines the CAN interfaces and the corresponding module.

For a virtual gateway with 7 interfaces using SocketCAN you can use:
````
scripts/data/gw_mapping_test1_vcan.json
````

With a corressponding calibration file:
````
scripts/data/gw_calibration_test1.json
````

To run the virtual gateway just run in a first terminal:
````
$ python3 scripts/gw_virtual_socketcan.py scripts/data/gw_calibration_test1.json scripts/data/gw_mapping_test1_vcan.json
Warning, no calibration rule for interface v1
canread_process: START [physical=pt virtual=vcan0]
canread_process: START [physical=ext virtual=vcan1]
canread_process: START [physical=chassis virtual=vcan3]
canread_process: START [physical=v2 virtual=vcan4]
canread_process: START [physical=ic virtual=vcan5]
canread_process: START [physical=dlc virtual=vcan2]
canwrite_process: START
````

In another terminal you can see the new created interfaces:
````
$ ifconfig|grep vcan
vcan0: flags=193<UP,RUNNING,NOARP>  mtu 72
vcan1: flags=193<UP,RUNNING,NOARP>  mtu 72
vcan2: flags=193<UP,RUNNING,NOARP>  mtu 72
vcan3: flags=193<UP,RUNNING,NOARP>  mtu 72
vcan4: flags=193<UP,RUNNING,NOARP>  mtu 72
vcan5: flags=193<UP,RUNNING,NOARP>  mtu 72
````

And then use can-utils commands to play with the gateway:
````
$ cangen vcan0
$ cangen vcan1
$ cangen vcan5
````

In the gateway terminal:
````
R: pt [0x1aa - 0xb'4a0940108f4fb84e']
R: pt [0x21a - 0xb'729d6602f31e013f']
R: pt [0x10f - 0xb'efe69a4530e91d41']
R: pt [0x486 - 0xb'52c401']
R: pt [0x28c - 0xb'e856ac0ae3bef032']
R: pt [0x761 - 0xb'bf798f0c93']
R: pt [0x189 - 0xb'd73918657d2a4d7a']
R: ext [0x58d - 0xb'3a10']
R: ext [0x382 - 0xb'ce1fba210f3a7517']
R: ic [0x0e0 - 0xb'3627506f3cfbfd18']
  R: CAN ID matches = 0x0e0
    F: ic -> dlc [0x0e0 - 0xb'3627506f3cfbfd18']
R: v2 [0x238 - 0xb'11776c1637007458']
R: ic [0x167 - 0xb'1c606e5cc986']
R: v2 [0x3d5 - 0xb'a5018b34f3']
R: ic [0x6d6 - 0xb'd04d055042317e1a']
````

# Documentation

To compile the documentation you need to install the sphinx package
(for us test we have used the version 1.6.7)

````
pip install termcolor
make doc
````

And open with your browser:

````
docs/build/html/index.html
````

# Tests

The framework comes with a set of unit tests.
````
make test
````

