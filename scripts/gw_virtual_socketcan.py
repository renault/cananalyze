#!/usr/bin/env python3
'''
This script simulate a gateway using virtual CAN interfaces.

This script load a calibration file that defines the routing and
filtering rules of the gateway, and interface mapping file that
defines the CAN interfaces and the corresponding module.

Press CTRL+C to stop the gateway.
'''

import os
import sys
import time
import multiprocessing as mp
import signal
import json
import queue
import codecs
import can
from termcolor import colored
import argparse

import cananalyze.abstract_can as vcan
import cananalyze.context as context
from cananalyze.context import BusType
import scripts.gw_calibration_tools as cal


CACHE_TIMEOUT = 0.05
verbose = False
end_process = mp.Value('i', False)
pids = []

#cangen_cmd  = 'sleep 10 && cangen -n 10 %s' % intf

# Manager
mng = mp.Manager()

# Queue for messages received from an interface x to forward to other interfaces
forward_queue = mng.Queue()

# List of messages written after a forward
write_cache = mng.list()


def _signal_handler(sig, frame):
    print("Please wait, stopping gateway")
    end_process.value = True
    time.sleep(5)

# Read process of CAN
def _canread_process(intf, intfs, calibration, end_process):
    intf_phy  = intf
    intf_virt = intfs[intf]['channel']

    print("canread_process: START [physical={} virtual={}]".format(intf_phy, intf_virt))

    # Create the read context
    try:
        ctx_read = context.create_ctx (channel = intf_virt,
                                       bustype = BusType.SOCKETCAN,
                                       bitrate = intfs[intf]['bitrate'],
                                       canid_recv = 0,
                                       canid_send = 0,
                                       timeout = 2,
                                       trace = 0)
    except:
        print("Error creating context on interface {}".format(intf_virt))
        return

    while not end_process.value:
        ret, msg = vcan.read (ctx_read)
        if msg is not None:
            canid = msg.arbitration_id

            if len(msg.data) == 0:
                print("R: {} [0x{:03x} - empty]".format(intf_phy, msg.arbitration_id))
                continue

            # Check if GW write the same message on the same interface recently
            found = False
            for e in write_cache:
                # Clean very old cache
                try:
                    if e['time'] > msg.timestamp + CACHE_TIMEOUT:
                        write_cache.remove(e)
                    elif e['msg']['intf'] == intf_phy and \
                         e['msg']['canid'] == msg.arbitration_id and \
                         e['msg']['data'] == msg.data:
                        found = True
                        write_cache.remove(e)
                        break
                except ValueError:
                    break

            if found:
                if verbose:
                    print("R: {} [0x{:03x} - 0x{}] (from GW)".format(intf_phy, msg.arbitration_id,
                                                                     codecs.encode(msg.data, 'hex')))
                continue

            print("R: {} [0x{:03x} - 0x{}]".format(intf_phy, msg.arbitration_id,
                                                       codecs.encode(msg.data, 'hex')))
            # for each output interface
            for k, v in intfs.items():

                # Ignore the same interface
                if k == intf_phy:
                    continue

                # Check rules
                if cal.calibration_matches(calibration,
                                           intf_phy, k,
                                           msg.arbitration_id,
                                           list(msg.data)):
                    out = "    F: {} -> {} [0x{:03x} - 0x{}]".format(intf_phy,
                                                                     k,
                                                                     msg.arbitration_id,
                                                                     codecs.encode(msg.data, 'hex'))
                    print(colored(out, 'green'))
                    forward_queue.put({'intf': k, 'canid': msg.arbitration_id, 'data': msg.data})


# write process of CAN
def _canwrite_process(intfs, calibration, end_process):
    print("canwrite_process: START")

    for k, v in intfs.items():
        try:
            v['ctx']  = context.create_ctx (channel = v['channel'],
                                            bustype = BusType.SOCKETCAN,
                                            bitrate = v['bitrate'],
                                            canid_recv = 0,
                                            canid_send = 0,
                                            timeout = None,
                                            trace = 0)
        except:
            print("Error creating context on interface {}".format(v['channel']))

    while not end_process.value:
        try:
            e = forward_queue.get(timeout=2)
        except queue.Empty:
            pass
        except EOFError:
            return
        else:
            i = e['intf']
            if i in intfs:
                # Memorize message that will be written
                ecache = {
                    'msg'  : e,
                    'time' : time.time ()
                }
                write_cache.append(ecache)

                msg = can.Message(data = e['data'])
                out = "W: {} [0x{:03x} - {}]".format(i, e['canid'],
                                                     codecs.encode(msg.data, 'hex'))
                print(colored(out, 'green'))

                vcan.write(intfs[i]['ctx'], msg, can_id=e['canid'])
            else:
                print("Warning interface {} doesn't exist".format(i))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _signal_handler)

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("calibration", help="JSON calibration file")
    parser.add_argument("interfaces", help="JSON interfaces mapping file")
    parser.add_argument("--verbose", help="Verbose messages")

    args = parser.parse_args()

    # Load the input data file
    # Load the calibration file and the mapping interfaces
    with open(args.interfaces) as f:
        interfaces = json.load(f)
    with open(args.calibration) as f:
        calibration= json.load(f)

    # Optional arguments
    if args.verbose:
        verbose = True

    if cal.verify_mapping(interfaces) == False or cal.initialize_mapping(interfaces) == False:
        print("Error with mapping file")
        sys.exit(1)

    # Create a read thread for each vcan
    for k, v in interfaces['interfaces'].items():
        if k in calibration:
            p = mp.Process(target=_canread_process, args=(k, interfaces['interfaces'],
                                                          calibration, end_process, ))
            p.start()
            pids += [p]
        else:
            print("Warning, no calibration rule for interface " + k)

    # Launch the write process
    p = mp.Process(target=_canwrite_process, args=(interfaces['interfaces'], calibration, end_process, ))
    p.start()
    pids += [p]

    signal.pause()
    for p in pids:
        p.join()
