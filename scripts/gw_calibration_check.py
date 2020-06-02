#!/usr/bin/env python3
'''
Gateway calibration check

Command line tool to manually check a CAN message sent to a Gateway.
The tool takes as argument a calibration file.

Warning: code not hardened for invalid inputs
'''

import os
import sys
import json
import can

import scripts.gw_calibration_tools as cal

if __name__ == "__main__":

    # Load the input data file
    if len(sys.argv) != 2:
        print("missing data input parameters (JSON files)")
        print("usage : {} cal.json".format(sys.argv[0]))
        print("    cal.json is the gateway calibration profil in JSON format")
        sys.exit(1)

    # Load the calibration file and the mapping interfaces
    with open(sys.argv[1]) as f:
        calibration = json.load(f)

    while True:
        rx = input("RX interface (input CAN interface) ? ")
        tx = input("TX interface (output CAN interface) ? ")

        canid = input("CAN ID (hexadecimal value without 0x) ? ")
        canid = int(canid, 16)

        payload = input("payload (hexadecimal value without 0x) ? ")
        payload = [int(payload[i:i+2],16) for i in range(0, len(payload), 2)]

        if cal.calibration_matches(calibration, rx, tx, canid, payload):
            print("-> OK")
        else:
            print("-> NOK")
        print()
