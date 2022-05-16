#!/usr/bin/env python3
"""
ISO-TP ISO 15765-2 data packets over CAN-Bus (Transport Layer) module
"""

from array import array
from cananalyze.tools import *
from . import context 
import can
from . import abstract_can as acan
import time

def _write_frag (ctx, data): 
    """isotp implementation of message sending

    :param ctx: application context
    :param data: data buffer to write
    :return: -1 on error else 0
    """

    sn = 1
    ff_dl = len (data)
    
    ff = [0x10 | (ff_dl >> 8), ff_dl & 255] + data [0:6]
    bs = 0

    # Add ISOTP PADDING
    if (len(data)  - 6) % 7 != 0: 
        data = data + [0] * max( 7 - ((len(data)  - 6) % 7) , 0)
    ff_dl = len (data)

    msg = can.Message(data = ff)
    ret = acan.write (ctx, msg)
    if ret:
        return -1

    fc_format = []
    for i in range (0x10):
        fc_format.append ([0x30 | i])

    (err, data_fc) = _read_first (ctx, mdata = fc_format, bitmask = 1)
    if err == -1 or data_fc is None:
        return err

    def parse_fc_parms (fc):
        global bs 
        context.debug (4, "isotp.parse_fc_parms: " + hex_array (fc))
        fs, bs, stmin = fc [0] & 15, fc [1], fc [2]
        context.debug (3, "isotp.parse_fc_parms: received flow control parameters %x %x %x" \
                % (fs, bs, stmin), ctx)
    parse_fc_parms (data_fc)

    # adjust data length according to the first frame sent
    ff_dl -= 6
    #data = list(msg.data [6:])
    data = data[6:]

    current_bs = 0

    while ff_dl > 0:
        cf_dl = ff_dl - (max (0, ff_dl - 7)) 
        #cf = array ("B", [0x20 | sn] + data [0:cf_dl])
        cf = [0x20 | sn] + data [0:cf_dl]

        context.debug (4, "isotp._write_frag: sending CF " + hex_array (cf))

        msg = can.Message (data = cf)
        ret = acan.write (ctx, msg)
        if ret == -1:
            return ret

        sn = (sn + 1) % 16
        data = data [cf_dl:]
        ff_dl = len (data)
        current_bs += 1

        if current_bs == bs:
            (ret, msg) = _read_first (ctx, mdata = fc_format, bitmask = 1)
            if ret == -1:
                return ret
            parse_fc_parms (msg.data)
            current_bs = 0

    # TODO consume last ACQ
    
    return 0


def write (ctx, data):
    """Data emission, isotp case implementation

    :param ctx: application context
    :param data: data buffer to write
    :return: -1 on error else 0
    """
    ret = 0

    if len (data) > 7:
        context.debug (4, "isotp.write: data = [" + hex_array(data) + "] len > 7")
        ret = _write_frag (ctx, data)
    else:
        context.debug (4, "isotp.write: data = [" + hex_array(data) + "] len <= 7")
        msg = can.Message(data = [len (data)] + data + [0] * max(7-len(data), 0) )
        ret = acan.write (ctx, msg)
        """
        if ret == 0:
            # Wait for an ACQ ?
            context.debug (2, "isotp.write: FIXME wait for an ACQ")

        """
    return ret


def _read_frag (ctx, ff):
    """isotp implementation of data reception

    :param ctx: application context
    :param ff: the packet fragment read
    :return: (errn fragment data)
    """

    # Check for N_PCIType
    if ff [0] >> 4 != 1:
        context.debug (1, "isotp._read_frag: ff wrong format")
        return (-1, None)

    # skip headers and init data buffer 
    buf = list (ff [2:8])
    ff_dl = ((ff [0] & 15) << 8) + ff [1]

    context.debug (4, "isotp._read_frag: %d bytes to receive" % ff_dl, ctx)

    # Send Flow Control<
    # SF, BS, STmin
    #fc = array ("B", [0b00110000, 0, 0, 0, 0, 0, 0, 0])
    #fc = array ("B", [0b00110000, 0x02, 0x14, 0, 0, 0, 0, 0])
    #fc = array ("B", [0b00110000, 0xFF, 0x14])
    #fc = array ("B", [0b00110000, 0x40, 0x14, 0, 0, 0, 0, 0])
    ackmax = 0x40
    messageWithoutAck = 1 
    fc = array ("B", [0b00110000, ackmax, 0x14, 0, 0, 0, 0, 0])
    acan.write (ctx, can.Message(data = fc))
    # Receive consecutive frames
    ff_dl -= 6
    sn = 0
    while ff_dl:
        sn = (sn + 1) % 16
        (err, pkt) = _read_first (ctx, ctx.canid_recv (), mdata = [[0x20 + sn]], bitmask = [1])

        if -1 == err:
            context.debug (1, "isotp._read_frag: err " + str(err))
            return (err, None)

        context.debug (4, "isotp._read_frag: received " + hex_array (pkt))
        assert pkt [0] >> 4 == 2
        sn = pkt [0] & 15

        context.debug (4, "isotp._read_frag: received packet %d" % sn, ctx)
        buf = buf + list (pkt [1: min (ff_dl, 7) + 1])
        ff_dl = max (ff_dl - 7, 0)
        if messageWithoutAck == ackmax:
            acan.write (ctx, can.Message(data = fc))
            messageWithoutAck = 1
            messageWithoutAck = messageWithoutAck + 1
        
        context.debug (4, "isotp._read_frag: ff_dl %d" % ff_dl, ctx)
        
    return (0, buf)

def read (ctx,
          can_id = -1,
          mdata = -1,
          limit = 3,
          ignore_timeout = False,
          bitmask = -1,
          timestamp = -1):
    """Main data reception

    :param ctx: application context
    :param can_id: set can_id parameter to override ctx one
    :param mdata: the data to match, if not -1 also match for the length and data part
    :param limit: seconds to wait for the given packet
    :param ignore_timeout:
    :bitmask: gives a bitmask of indices of mdata bytes to compare with received packet
    :param timestamp: to match a packet that did not occur before timestamp
    :return: tuple (err, data) err is -1 on error else 0
    """
    (err, data) = _read_first (ctx, can_id,
                               mdata, limit, ignore_timeout,
                               bitmask, timestamp)
    if err == -1 or data == None:
        context.debug (2, "isotp.read: no response received")
        return (err, data)

    (err, data) = _read_dispacher (ctx, data)
    if err == -1:
        context.debug (1, "isotp.read: transfer failed")

    return (err, data)


def _read_dispacher(ctx, data):
    """Data reception, isotp case implementation

    Dispatch packets from SF to FF.
    SF is for a Single Frame.
    FF is First Frame.
    Can debugger if not.

    :param ctx: application context
    :param data: received data
    :return: (err, data packet) for SF and (err, data fragment) for FF
    """
    N_PCItype = data[0] >> 4
    
    # SF case 
    if N_PCItype == 0:
        messageLen = data[0]
        return 0, data[1:messageLen+1]
    # FF case
    elif N_PCItype == 1:
        return _read_frag (ctx, data)
    else:
        pdb.set_trace ()

def _read_first (ctx,
                can_id = -1,
                mdata = -1,
                limit = 3,
                ignore_timeout = False,
                bitmask = -1,
                timestamp = -1):
    """Wait for a packet, optionally given a CAN_ID and matching
    MDATA. Returns a tuple (info, pkt, data) as it is returned by
    km_can_read.

    :param ctx: application context
    :param can_id: set can_id parameter to override ctx one
    :param mdata: the data to match, if not -1 also match for the length and data part
    :param limit: wait for a maximum of LIMIT seconds,
                  then return even if packet was not found
    :param timestamp: to match a packet that dit not occur before TIMESTAMP
    :bitmask: gives a bitmask of indices of mdata bytes to compare with received packet
    :return: tuple (err, data) err is -1 on error else 0
    """

    count = 0
    timestamp = timestamp if timestamp != -1 else ctx.get_last_timestamp()
    cache = context.cache_lookup (ctx, timestamp)
    cache.reverse ()
    cache = []
    t = time.time ()
    msg = None
    ret = 0

    context.debug (4, "isotp._read_first: found %d entrie(s) in cache" % len (cache))

    while (limit == -1) or ((1 * (time.time () - t)) < limit):
        if cache:
            msg = cache.pop ()
        else:
            (ret, msg) = acan.read (ctx)
        
        if ret == 0 and msg is None:
            if ignore_timeout:
                context.debug (1, "isotp._read_first: timeout, abort", ctx)
                return (ret, None)
            else:
                continue
        elif ret < 0:
            context.debug (1, "isotp._read_first: error ", ret)
            return (ret, list(msg.data))

        if can_id == -1 or msg.arbitration_id == can_id:
            context.debug(3, "isotp._read_first: try to match")
            if mdata == -1 or match (mdata, msg.data, bitmask):
                ctx.set_last_timestamp(msg.timestamp)
                return (ret, list(msg.data))

        if ctx.canid_recv() == msg.arbitration_id:
            context.debug (3, "isotp._read_first: drop " + hex_array (msg.data))

    context.debug (2, "isotp._read_first: limit reached, packet not found", ctx)

    return (-1, None)

