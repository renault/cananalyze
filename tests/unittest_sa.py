#!/usr/bin/env python2

from array import array, ArrayType
import os, time
from multiprocessing import Process, Lock, Value, Queue
import unittest
import netifaces
import cananalyze.abstract_can as vcan
import cananalyze.context as context
import cananalyze.isotp as isotp
import cananalyze.security_access as sa
from tests_tools import *

ctxlock = Lock()
intf='vcan0'

def generate_key(ctx, data, key):
    return [0x42]
def virtualECU(ctx):
    limit = 0
    while limit < 5:
        (ret, message) = vcan.read(ctx)
        if ret != 0 or message == None:
            limit = limit + 1
            time.sleep(0.1)
            continue 
        
        if message.arbitration_id != ctx.canid_recv():
            print("read message not forme")
            continue

        if len(message.data) >= 4 and message.data[0x01] == 0x27:
            if message.data[0x02] == 0x0:
                data_send = array('B', [0x03, 0x27 + 0x40, 0x01 , 0x42, 0, 0, 0, 0])
            elif message.data[0x3] == 0x42:
                data_send = array('B', [0x03, 0x27 + 0x40, 0x02, 0, 0, 0, 0])
            else:
                data_send = array('B', [0x03, 0x7F, 0x27, 0x10, 0, 0, 0, 0])
            vcan.write(ctx,can.Message(data = data_send))
    

class TestUDS(unittest.TestCase):
    ctxECU = None
    ctxt   = None

    def test_sa(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        result = sa.start(self.ctxt, 0x00,  0x1234, generate_key)
        self.assertEqual(result, 0x00)
        p.join()

if __name__ == '__main__':
    
    ctx1 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x400, canid_send = 0x450, timeout = 1)
    ctx2 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x450, canid_send = 0x400, timeout = 1)
 
    TestUDS.ctxECU = ctx1
    TestUDS.ctxt   = ctx2
    unittest.main(exit=False)
    
    
