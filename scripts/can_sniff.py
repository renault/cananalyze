#!/usr/bin/env python3
'''
This script dumps all CAN messages read from an interface.
'''

import sys
from array import array, ArrayType
import time
import can
import argparse

import cananalyze.abstract_can as vcan
import cananalyze.context as context
from cananalyze.context import BusType

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="dump all CAN messages read from an interface")
    parser.add_argument("channel", help="\"A\", \"B\", \"vcanX\" depending if bustype is komodo or socketcan")
    parser.add_argument("bustype", help="\"komodo\",  \"socketcan\", ... ")
    parser.add_argument("--count", help="the number of packets to get")
    args = parser.parse_args()

  
    ctx_read  = context.create_ctx (channel = args.channel,
                                    bustype = args.bustype,
                                    port_nr = 0,
                                    bitrate = 500000,
                                    canid_recv = 0,
                                    canid_send = 0,
                                    timeout = None)
    if args.count :
        vcan.sniff (ctx_read, max=int(args.count))
    else:
        vcan.sniff (ctx_read)
