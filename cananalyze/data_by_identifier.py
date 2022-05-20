#!/usr/bin/env python3
"""
Unified Diagnostic Services : **Data By Identifier module**

Implement data transmission functional unit :

* ReadDataByIdentifier
* WriteDataByIdentifier
"""

from cananalyze.tools import *
from . import context 
from . import uds


def write (ctx, id, data):
    """Write data by identifier

    :param ctx: application context
    :param id: the identifier
    :param data: data buffer to write
    :return: data read
    """
    dbi = [(id & 0xff00) >> 8, id & 0xff]
    ret = uds.write (ctx, [0x2E] +  dbi + data)
    if -1 == ret:
        return ret

    (err, data) = uds.read (ctx, "read_dbi", 0x2E)
    if -1 == err:
        context.output ("write_dbi: no response", ctx)
        return -1

    context.output ("write_dbi: " + hex_array (data), ctx)
    return data

def read (ctx, id):
    """Read data by identifier

    :param ctx: application context
    :param id: the identifier
    :return: -1 on error else 0, data read
    """
    dbi = [(id & 0xff00) >> 8, id & 0xff]
    ret = uds.write (ctx, [0x22] +  dbi)

    if -1 == ret:
        return ret

    (err, data) = uds.read (ctx, "read_dbi", 0x22)
    #info, pkt, data, err = uds.read (ctx, "read_dbi", 0x22)
    if -1 == err:
        context.output ("read_dbi: no response", ctx)
        return -1, None

    context.output ("read_dbi: " + hex_array (data), ctx)
    return err, data
