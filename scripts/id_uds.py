#!/usr/bin/env python3
'''
This script detects the UDS CANid, this script tries to start an UDS session for each canid (no extended). The script prints all the CANids(received) sending an UDS answer.
'''

import time
import can
import sys
from cananalyze.tools import *
import cananalyze.abstract_can as vcan
import cananalyze.context as context
import argparse


"""
This script detects the UDS services CANid by sendding an openning session frame 
"""
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="detect the UDS CANid")
    parser.add_argument("channel", help="\"A\", \"B\", \"vcanX\" depending if bustype is komodo or socketcan")
    parser.add_argument("bustype", help="\"komodo\",  \"socketcan\", ... ")
    args = parser.parse_args()

    ctx = context.create_ctx (channel = args.channel,
                              bustype = args.bustype,
                              port_nr = 0,
                              bitrate = 500000,
                              canid_recv = 0x7DA,
                              canid_send = 0x7cA,
                              timeout = 0)

    lcanid = list()

    if ctx == None:
        context.output("Error initialization")
        sys.exit(-1)


    for i in range(0, 0x7ff):
        ctx.set_canid_send(i)
        
        vcan.write (ctx, can.Message(data=[0x02,0x10, 0x01, 0xff, 0xff, 0xff, 0xff, 0xff], arbitration_id=i))
        time.sleep(0.10)
        
        ret, msg = vcan.read (ctx)

        while msg != None:
            if msg != None and msg.dlc >= 3  and msg.data[0] > 1 and msg.data[0] < 8 and  ((msg.data[0x1] == 0x50 and msg.data[0x2] == 0x01) or msg.data[0x1] == 0x7F):
                context.output ("Receive id " +  hex(msg.arbitration_id) + " data " + hex_array (msg.data) + " with canid " + hex(i))
                lcanid.append([i, msg.arbitration_id])
            ret, msg = vcan.read (ctx)

    for item in lcanid:
        context.output("UDS service detected (canid_send=%3x, canid_receive=%3x)" % (item[0], item[1]))



