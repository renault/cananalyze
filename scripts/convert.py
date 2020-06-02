#!/usr/bin/env python3
import os
import sys
import time
import argparse

'''Sample script to convert CAN log files from format :

Hex CAN ID, Hex CAN DATA 1, Hex CAN DATA 2 ....
to 
can-tools utilities
'''
parser = argparse.ArgumentParser(description="convert CAN log files from format : \"Hex CAN ID, Hex CAN DATA 1 ...\" to can-tools utilitie")
parser.add_argument("srcfile", help="file to convert")
parser.add_argument("dstfile", help="ouput file")
args = parser.parse_args()


cans = []
f = open(args.srcfile, "r")
for l in f.readlines():
    l = l.strip().split(',')
    ldata = list([int(x, 0) for x in l])
    cans.append(list(ldata))
    f.close()

f = open(args.dstfile, "w")
for l in cans:
    line="(%f) can0 %03X#" % (time.time(), l[0])
    for e in l[1:]:
        line += "%02X" % e
    line += "\n"
    f.write(line)
f.close()

