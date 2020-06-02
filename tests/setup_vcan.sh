#!/bin/bash

if [ $# -ne 2 ]
then
    echo "usage: setup_vcan up|down vcanX"
    exit 1
fi

modprobe can
modprobe can_raw
modprobe vcan

if [ "$1" = "up" ]
then
    echo "Add virtual CAN interface ${2}"
    ip link add dev ${2} type vcan
    ip link set up ${2}
else
    echo "Remove virtual CAN interface ${2}"
    ip link set down ${2}
    ip link del dev ${2}
fi
