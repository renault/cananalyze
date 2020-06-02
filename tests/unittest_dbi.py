#!/usr/bin/env python2

from array import array, ArrayType
import os, time
from multiprocessing import Process, Lock, Value, Queue
import unittest
import netifaces
import cananalyze.abstract_can as vcan
import cananalyze.context as context
import cananalyze.isotp as isotp
import cananalyze.diag_session as diag
import cananalyze.data_by_identifier as dbi
from tests_tools import *

ctxlock = Lock()
intf='vcan0'
global VALUE 
def virtualECU(ctx):
    global VALUE
    virtualECUIsRun = True 
    while virtualECUIsRun:
        (ret, message) = vcan.read(ctx)
        if ret == 0 and message != None and len(message.data) > 3:
                data_recv = message.data
                if data_recv[0x01] == 0x2E  and data_recv[0x02] == 0x12 and data_recv[0x03] == 0x34:
                    VALUE = data_recv[0x04]
                    data_send = array('B', [0x04, 0x2E + 0x40, 0x12, 0x34, 0, 0, 0, 0])
                    vcan.write(ctx,can.Message(data = data_send))
                if data_recv[0x01] == 0x2E  and data_recv[0x02] == 0x12 and data_recv[0x03] == 0x34:
                    data_send = array('B', [0x04, 0x22 + 0x40, 0x12, 0x34, VALUE, 0, 0, 0])
                    vcan.write(ctx,can.Message(data = data_send))
                    virtualECUIsRun = False
        time.sleep(0.01)

class TestUDS(unittest.TestCase):
    ctxECU = None
    ctxt   = None

    def test_dbi(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        time.sleep(0.5)
        dbi.write(self.ctxt, 0x1234, [0xAB])
        e, value = dbi.read(self.ctxt, 0x1234)
        
        self.assertEqual(0, e)
        self.assertEqual(value[3], 0xAB)
        p.join()

if __name__ == '__main__': 
    ctx1 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x400, canid_send = 0x450, timeout = 1)
    ctx2 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x450, canid_send = 0x400, timeout = 1)
 
    TestUDS.ctxECU = ctx1
    TestUDS.ctxt   = ctx2
    unittest.main(exit=False)
    
    
