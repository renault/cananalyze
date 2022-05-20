#!/usr/bin/env python3
"""
Controller Area Network module

CAN interface python-can
"""

import can
import copy
import context

def init (ctx_obj):
    """Initialisation global context object for python-can interface

    :param ctx_obj: the application context
    :return: 0 on success -1 on error
    """
    b = can.interface.Bus(bustype=ctx_obj.get_bustype(),
            channel=ctx_obj.get_channel(),
            bitrate=ctx_obj.get_bitrate(),
            app_name='python-can',
            fd=True,
            data_bitrate=2000000)
    context.debug (3, "pycan.init: can bus initialized")
    ctx_obj.set_bus(b)
    if ctx_obj.get_timeout() == 0:
        ctx_obj.timeout = None
    return 0


def write (ctx, msg, can_id = -1):
    """Write data to can BUS

    :param ctx: application context
    :param msg: CAN message to send
    :param can_id: set can_id parameter to override ctx one
    :return: 0 on success -1 on error
    """
    ret = 0
    nmsg = msg

    ctx.lock_acquire ()

    # Force CAN id to context one
    current_canid = can_id
    if current_canid == -1:
        current_canid = ctx.canid_send()

    # Set extended id value
    current_ext_id = False
    if ctx.get_extended_id() == context.Ctx.ExtendedMode.FORCED_EXTENDED or \
       (ctx.get_extended_id() == context.Ctx.ExtendedMode.AUTO and current_canid > 0xFFF):
        current_ext_id = True

    nmsg = can.Message(is_extended_id = current_ext_id,
                       arbitration_id = int(current_canid),
                       data=msg.data, is_fd=True)

    context.debug (4, "pycan.write: " + str(nmsg))

    bus = ctx.get_bus()
    try:
        bus.send(copy.deepcopy(nmsg))
    except Exception as e:
        context.debug (2, "pycan.write: exception " + str(e))
        ret = -1
    ctx.lock_release()
 
    return ret


def read (ctx):
    """Read data from can BUS

    Returns (0, None) in no message or timeout

    :param ctx: application context
    :return: return code, CAN message
    """
    msg = None
    ctx.lock_acquire ()
    bus = ctx.get_bus()
    try:
        msg = bus.recv(timeout=ctx.get_timeout())
        context.debug (4, "pycan.read: " + str(msg))
    except Exception as e:
        context.debug (2, "pycan.read: exception", str(e))
        return 0, None
    ctx.lock_release()
    return 0, msg
