#!/usr/bin/env python3
"""
Unified Diagnostic Services : **Routine Control module**

Implements Remote Activation Of Routine Functional Unit

* RoutineControl
"""

from . import context
from cananalyze.tools import *
from . import uds

def start (ctx, req ,routine_id, data):
    """ Start routine specified by ROUTINE_ID parameter. Returns result
    sent by target ECU
    :param ctx: application context
    :param req: action (0 = noRequest, 1 = startRoutine, 2 = stopRoutine)	
    :param routine_id: id of the routine
    :paran data: data to send
    :return: error status (-1 = error to send/receive request, -2 = UDS error, 0 == sucess), data

    """
    ret = uds.write (ctx, [0x31, req] + int_to_array (routine_id, 2) + data)
    if -1 == ret:
        context.output ("rc: error occured during message sending, abort")
        return -1, None

    err, data = uds.read (ctx, "rc", 0x31)
    if -1 == err:
        return err, None

    context.output ("rc: received " +  hex_array (data))
    return err, data

