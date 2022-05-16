#!/usr/bin/env python2

from array import array
import os, time
from multiprocessing import Process, Lock, Value, Queue
import unittest
import can
import cananalyze.abstract_can as vcan
import cananalyze.context as context
import cananalyze.isotp as isotp
import cananalyze.scan as scan
import tests_tools

ctxlock = Lock()
intf='vcan0'
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

        if len(message.data) >= 2:
            data_send = array('B', [0x03, 0x7F, message.data[0x01], 0x11, 0, 0, 0, 0])
            if message.data[0x01] == 0x10:
                if message.data[0x02] == 0x1 or message.data[0x02] == 0x2 or message.data[0x02] == 0x3:
                    data_send = array('B', [0x02, 0x50, message.data[0x02], 0, 0, 0, 0, 0])
                else:
                    data_send = array('B', [0x03, 0x7F, message.data[0x01], 0x12, 0, 0, 0, 0])
            vcan.write(ctx,can.Message(data = data_send))
    

class TestUDS(unittest.TestCase):
    ctxECU = None
    ctxt   = None

    def test_scan_service(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        lservice = scan.services(self.ctxt)
        self.assertEqual(lservice, [0x10])
        p.join()

    def test_scan_session(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        lsession = scan.sessions(self.ctxt)
        self.assertEqual(lsession, [0x1, 0x2, 0x3])
        p.join()

    def test_scan_services_session(self):
        p = Process(target=virtualECU, args=(self.ctxECU,))
        p.start()
        lsession = scan.services_sessions(self.ctxt)
        self.assertEqual(lsession, [[0x10, 0x1, False], [0x10, 0x2, False], [0x10, 0x3, False]])
        p.join()

if __name__ == '__main__':
    if tests_tools.check_context(intf): 
        ctx1 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x400, canid_send = 0x450, timeout = 1)
        ctx2 = context.create_ctx (channel = intf, bustype = 'socketcan', bitrate = 115200, canid_recv = 0x450, canid_send = 0x400, timeout = 1)
     
        TestUDS.ctxECU = ctx1
        TestUDS.ctxt   = ctx2
        unittest.main(exit=False)
        
    
