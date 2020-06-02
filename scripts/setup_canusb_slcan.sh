#!/bin/bash

# param1 = ttyUSB
# param2 = slcan

if [ $# -ne 2 ]
then
    echo "usage: $0 /dev/ttyUSBx vcanx"
    exit 1
fi

sudo modprobe can
sudo modprobe can_raw
sudo modprobe slcan

sudo slcand -o -c -f -s6 ${1} ${2}

ip addr

sudo ifconfig ${2} up

ip addr
