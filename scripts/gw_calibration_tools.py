#!/usr/bin/env python3
'''
Gateway calibration check
'''

import os
import sys
import codecs
from array import array, ArrayType

from cananalyze.context import BusType
import tests.tests_tools as tests_tools

def verify_mapping(interfaces):
    for k1, v1 in interfaces['interfaces'].items():
        for k2, v2 in interfaces['interfaces'].items():
            if k1 != k2 and v1['channel'] == v2['channel']:
                print("Mapping file  uses the same channel "+ v1['channel'] + " for the interfaces " + k1 + " and " + k2)
                return False
    return True

def initialize_mapping(interfaces):
    # Initialize the vcans
    for k, v in interfaces['interfaces'].items():
        if v['bustype'] == BusType.SOCKETCAN and not tests_tools.check_context(v['channel']):
            print("Error initializing context with " + v['channel'])
            return False
    return True



"""Check if calibration matches

:param calibration: JSON calibration
:param from_intf: source CAN interface string
:param to_intf: destination CAN interface string
:param canid: CAN id integer
:param msg: CAN massage as a list
:return: Boolean
"""
def calibration_matches(calibration, from_intf, to_intf, canid, msg):
    #print("search calibration received from {} to {} for canid {}".format(from_intf, to_intf, canid))
    if from_intf in calibration:
        #print("  ok found {}".format(from_intf))
        if to_intf in calibration[from_intf]:
            #print("    ok found {}".format(to_intf))
            #print("    search canid {}".format(canid))
            #if id in calibration[from_intf][to_intf]:
            for v in calibration[from_intf][to_intf]:
                if int(v, 16) == canid:
                    #print("      ok found canid {}".format(canid))
                    for e in calibration[from_intf][to_intf][v]:
                        #print(" ==> element {}".format(e))
                        mask = int(e['mask'], 16)
                        payload = int(e['payload'], 16)
                        for n in range(len(msg), 8):
                            msg.append(0)
                        #print(msg)
                        data = int(codecs.encode(bytearray(msg), 'hex'), 16)
                        # Check if it maps
                        #print(data)
                        #print(mask)
                        #print(payload)
                        if (mask & data) == payload:
                            #print("gw_calibration_tool: payload matches")
                            return True
    return False
