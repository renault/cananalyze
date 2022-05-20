#!/usr/bin/env python3
"""
Context module.

Global context module for each application.
Manage contexts, opened ports, initialized channels ...
"""

import os
import time
import threading
import signal
import sys
import can

from cananalyze.tools import *

# If ctx is an instance of `Ctx' class, `g_ctxs' dict contains entries
# in the form `id (ctx) : ctx'; this variable keeps a track on all
# context objects
g_ctxs = {}

# stdout file descriptor mutex
stdout_lock = threading.Lock ()

# Verbosity level
VERBOSE = 1

# content cache of recently received packets. Used by cache_* family
# functions to handle can data shared between multiple threads
CACHE = []
CACHE_MAX_SIZE = 5000
CACHE_STEP = 1000 # Number of old entries to remove when limit is
                  # reached
CACHE_LOCK = threading.Lock ()


class BusType:
    KOMODO = "komodo"
    SOCKETCAN = "socketcan"
    VECTOR = "vector"


class Ctx:

    class ExtendedMode:
        AUTO = 0
        FORCED_EXTENDED = 1
        FORCED_NOT_EXTENDED = 2

    """A context object is tied to a specific port, channel and can id.

    Bus type should be :
    * "komodo" :
    * Any python-can BUS interface (socketcan, ...)

    :param bustype: the CAN bus type
    :param port_nr: komodo port number
    :param channel: CAN channel
    :param bitrate: channel bitrate
    :param canid_recv: todo
    :param canid_send: todo
    :param timeout: read timeout
    :param extended: extended mode 'auto' 'forced_extended' 'forced_not_extended'
    """
    def __init__ (self, bustype, channel, port_nr,
                  bitrate,
                  canid_recv, canid_send, timeout, extended):
        self.__port_nr = port_nr
        self.__channel = channel
        self.__can_intf = None
        self.__bustype = bustype
        self.__bus     = None
        self.__timeout = timeout
        self.__bitrate = bitrate
        self.__canid_recv, self.__canid_send = canid_recv, canid_send
        self.__last_timestamp = -1
        self.__diag_session = 0
        self.__diag_tester_thread = None
        self.__extended = extended
        self.__can_intf = None
        self.__mutex = threading.Lock()

    def init_can (self):
        """Initialize CAN interface

        :return: 0 on success -1 on error
        """
        from . import python_can as pycan
        from . import komodo_can as kcan
        # Check CAN interface
        if self.__bustype == BusType.KOMODO:
            self.__can_intf = kcan
        elif self.__bustype == BusType.SOCKETCAN or self.__bustype == BusType.VECTOR:
            self.__can_intf = pycan
        else:
            context.debug (1, "abstract_can.init: unknown bustype " + self.__bustype)
            return -1
        return self.__can_intf.init(self)

    def get_diag_tester_thread(self):
        return self.__diag_tester_thread

    def set_diag_tester_thread(self, tester):
        self.__diag_tester_thread = tester

    def get_diag_session(self):
        return self.__diag_session

    def set_diag_session(self, session):
        self.__daig_session = session

    def get_bitrate(self):
        return self.__bitrate
    def get_port_nr(self):
        return self.__port_nr

    def get_last_timestamp(self):
        return self.__last_timestamp

    def get_bustype(self):
        return self.__bustype

    def get_bus(self):
       return self.__bus

    def get_can(self):
       return self.__can_intf

    def get_timeout(self):
       return self.__timeout

    def get_channel (self):
       return self.__channel

    def get_extended_id (self):
       return self.__extended

    def canid_recv (self):
        return self.__canid_recv

    def canid_send (self):
        return self.__canid_send

    def set_bus(self, bus):
        self.__bus = bus

    def set_samplerate(self, samplerate):
        self.__samplerate = samplerate

    def set_last_timestamp (self, timestamp):
        self.__last_timestamp = timestamp

    def set_canid_recv (self, canid):
        self.__canid_recv = canid

    def set_canid_send (self, canid):
        self.__canid_send = canid
   
    def set_channel(self, channel):
        self.__channel = channel
    
    def set_port_l(self, port):
        self.__set_port_l = port

    def set_timeout(self, timeout):
        self.__timeout = timeout

    def lock_acquire (self):
        self.__mutex.acquire()
        True

    def lock_release (self):
        self.__mutex.release()
        True


class packet_t:
    """This class define stored packet type cache entry

    :param ret: status code
    :param info: packet info (timestamp, events, channel, bitrate...)
    :param pkt: CAN packet header
    :param data: packet data
    """
    def __init__ (self, ret, info, pkt, data):
        self.ret, self.info, self.pkt, self.data = ret, info, pkt, data

def cache_lookup (ctx, timestamp):
    """Return all cache entries, in the form of packet_t list, that
    happened after timestamp

    :param ctx: application context
    :param timestamp: the start timestamp
    :return: packets list
    """
    global CACHE_LOCK

    CACHE_LOCK.acquire ()
    elts = [e for e in CACHE if timestamp < e.timestamp]
    CACHE_LOCK.release ()
    return elts

def cache_update (ctx, packet):
    """Insert packet into cache area if and only if it's canid is
    referenced by any global context. packet is returned if it is
    actually inserted

    :param ctx: application context
    :param packet: received packet
    :return: packet
    """
    global CACHE

    if None == packet or not isinstance (packet, can.Message):
        debug (3, "cache_update: wrong argument type / invalid packet") 
        return -1

    can_ids_recv = set ()
    for e in g_ctxs:
        can_ids_recv.add (get(e).canid_recv())

    if packet.arbitration_id not in can_ids_recv:
        return 0

    debug (3, "cache_update: appended " + hex_array (packet.data))

    CACHE_LOCK.acquire ()
    if len (CACHE) == CACHE_MAX_SIZE:
        cache = CACHE [CACHE_STEP:]
    CACHE.append (packet)
    CACHE_LOCK.release ()

    return packet

def debug (level, msg, ctx=None):
    """Output MSG if given LEVEL is less or equal than verbosity global
    variable

    """
    if level <= VERBOSE:
        output (msg, ctx)

def output (s, ctx = None, prefix = None):
    if prefix == None: 
        prefix = "Thread {0:d} - {1:.3f}".format (
            threading.current_thread ().ident % 100000,
            time.time ())

        if ctx != None:
            prefix = str (id (ctx)) + " " + prefix 

        prefix = "[" + prefix + "]"

    stdout_lock.acquire (True)
    print(prefix + s)
    # os.fsync (sys.stdout.fileno ())
    sys.stdout.flush ()
    stdout_lock.release ()



def signal_handler(signal, frame):
    os._exit(0)

def get(ctx_id):
    global g_ctxs
    return g_ctxs [ctx_id]

def create_ctx (bustype=BusType.KOMODO, port_nr = 0, channel = "A",
                bitrate = 125000,
                canid_recv = 0x664, canid_send = 0x764,
                timeout = 0, extended = Ctx.ExtendedMode.AUTO,
                trace = 1):
    """Ctx instance factory. IMPORTANT: do not set timeout to infinite in
    multithreading context (light processes would block each other)

    """
    global VERBOSE
    global g_ctxs
    #signal.signal(signal.SIGINT, signal_handler)

    # Create context instance
    ret = Ctx (bustype, channel, port_nr, bitrate, canid_recv, canid_send, timeout, extended)

    # Initialize specific context
    if ret.init_can():
        debug (1, "create_ctx: error occured")
        return None

    # Set debug level
    #VERBOSE = trace

    g_ctxs [id (ret)] = ret
    return ret


sigStop = threading.Event()
tw = None

def wake_up(sigStop, ctx, frames):
    while not sigStop.wait(0.150):
        for f in frames:
            ctx.get_can().write(ctx, can.Message(data=f[1]),f[0])


def wakeup_start(ctx, frames=[[0x47d,[0x0,0xc0,0x70,0x0,0x0,0x0,0x0,0x0]],[0x418, [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]],[0x46b, [0x1,0x0,0x0,0x0,0x0,0x0,0x0,0x0]],[0x46f, [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]],[0x47f, [0x0,0x0,0x0,0x0,0x8,0x0,0x0,0x0]],[0x47c, [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]]]):
    global sigStop, tw
    sigStop = threading.Event()
    tw = threading.Thread(target=wake_up, args=[sigStop,ctx,frames])
    tw.start()
    time.sleep(3)

def wakeup_stop():
    global sigStop, tw
    if tw != None:
        sigStop.set()
        tw.join()

