#!/usr/bin/env python3
'''
Gateway validation script.

This script load a calibration file that defines the routing and
filtering rules of the gateway, and interface mapping file that
defines the CAN interfaces and the corresponding module.

The script will run different tests:

 - Send UDS DiagnosticSessionControl message on CAN ids from 0x000 to OxFFF, to each gateway interface
 - Check on other interfaces if a message is received
 - Check the conformity with the gateway calibration
 - Replay all CAN ids and payloads from calibration file
 - Check if filtering and routing is fine, if gateway does not accept something wrong
 - ...

'''

import os
import sys
import time
import multiprocessing
import ctypes
import netifaces
import signal
import json
import queue
import codecs
from termcolor import colored
import can
from copy import deepcopy
import argparse

import cananalyze.abstract_can as vcan
import cananalyze.uds as uds
import cananalyze.context as context
import scripts.gw_calibration_tools as cal
from array import array, ArrayType

pids = []
canid_range = 0x7ff
runtests = ["test1", "test3"]


def _signal_handler(sig, frame):
    print("Please wait, stopping gateway validation script")
    end_validation.value = True
    time.sleep(5)

# Analyze the result
def _analyze_result(intf_in, gctx_op, gctx_data):
    for k2, _ in gctx_op.items():
        # For all read interfaces
        if k2 != intf_in:
            # If something has been received
            if len(gctx_data[k2]) > 0:
                if cal.calibration_matches(calibration, intf_in, k2, gctx_data[k2][0], gctx_data[k2][1:]):
                    print("{} R: {} -> {} [0x{:03x} - 0x{}]".format(
                        colored('[OK]', 'green'),
                                 intf_in, k2,
                        gctx_data[k2][0],
                        codecs.encode(bytearray(gctx_data[k2][1:]), 'hex')))

                else:
                    print("{} R: {} -> {} [0x{:03x} - 0x{}]".format(
                        colored('[ERROR]', 'red'),
                        intf_in, k2,
                        gctx_data[k2][0],
                        codecs.encode(bytearray(gctx_data[k2][1:]), 'hex')))

                sys.stdout.flush()
                gctx_data[k2] = []
    gctx_data[intf_in] = []


# First test
# - Send UDS DiagnosticSessionControl message on CAN ids from 0x000 to Ox7FF, to each gateway interface
# - Check on other interfaces if a message is received
# - Check the conformity with the gateway calibration
def _gw_test1(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata, gcanid):
    print("_monitor_process: TEST #1 : CAN ID FILTERING (UDS DiagnosticSessionControl) START")
    for int_send, _ in intfs.items():

        # Ignore interfaces without calibration
        if not int_send in calibration:
            print("Warning, no calibration rule for interface " + int_send)
            continue

        # Init global context
        for interface, _ in gctx_op.items():
            if interface == int_send:
                gctx_op[interface] = True
            else:
                gctx_op[interface] = False

        print("_monitor_process: TEST #1 running : {}".format(int_send))
        for canid in range(canid_range):
            if end_validation.value: # exit test
                return
            
            gctx_data[int_send] = [canid, 0x02, 0x10, 0x01]
            gdata[0] = [0x02, 0x10, 0x01]
            # Wait for synch for updated context, start operation
            sync.wait()

            # Wait for synch for end operation
            sync.wait()

            # Add canid to gcanid for filtering payload test (to save canid not filtered)
            for int_receive, _ in gctx_op.items():
                if int_receive != int_send:
                    if len(gctx_data[int_receive]) > 0 and not(int_receive in gcanid[int_send].keys()):
                        if cal.calibration_matches(calibration,int_send,int_receive, canid, gdata[0]):
                            gcanid[int_send][int_receive] = canid
                            print("_monitor_process: TEST #1  add gcanid[%s][%s] = %02x" %
                                  (int_send,int_receive, canid))
            
            # Analyze the result
            _analyze_result(int_send, gctx_op, gctx_data)
    
    print("_monitor_process: TEST #1 : CAN ID FILTERING (UDS DiagnosticSessionControl) END")


# Second test
# Replay all CAN ids and payloads from calibration file
# Check if filtering and routing is fine => if gateway does not accept something wrong
def _gw_test2(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata):
    print("_monitor_process: TEST #2 : CAN ID FILTERING (calibration file) START")
    for int_send, _  in intfs.items():
        print("_monitor_process: TEST #2 running : {}".format(k1))

        # Init global context
        for interface, _ in gctx_op.items():
            if interface == int_send:
                gctx_op[interface] = True
            else:
                gctx_op[interface] = False

        # For each output interface in calibration
        for interface, _ in calibration[int_send].items():
            # For each CAN id
            for cid, e in calibration[int_send][interface].items():
                # for each payload / mask
                for pm in calibration[int_send][interface][cid]:
                    if end_validation.value: # exit test
                        return
                    if len(pm['payload']) > 3:
                        d = list(bytearray.fromhex(pm['payload'][2:]))
                        gctx_data[int_send] = [int(cid, 16)] + d
                    else:
                        gctx_data[int_send] = [int(cid, 16),  0x00]

                    # Wait for synch for updated context, start operation
                    sync.wait()

                    # Wait for synch for end operation
                    sync.wait()

                    # Analyze the result
                    _analyze_result(int_send, gctx_op, gctx_data)

    print("_monitor_process: TEST #2 : CAN ID FILTERING (calibration file) END")


def _gw_test3(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata, gcanid):
    print("_monitor_process: TEST #3 : CAN ID PAYLOAD FILTERING START")

    for int_send, _ in intfs.items():
        for interface, _ in gctx_op.items():
            if interface == int_send:
                gctx_op[interface] = True
            else:
                gctx_op[interface] = False

        for int_receive, _ in gctx_op.items():
            if int_receive == int_send:
                continue

            canid = 0
            if not(int_receive in gcanid [int_send].keys()):
                continue
            else:
                canid = gcanid[int_send][int_receive]
            print("_monitor_process: TEST #3 running : Send {} to {} with canid {}".format(int_send, int_receive, canid))
            for udsFunction in [0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x24, 0x27, 0x28, 0x2A, 0x2C, 0x2E, 0x2F, 0x31, 0x34, 0x35, 0x36, 0x37,0x38, 0x3D, 0x3E, 0x83, 0x84, 0x85, 0x86, 0x87]:
                for udsSubFunction in range(0, 0xFF):
                    if end_validation.value: # exit test
                        return

                    gdata[0] = [0x02, udsFunction, udsSubFunction]
                    gctx_data[int_send] = [canid, 0x02, udsFunction, udsSubFunction]

                    # Wait for synch for updated context, start operation
                    sync.wait()

                    # Wait for synch for end operation
                    sync.wait()

                    # Analyze the result
                    _analyze_result(int_send, gctx_op, gctx_data)

        print("_monitor_process: TEST #3 : CAN ID PAYLOAD FILTERING END")


# Process monitor tests
def _monitor_process(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata, gcan_id):
    print("monitor_process: START")

    # Wait for synch processes started
    sync.wait()

    if "test1" in runtests:
        _gw_test1(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata, gcan_id)

    if "test3" in runtests:
        _gw_test3(intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata, gcan_id)

    end_validation.value = True
    # To unblock processes to detect end
    sync.wait()
    sync.wait()

    print("monitor_process: END")


# Process of CAN
def _can_process(intf, intfs, calibration, end_validation, sync, gctx_op, gctx_data, gdata):
    intf_phy  = intf
    intf_virt = intfs[intf]['channel']

    print("can_process: START [physical={} virtual={}]".format(intf_phy, intf_virt))

    # Create the read/write context
    ctx = context.create_ctx (channel = intf_virt,
                                  port_nr = intfs[intf]['port_nr'],
                                  bustype = intfs[intf]['bustype'],
                                  bitrate = intfs[intf]['bitrate'],
                                  canid_recv = 0,
                                  canid_send = 0,
                                  timeout = 0.010,
                                  trace = 0)
    if ctx == None:
        print("Error creating context on interface {}".format(intf_virt))
        return

    # Wait for synch processes started
    sync.wait()

    while not end_validation.value:
        # Wait for synch for updated context, before operation
        sync.wait()
        dataReceived = gdata[0].copy()
        if gctx_op[intf] and len(gctx_data[intf]) > 0:
            data = list(gctx_data[intf])
        
            ctx.set_canid_send(data[0])
            msg = can.Message(data=data[1:], arbitration_id=data[0], dlc=len(data[1:]))
            vcan.write (ctx, msg)
        else:
            for i in range(2):
                ret, msg = vcan.read (ctx)
                if msg is not None  and msg.dlc >= len(dataReceived):
                    size = len(dataReceived)
                    match = True
                    
                    for i in range(size):
                        if dataReceived[i] != msg.data[i]:
                            match = False
                       
                    if match == True:
                        gctx_data[intf] = [msg.arbitration_id,] + list(msg.data)
                        break
                    else:
                        print("{} R: {} [{}] expected [{}]".format(
                            colored('[WARNING]', 'yellow'),
                            intf,
                            ','.join(hex(x) for x in msg.data),
                            ','.join(hex(x) for x in dataReceived)))

        # Wait for synch for end operation
        sync.wait()

    print("can_process: END [physical={} virtual={}]".format(intf_phy, intf_virt))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _signal_handler)

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("calibration", help="JSON calibration file")
    parser.add_argument("interfaces", help="JSON interfaces mapping file")
    parser.add_argument("--range", help="CANID max range")
    parser.add_argument("--tests", help="List of tests to execute separate with coma (test1,...,testn)")
    args = parser.parse_args()

    # Load the input data file
    # Load the calibration file and the mapping interfaces
    with open(args.interfaces) as f:
        interfaces = json.load(f)
    with open(args.calibration) as f:
        calibration= json.load(f)

    if cal.verify_mapping(interfaces) == False or cal.initialize_mapping(interfaces) == False:
        print("Error with mapping file")
        sys.exit(1)

    # Optional arguments
    if args.range:
        canid_range = int(args.range, 16)
    if args.tests:
        runtests = args.tests.split(',')

    mng = multiprocessing.Manager()
    end_validation = mng.Value('i', False)
    sync = mng.Barrier(len(interfaces['interfaces']) + 1, timeout=None)
    gctx_op = mng.dict()
    gctx_data = mng.dict()
    gdata = mng.dict()
    gcanid = mng.dict()

    for k, v in interfaces['interfaces'].items():
        gcanid[k] = mng.dict()

    # Create a process for each vcan
    for k, v in interfaces['interfaces'].items():
        gctx_op[k] = False
        gctx_data[k] = mng.list()
        p = multiprocessing.Process(target=_can_process, args=(k, interfaces['interfaces'],
                                                               calibration, end_validation, sync,
                                                               gctx_op, gctx_data, gdata))
        p.start()
        time.sleep(2)
        pids += [p]

    # Launch the monitor
    p = multiprocessing.Process(target=_monitor_process, args=(interfaces['interfaces'],
                                                               calibration, end_validation, sync,
                                                               gctx_op, gctx_data, gdata, gcanid ))
    p.start()
    pids += [p]
    for p in pids:
        p.join()
