#!/usr/bin/env python2

from array import array
import os, time
import json
import unittest
from tests_tools import *
import scripts.gw_calibration_tools as cal

calibration_file = "./tests/data/gw_calibration_test1.json"
calibration_data = {}

class TestCalibration(unittest.TestCase):

    def test_01(self):
        self.assertEqual(True,
                         cal.calibration_matches
                         (calibration_data, "ext", "v1", 0x020, [0x02, 0x10, 0x01]))

    def test_02(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "ext", "v2", 0x020, [0x02, 0x10, 0x01]))

    def test_03(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "dlc", "v1", 0x020, [0x02, 0x10, 0x01]))
    def test_04(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "ext", "dlc", 0x10, [0x02, 0x10, 0x01]))

    def test_05(self):
        self.assertEqual(True,
                         cal.calibration_matches
                         (calibration_data, "chassis", "dlc", 0x704, [0x02, 0x10, 0x01]))

    def test_06(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "chassis", "v1", 0x704, [0x02, 0x10, 0x01]))

    def test_07(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "dlc", "ext", 0x704, [0x02, 0x10, 0x01]))

    def test_08(self):
        self.assertEqual(True,
                         cal.calibration_matches
                         (calibration_data, "dlc", "pt", 0xA0, [0x02, 0x10, 0xC0]))

    def test_09(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "dlc", "pt", 0xA0, [0x02, 0x10, 0x02]))

    def test_10(self):
        self.assertEqual(False,
                         cal.calibration_matches
                         (calibration_data, "dlc", "pt", 0xA0, [0x10, 0x10, 0xC0]))

if __name__ == '__main__':
    # Load the calibration file
    with open(calibration_file) as f:
        calibration_data = json.load(f)
    unittest.main(exit=False)
    
    
