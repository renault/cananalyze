#!/usr/bin/env python3
"""
Unified Diagnostic Services : **Security Access module**
"""

from cananalyze.tools import *
from . import context
from . import uds

def custom_sa(ctx, data, key):
    """Custom Security Access generation

    :param ctx: application context
    :param data: data received
    :paran key: key file path
    :return: seed bytes array
    """
    return [0] * 32

def request_seed (ctx, sa):
    """Request a Security Access seed

    :param ctx: application context
    :paran sa: the generated security access
    :return: error status (-1 : problem to send/receive request, -2 UDS error, 0 success), data 
    """
    ret = uds.write (ctx, [0x27, sa])
    if -1 == ret:
        debug (2, "sa_request_seed: error occured during data transmission")
        return  -1, None
    else: 
        context.debug (2, "sa_request_seed: SecurityAccess %d request \
        successfully sent" % sa)

    err, data = uds.read (ctx, "sa_request_seed", 0x27, -1)
    if -1 == err:
        context.debug (2, "sa_request_seed: no response received")
    elif data [0] == 0x67:
        context.output ("sa_request_seed: received seed" + hex_array (data))
    
    return err, data

def send_key (ctx, sa, data, key, alg = custom_sa):
    """Send security access key

    :param ctx: application context
    :paran sa: the generated security access
    :param data:
    :param key: the file key path
    :param algo: the cryptographic mechanism to use
    :return: -1 on error else 0
    """
    res = alg (ctx, data , key)
    if -1 == res:
        context.output ("sa_send_key: failed to compute key, operation aborted")
        return -1

    arr = [0x27, sa + 1] + res
    context.output ("sa_send_key: sending " + hex_array (arr))
    uds.write (ctx, arr)

    err, data = uds.read (ctx, "sa_send_key", 0x27)
    if -1 == err:
        return -1
    elif data [0] == 0x67:
        context.output ("sa_send_key: received positive response " + hex_array (data))
        return 0

    return -1


def start (ctx, sa, key, alg = custom_sa):
    """Main function to request seed for Security Access
    
    :param ctx: application context
    :paran sa: the security access level
    :param key: the file key path
    :param algo: the cryptographic mechanism to use
    :return: -1 on error else 0
    """
    err, data = request_seed(ctx, sa)
    if -1 == err:
        return -1
   
    if 0 > send_key (ctx, sa, data, key, alg):
        return -1

    return 0

