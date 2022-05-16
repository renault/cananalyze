#!/usr/bin/env python3
'''
This script dumps all ISOTP messages read from an interface.
'''

import sys
from array import array
import time
import can
import argparse
import cananalyze.abstract_can as vcan
import cananalyze.isotp as isotp
import cananalyze.context as context
from cananalyze.context import BusType

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="dump all ISOTP messages from an interface")
    parser.add_argument("channel", help="\"A\", \"B\", \"vcanX\" depending if bustype is komodo or socketcan")
    parser.add_argument("bustype", help="\"komodo\",  \"socketcan\", ... ")
    args = parser.parse_args()

    ctx_read  = context.create_ctx (channel = args.channel,
                                    bustype = args.bustype,
                                    bitrate = 0,
                                    canid_recv = 0,
                                    canid_send = 0,
                                    timeout = 2)

    while True:
        err, msg = isotp.read(ctx_read)
        print("RetCode=%u, Message=%s" % (err, msg))
