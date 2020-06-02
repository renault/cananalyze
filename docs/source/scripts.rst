Scripts
=======

Advanced scripts and tools to user CANanalyze.


Setup CANUSB interface
----------------------

Basic shell script to setup userspace daemon for serial line CAN interface driver SLCAN.

Set a slcanx interface from a ttyUSBxx interface.

.. code-block:: console

        scripts/setup_canusb_slcan.sh ttyUSB0 vcan0


Detecting the UDS service CANid
-------------------------------

.. automodule:: scripts.id_uds

.. code-block:: console

        $ python3 scripts/id_uds.py A komodo
        [Thread 28608 - 1554369033.697]km_init_channel: Acquired features: 38
        [Thread 28608 - 1554369033.698]km_init_channel: bitrate set to 500000
        [Thread 28608 - 1554369033.698]km_init_channel: timeout set to 1 seconds
        [Thread 37056 - 1554369035.801]Receive id 0x7da data 0x03,0x7f,0x10,0x78,0xff,0xff,0xff,0xff
        [Thread 95360 - 1582795920.230]km_init_channel: Acquired features: 38
        [Thread 95360 - 1582795920.238]km_init_channel: bitrate set to 500000
        [Thread 95360 - 1582795920.239]km_init_channel: timeout set to 0 ms
        [Thread 95360 - 1582795973.957]Receive id 0x7da data 0x03,0x7f,0x10,0x78,0xff,0xff,0xff,0xff with canid 0x7cc
        [Thread 95360 - 1582795975.224]UDS service detected (canid_send=7ca, canid_receive=7da)

Detecting the UDS services
--------------------------

.. automodule:: scripts.nmap

.. code-block:: console

        $ python3 scripts/nmap.py A komodo
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

Dump CAN messages
-----------------

.. automodule:: scripts.can_sniff

.. code-block:: console

	$ python3 scripts/can_sniff.py vcan0 socketcan
	Ox1f0#0x94,0x05,0x6a,0x2a,0x40,0xc0,0xc9,0x25
	Ox1f0#0x63,0x7f,0x80,0x1b,0xc7,0xf8,0x00,0x11
	Ox1a9#0xd1,0xaa,0xeb,0x0b
	Ox183#0xdc,0x6b,0x5b,0x13,0xe0,0x21,0xe6
	Ox208#0x5e,0x1b,0x21,0x2d,0xe0
	Ox125#0xbf,0x51
	Ox2f2#0xf7,0xb4,0xb9,0x2d,0xfc,0xf2,0xbe,0x53
	Ox45b#0xbf,0x13,0x10,0x56,0x4c,0xc6,0xd6
	Ox315#0x8c,0x86,0xa0
	Ox583#0xcc,0xcd,0x30,0x33,0x2c,0x27,0x34,0x7e
	Ox2e3#0x67,0x84,0x01,0x07,0x66,0x7c,0xed,0x46
	Ox145#0x47,0x9e,0xd3
	Ox48#0x2d,0x2a,0xbf,0x5b,0x6e

Dump ISOTP messages
-------------------

.. automodule:: scripts.isotp_read

.. code-block:: console

	$ python3 scripts/isotp_read.py vcan0 socketcan

Calibration check
-----------------

.. automodule:: scripts.gw_calibration_check

.. code-block:: console

		$ python3 scripts/gw_calibration_check.py scripts/data/gw_calibration_test1.json
		RX interface (input CAN interface) ? ext
		TX interface (output CAN interface) ? dlc
		CAN ID (hexadecimal value) ? 0x20
		payload (hexadecimal value) ? 0x202010
		-> NOK

Gateway simulation
------------------

.. automodule:: scripts.gw_virtual_socketcan

.. code-block:: console

		$ python3 scripts/gw_virtual_socketcan.py scripts/data/gw_calibration_test1.json scripts/data/gw_mapping_test1_vcan.json
		Warning, no calibration rule for interface v1
		canread_process: START [physical=pt virtual=vcan0]
		canread_process: START [physical=ext virtual=vcan1]
		canread_process: START [physical=v2 virtual=vcan4]
		canread_process: START [physical=chassis virtual=vcan3]
		canread_process: START [physical=ic virtual=vcan5]
		canread_process: START [physical=dlc virtual=vcan2]
		canwrite_process: START
		R: pt [0x302 - 0xb'55']
		R: ic [0x53e - 0xb'658d8c334e1fed40']
		R: v2 [0x0f7 - 0xb'83ccd7135e450862']
		R: pt [0x30d - 0xb'']
		R: msg ignored data empty
		R: ic [0x6c6 - 0xb'48c7b777775ee421']
		R: v2 [0x427 - 0xb'b06c']
		R: pt [0x7ed - 0xb'']
		R: msg ignored data empty
		R: ic [0x4d5 - 0xb'9ba5270c']
		R: v2 [0x33f - 0xb'1a231429']
		R: pt [0x361 - 0xb'5648907643108751']
		R: ic [0x27a - 0xb'dc705d1a84a0f201']
		R: v2 [0x5e9 - 0xb'']
		R: msg ignored data empty
		R: pt [0x12e - 0xb'd2e9940d9a79']
		R: ic [0x290 - 0xb'8e74']
		R: v2 [0x32e - 0xb'2be1944df5']
		R: pt [0x25a - 0xb'']
		R: msg ignored data empty
		R: ic [0x33a - 0xb'148004643d861a1c']
		R: v2 [0x026 - 0xb'9e8cb01f866d82']
		R: pt [0x269 - 0xb'65c7']
		R: ic [0x6dd - 0xb'29d7bf0e0720']
		R: v2 [0x4c9 - 0xb'0cecae6a52fb4560']
		R: pt [0x3a8 - 0xb'cc3c4b19aa36a534']
		R: ic [0x34a - 0xb'1e1a7e2d89483a5a']
		R: v2 [0x648 - 0xb'b356f60b3f87f04b']
		R: pt [0x0cd - 0xb'a0']
		R: ic [0x768 - 0xb'd767271b']
		R: v2 [0x474 - 0xb'9dccf82d9bb8']
		R: pt [0x4f1 - 0xb'9c6ae16bdedca478']
		^CPlease wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway
		Please wait, stopping gateway

Gateway validation
------------------

.. automodule:: scripts.gw_validate

.. code-block:: console

		$ python3 scripts/gw_validate.py scripts/data/gw_calibration_test1.json scripts/data/gw_mapping_test1_vcan.json
