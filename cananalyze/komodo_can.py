#!/usr/bin/env python3
"""
Controller Area Network module

CAN interface for Komodo module.
"""

import argparse
import can

from . import komodo_py
from . import context
import threading
from . import tools

# `ports' variable holds komodo's port access mutex in the form
# `Komodo : Lock'. It is principally used to keep a reference to a
# previously initialized port when it is accessed
ports = {}

# this global array records all previously initialized channels
chans = []

def _km_print_err (func_name, ret):
    """Print Komodo status code

    :param func_name: the function name
    :param ret: the returned code
    :return: ret
    """
    if ret == KM_OK:
        return ret
    context.output (func_name + ": %d %s" % (ret, km_status_string (ret)))
    return ret


def init (ctx):
    """Initialisation global context for python-can interface

    :param ctx: the application context
    :return: 0 on success -1 on error
    """
    # Komodo parameters
    if ctx.get_channel() == "A":
        ctx.set_channel(KM_CAN_CH_A)
    else:
        ctx.set_channel(KM_CAN_CH_B)
    if ctx.get_timeout() is None:
        ctx.set_timeout(KM_TIMEOUT_INFINITE)

    ret = _km_open_port (ctx.get_port_nr(), ctx.get_channel(), ctx.get_bitrate(), ctx.get_timeout())
    if -1 == ret:
        return ret
    kmtmp, prot_ltmp = ports [ctx.get_port_nr()]
    ctx.set_port_l(prot_ltmp)
    ctx.km = kmtmp
    ctx.set_samplerate(km_get_samplerate (ctx.km))
    ctx.set_bus(None)
    return 0


def write (ctx, msg, can_id = -1):
    """Write data to can BUS

    :param ctx: application context
    :param msg: CAN message to send
    :param can_id: set can_id parameter to override ctx one
    :return: 0 on success -1 on error
    """

    pkt            = km_can_packet_t()
    if can_id == -1:
        pkt.id = ctx.canid_send()
    else:
        pkt.id = can_id
    pkt.dlc        = msg.dlc

    if ctx.get_extended_id() == context.Ctx.ExtendedMode.FORCED_EXTENDED or pkt.id > 0xFFF:
        pkt.extend_addr= True
    else:
        pkt.extend_addr= False

    context.debug (4, "write_can: " + tools.hex_array(msg.data) + " to id " + hex(pkt.id) +
           " extended " + str(pkt.extend_addr)  )

    ctx.lock_acquire ()
    ret, arbitration_count = km_can_write (ctx.km,
                                           ctx.get_channel(),
                                           0,
                                           pkt,
                                           array ('B', msg.data))
    ctx.lock_release()
 
    if ret != KM_OK:
        _km_print_err ("komodo_can.write:", ret)
        return -1
    return 0


def read (ctx):
    """Read data from can BUS

    :param ctx: application context
    :return: 0 on success -1 on error, CAN message
    """
    msg = None
    ctx.lock_acquire ()
    ret, info, pkt, data = km_can_read (ctx.km, array_u08 (8))
    ctx.lock_release()

    if not (info.status & KM_READ_TIMEOUT) and  pkt.dlc != 0:
        # FIXME missing parameters ?
        msg = can.Message(timestamp=info.timestamp,
                      arbitration_id=pkt.id,
                      #is_extended_id=None,
                      #is_remote_frame=False,
                      #is_error_frame=False,
                      channel=info.channel,
                      dlc=pkt.dlc,
                      data=data,
                      #is_fd=False,
                      #bitrate_switch=False,
                      #error_state_indicator=False,
                      #extended_id=True,
                      #check=False
        )
    
    return ret, msg

"""
def sniff(ctx):
    Dump packets on standard context.output
    print("sniff")
    while True:
        ret, info, pkt, data = read(ctx)
        if ret != -1 and pkt.id != 0 :
            context.output ("id " +  hex(pkt.id) + " data" + tools.hex_array (data) + " " + str(pkt.dlc))
"""

##########################################


def print_events (events, bitrate):
    """Return string representation of the event

    :param events: komodo event
    :param bitrate: bus bitrate
    :return: string value
    """
    ret = ""
    event_strings = {
        KM_EVENT_CAN_BUS_STATE_LISTEN_ONLY : "BUS STATE LISTEN ONLY",
        KM_EVENT_CAN_BUS_STATE_CONTROL : "BUS STATE CONTROL",
        KM_EVENT_CAN_BUS_STATE_WARNING : "BUS STATE WARNING",
        KM_EVENT_CAN_BUS_STATE_ACTIVE : "BUS STATE ACTIVE",
        KM_EVENT_CAN_BUS_STATE_PASSIVE : "BUS STATE PASSIVE",
        KM_EVENT_CAN_BUS_STATE_OFF : "BUS STATE OFF",
        KM_EVENT_CAN_BUS_BITRATE : "BITRATE %d kHz" % (bitrate / 1000),
        KM_EVENT_DIGITAL_INPUT : "GPIO CHANGE 0x%x;" \
        % (events & KM_EVENT_DIGITAL_INPUT_MASK)
    }

    if events == 0:
        return ret

    for item in list(event_strings.items ()):
        if events & item [0]:
            ret += (item [1] + "; ")

    return ret


def print_status (status):
    """Return string representation of status
    
    :param status: komodo interface status
    :return: string status
    """
    status_strings = {
        KM_OK : "OK",
        KM_READ_TIMEOUT : "TIMEOUT",
        KM_READ_ERR_OVERFLOW : "OVERFLOW",
        KM_READ_END_OF_CAPTURE : "END OF CAPTURE",
        KM_READ_CAN_ARB_LOST : "ARBITRATION LOST",
        KM_READ_CAN_ERR : "ERROR %x" % (status & KM_READ_CAN_ERR_FULL_MASK),
    }
    ret = ""
    for item in list(status_strings.items ()):
        if status & item [0]:
            ret += item [1] +  " "
    return ret if ret else "UNKNOWN (%d)" % status


#def arg_parse ():
#    Komodo argument parser for channel initialization
#    :return: tuple (port, channel, bitrate, canid receive, canid send, timeout)
#    
#    parser = argparse.ArgumentParser (
#        description = "Komodo channel initialization")
#
#    parser.add_argument ("--port", "-p", default = 0, type = int,
#                         help = "komodo port number selection")
#    parser.add_argument ("--channel", "-c", choices = ["A", "B"], default = "A",
#                         help = "komodo channel selection")
#    parser.add_argument ("--bitrate", "-b", type = int, default = 500000,
#                         help = "CAN bitrate, in Hz")
#    parser.add_argument ("--timeout", type = int, default = 4000,
#                         help = "CAN read timeout")
#    parser.add_argument ("--canid-recv", type = int, default = 0x652,
#                         help = "canid on reception side")
#    parser.add_argument ("--canid-send", type = int, default = 0x752,
#                         help = "canid on emission side")
#
#    namespace = parser.parse_args ()
#    return namespace.port, \
#        KM_CAN_CH_A if namespace.channel == "A" else KM_CAN_CH_B, \
#        namespace.bitrate, namespace.canid_recv, namespace.canid_send, \
#        namespace.timeout
#

def _km_init_channel (km, channel, bitrate, timeout):
    """Init a komodo channel according to given arguments and a disabled
    komodo port

    """
    global chans

    if channel in chans:
        context.output ("km_init_channel: channel %d already initialized" % channel)
        return 0

    # Permissions required to configure channel
    features = KM_FEATURE_CAN_A_LISTEN \
               | KM_FEATURE_CAN_A_CONFIG \
               | KM_FEATURE_CAN_A_CONTROL

    if channel == KM_CAN_CH_A:
        ret = km_acquire (km, features)
    else:
        features = features << 3
        ret = km_acquire (km, features)

    if ret != features:
        _km_print_err ("komodo_can.km_init_channel:", ret)
        return -1

    context.output ("km_init_channel: Acquired features: %x" % ret)

    """
    if km_can_configure(km, KM_CAN_CONFIG_LISTEN_SELF) != KM_OK: 
        context.output ("open_port: Unable to configure km with km_can_configure")
        return -1
    """

    # Set bitrate and timeout configuration values
    ret = km_can_bitrate (km, channel, bitrate)
    context.output ("km_init_channel: bitrate set to %d" % ret) 
    ret = km_timeout (km, int(timeout * 1000))

    if ret != KM_OK:
        _km_print_err ("komodo_can.km_init_channel:", ret)
        return -1

    context.output ("km_init_channel: timeout set to %d ms" % int(timeout * 1000))
    chans += [channel]
    return 0


def _km_open_port (port_nr, channel, bitrate, timeout, bus_timeout = 1200):
    """Initialize a komodo USB port context

    Open port and create a dedicated lock if required.

    """
    global ports

    if port_nr in ports:
        context.output ("_km_open_port: port %d already configured " % channel)
        return ports [port_nr] [0]

    context.debug (4, "_km_open_port: try to open port %d" % port_nr)
    km = km_open (port_nr)

    if km <= 0:
        av_ports = array_u16 (10)
        km_find_devices (av_ports)
        context.debug  (4, "_km_open_port: Available ports %s" % ", ".join (map (str, av_ports)))

        if km == KM_UNABLE_TO_OPEN:
            context.debug (1, "_km_open_port: Unable to open desired port")
            return -1
        elif km == KM_INCOMPATIBLE_DEVICE:
            context.debug (1, \
                """_km_open_port: Current device is not compatible with
                installed shared library
                """)
            return -1

    context.debug (3, "_km_open_port: port successfully opened")

    ret = _km_init_channel (km, channel, bitrate, timeout)
    if -1 == ret:
        context.debug (1, "_km_open_port: init_channel failed")
        return -1

    ret = km_can_bus_timeout (km, channel, bus_timeout)
    context.debug (3, "_km_open_port: bus timeout set to %d" % ret)

    # enable komodo
    ret = km_enable (km)

    if ret != KM_OK:
        _km_print_err ("komodo_can._km_open_port:", ret)
        return -1

    ports [port_nr] = km, threading.Lock () 
    return km

"""
def port_set_state (ctx, enable = 1):
    ctx.lock_acquire ()
    if enable:
        ret = km_enable (ctx.km)
    else:
        ret = km_disable (ctx.km)
    ctx.lock_release()

    if ret != KM_OK:
        _km_print_err ("komodo_can.port_set_state:", ret)
    return ret


def samplerate_khz (ctx):
    port_set_state (ctx, 0)
    ctx.lock_acquire ()
    samplerate_khz = km_get_samplerate (ctx.km) / 1000
    ctx.lock_release()
    port_set_state (ctx, 1)
    return samplerate_khz
"""
