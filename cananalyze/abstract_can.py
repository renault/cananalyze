#!/usr/bin/env python3
"""
Abstract Controller Area Network module
"""

from . import context
import time
from . import python_can as pycan
from . import komodo_can as kcan


def write (ctx, msg, can_id = -1):
    """Abstract CAN interface to write data to can BUS

    :param ctx: application context
    :param msg: data buffer to write
    :param can_id: set can_id parameter to override ctx one
    :return: 0 on success -1 on error
    """
    ret = ctx.get_can().write (ctx, msg, can_id)
    ctx.set_last_timestamp(time.time())
    return ret


def read (ctx):
    """Abstract CAN interface to read data from can BUS
    Returns (0, None) in no message or timeout
    :param ctx: application context
    :return: 0 on success -1 on error, CAN message
    """
    ret, msg = ctx.get_can().read(ctx)
    if msg != None:
        context.cache_update (ctx, msg)
    return ret, msg


def sniff(ctx, max=0):
    """CAN interface to dump packets on standard output"""

    nolimit = False
    if max == 0:
        nolimit = True
    while nolimit or max > 0:
        ret, msg = read(ctx)
        if msg is not None:
            print("Ox%x#%s" % (msg.arbitration_id, tools.hex_array(msg.data)))
        else:
            print("timeout")
        max -= 1
