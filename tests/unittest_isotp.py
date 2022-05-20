#!/usr/bin/env python3

from multiprocessing import Process, Lock
import unittest
import cananalyze.context as context
import cananalyze.isotp as isotp
import tests_tools

ctxlock = Lock()
intf='vcan0'

def virtualECU(ctx):
        isotp.write(ctx, [0x10, 0x01])
        isotp.write(ctx, [0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09])

class TestUDS(unittest.TestCase):
    ctxECU = None
    ctxt   = None

    def test_sa(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        
        (err, data) = isotp.read(self.ctxt)
        self.assertEqual(data, [0x10,0x01])
        (err, data) = isotp.read(self.ctxt)
        self.assertEqual(data,  [0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09])
        p.join()

if __name__ == '__main__':
    if tests_tools.check_context(intf): 
        ctx1 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x400, canid_send = 0x450, timeout = 1)
        ctx2 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x450, canid_send = 0x400, timeout = 1)
     
        TestUDS.ctxECU = ctx1
        TestUDS.ctxt   = ctx2
        unittest.main(exit=False)
    
    
