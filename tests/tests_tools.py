#!/usr/bin/env python3

#from array import array, ArrayType
import os, time
import cananalyze.abstract_can as vcan
import cananalyze.isotp as isotp
import cananalyze.context as context
from cananalyze.context import BusType
import can

def check_context(intf):
    '''Check if virtual CAN interfaces are set up
    :param intf: socketcan can interface
    '''
    context_cmd = 'sudo ./tests/setup_vcan.sh'
    ret = os.system('ifconfig|grep "^' + intf + '" 2>&1 > /dev/null')
    if ret:
        print(("Error no %s interface found" % intf))
        print(("Setup environnement '%s'" % context_cmd))
        ret = os.system("%s %s %s" % (context_cmd, "up", intf) )
        if ret:
            return False
    return True


def ecu_process(intf, end, test, lock):
    ctx = context.create_ctx (channel = intf,
                      bustype = BusType.SOCKETCAN,
                      bitrate = 0,
                      canid_recv = 0x10,
                      canid_send = 0x10,
                      timeout = 2,
                      trace = 1)
    check = 0
    lock.acquire()
    while not end.value:
        if check != 3:
            ret, msg = vcan.read (ctx)
            if msg is None:
                continue
            else:
                data = list(msg.data)
                # Generate an ECU response
                if data == [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]:
                    print ("OK received single frame")
                    msg = can.Message(data =  [0x30, 0x02, 0x14])
                    vcan.write (ctx, msg, 0x10)
                    check += 1
                elif data == [0x10, 0x0B, 0x27,0x02,0x01,0x02,0x03,0x04]:
                    print ("OK received Multiple frame (part 1)")
                    msg = can.Message(data =  [0x30, 0x01, 0x14])
                    vcan.write (ctx, msg, 0x10)
                    check += 1
                elif data == [0x21,0x05,0x06,0x07,0x08,0x09,0x00,0x00]:
                    print ("OK received Multiple frame (part 2)")
                    msg = can.Message(data =  [0x30, 0x01, 0x14])
                    vcan.write (ctx, msg, 0x10)
                    check += 1
            continue
        else:
            lock.release()
            time.sleep(1)
            print ("ECU send ISO TP start")
            vcan.write (ctx, can.Message(data = [0x10, 0x0B, 0x27, 0x02,0x01,0x02,0x03,0x04]))
            vcan.write (ctx, can.Message(data = [0x21,0x05,0x06,0x07,0x08,0x09,0x00, 0x00]))
            break


def write_process(intf, is_isotp, end, auto_end, test, lock, queue):
    '''Process to write to CAN interface

    :param intf: the socket can interface
    :param is_isotp: to indicate if the write is at isotp stack level
    :param end: the flag to indicate the end of the process
    :param auto_end: the flag to indicate that the process auto stop the
                     test when all data have been written
    :param test: the flag to indicate the end of the test
    :param lock: RFU
    :param queue: the queue to exchange data
    '''
    write_ctx = context.create_ctx (channel = intf,
                            bustype = BusType.SOCKETCAN,
                            bitrate = 0,
                            canid_recv = 0,
                            canid_send = 0,
                            timeout = 2,
                            trace = 1)
    while not end.value:
        if test.value:
            if not queue.empty():
                for d in queue.get():
                    if is_isotp:
                        context.set_canid_send (write_ctx, d[0])
                        isotp.write (write_ctx, d[1:])
                    else:
                        msg = can.Message(data =  d[1:])
                        vcan.write (write_ctx, msg, can_id=d[0])
                    time.sleep(0.01)
                if auto_end:
                    test.value = False
            else:
                time.sleep(1)
        else:
            time.sleep(1)


def read_process(intf, is_isotp, end, auto_end, test, lock, queue):
    '''Process to read to CAN interface

    :param intf: the socket can interface
    :param is_isotp: to indicate if the write is at isotp stack level
    :param end: the flag to indicate the end of the process
    :param auto_end: RFU
    :param test: the flag to indicate the end of the test
    :param lock: RFU
    :param queue: the queue to exchange data
    '''
    read_ctx = context.create_ctx (channel = intf,
                           bustype = BusType.SOCKETCAN,
                           bitrate = 0,
                           canid_recv = 0,
                           canid_send = 0,
                           timeout = 1,
                           trace = 1)
    while not end.value:
        if test.value:
            read_data = []
            while True:
                if is_isotp:
                    ret, msg = isotp.read (read_ctx)
                else:
                    ret, msg = vcan.read (read_ctx)
                if msg is None:
                    break
                else:
                    data = [msg.arbitration_id] + list(msg.data)
                    read_data.append(list(data))
            if read_data:
                queue.put(read_data)
        else:
            time.sleep(1)


def load_testfile(path):
    '''Load the CAN values as a list of lists'''
    cans = []
    f = open(path, "r")
    for l in f.readlines():
        l = l.strip().split(' ')
        l = l[2]
        l = l.strip().split('#')
        it = iter(l[1])
        res = [int(l[0], 16)] + [int(a+b, 16) for a,b in zip(it, it)]
        cans.append(list(res))
    f.close()
    return cans
