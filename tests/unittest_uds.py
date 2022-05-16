#!/usr/bin/env python2

from array import array
import os, time
from multiprocessing import Process, Lock, Value, Queue
import unittest
import cananalyze.abstract_can as vcan
import cananalyze.context as context
import cananalyze.isotp as isotp
import cananalyze.diag_session as diag
from tests_tools import *

ctxlock = Lock()
intf='vcan0'

def virtualECU(ctx):
    virtualECUIsRun = True 
    while virtualECUIsRun:
        (ret, message) = vcan.read(ctx)
        if ret == 0 and message != None and len(message.data) > 3:
                data_recv = message.data
                data_send = array('B', [0x03, 0x7F, 0x10, 0x12, 0, 0, 0, 0])
                if data_recv[0x01] == 0x10 and data_recv[0x02] == 0x01:
                    data_send = array('B', [0x02, 0x50, 0x01, 0, 0, 0, 0, 0])
                vcan.write(ctx,can.Message(data = data_send))
                virtualECUIsRun = False
        time.sleep(0.01)

class TestUDS(unittest.TestCase):
    ctxECU = None
    ctxt   = None

    def test_session_supported(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        time.sleep(0.5)
        ret = diag.start(self.ctxt, 0x01, False) 

        self.assertEqual(ret, 0)
        p.join()

    def test_session_notsupported(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        ret = diag.start(self.ctxt, 0x80, False)
        self.assertEqual(ret, -1)
        p.join()
if __name__ == '__main__':
    
    ctx1 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x400, canid_send = 0x450, timeout = 1)
    ctx2 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x450, canid_send = 0x400, timeout = 1)
 
    TestUDS.ctxECU = ctx1
    TestUDS.ctxt   = ctx2
    unittest.main(exit=False)
    
    
