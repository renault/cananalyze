#!/usr/bin/env python3

import time
from multiprocessing import Process, Lock, Value, Queue
import unittest
import tests_tools

intf = 'vcan0'

end_process = Value('i', False)
read_auto_end = Value('i', False)
write_auto_end = Value('i', False)
read_test = Value('i', False)
write_test = Value('i', False)
write_lock = Lock()
read_lock = Lock()
read_queue = Queue()
write_queue = Queue ()

class TestCan(unittest.TestCase):

    def test_simple(self):
        # Start the read process
        read_test.value = True
        # Send to the write process the data to write
        write_data = tests_tools.load_testfile('tests/data/test1.log')
        write_queue.put(write_data)
        # Wait a moment
        time.sleep(2)
        # Start write process
        write_test.value = True
        # Wait a moment
        time.sleep(2)
        # Stop write process
        write_test.value = False
        # Get the read data
        read_data = read_queue.get()
        # Stop the read process
        read_test.value = False
        self.assertEqual(read_data, write_data)

    def test_flood(self):
        # Start the read process
        read_test.value = True
        # Send to the write process the data to write
        write_auto_end.value = True
        write_data = tests_tools.load_testfile('tests/data/2018-11-08-DumpCANDiag-EXTRACT.log')
        write_queue.put(write_data)
        # Wait a moment
        time.sleep(2)
        # Start write process
        write_test.value = True
        # Wait for the end of the write process
        while write_test.value:
            time.sleep(2)
        # Wait for end of read
        time.sleep(4)
        # Get the read data
        read_data = read_queue.get()
        # Stop the read process
        read_test.value = False
        
        self.assertEqual(len(read_data), len(write_data))

if __name__ == '__main__':
    if tests_tools.check_context(intf):
        p = Process(target=tests_tools.read_process,
                    args=(intf, False, end_process, read_auto_end,
                          read_test, read_lock, read_queue,))
        q = Process(target=tests_tools.write_process,
                    args=(intf, False, end_process, write_auto_end,
                          write_test, write_lock, write_queue,))
        p.start()
        q.start()
        unittest.main(exit=False)

        # Stop threads
        end_process.value = True
        p.join()
        q.join()
