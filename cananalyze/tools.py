#!/usr/bin/env python3
"""
Generic tools module.

"""

def timestamp_to_ns (stamp, samplerate_khz):
    """TODO comment"""
    return (stamp * 1000 / (samplerate_khz / 1000))


def hex_array (array, l = -1):
    """Returns a printable hex array representation of l elements of array

    :param array: input byte array
    :param l: array length to process
    :return: printable hexadecimal array
    """
    if -1 == l:
        l = len (array)

    #str = "["
    str = ""
    for i in range(l):
        str = str + "0x{:02x},".format(array[i])

    #str = str[:-1] + "]"
    str = str[:-1]
    return str
    #return '['+','.join(map(hex, array[0:l])) +']'

def int_to_array (val, width):
    """Convert VAL to array type, considering it as a WIDTH-bytes integer

    :param val: input integer of width bytes
    :param width: size of val in bytes
    :return: array of bytes
    """
    ret = []
    for i in range (width):
        ret.append ((val & (0xff << (i * 8))) >> (i * 8))
    ret.reverse ()
    return ret

def array_to_int (array):
    """Convert array of bytes to an integer

    :param array: input array of bytes
    :return: integer value
    """
    ret, i = 0, 0
    for e in array:
        ret += e << ((len (array) - i - 1) * 8)
        i+= 1
    return ret

def equal_without_pad(r_send, r_receive):
    """Check if send and receives packets are equal

    :param r_send: input send packet
    :param r_receive: input receive packet
    :return: Boolean
    """
    result = True
    if len(r_send) > len(r_receive):
        result = False
    else:
        for i in range(len(r_send)):
            if r_send[i] != r_receive[i]:
                    result = False
    return result

def _match (a1, a2, bitmask = -1):
    i = 0
    if len (a1) != len (a2):
        return False

    if -1 == bitmask:
        return a1 == a2

    while bitmask:
        if bitmask & 1:
            if a1 [i] != a2 [i]: return False
        bitmask = bitmask >> 1
        i += 1

    return True

def match (mdata, data, bitmask = -1):
    """Check is data bytes correspond with mdata bytes regarding bitmask

    :param mdata: the data to match
    :param data: the input data
    :bitmask: gives a bitmask of indices of mdata bytes to compare with data
    """
    if not isinstance (mdata [0], list):
        return _match (mdata, data [0:len (mdata)], bitmask)

    for i in mdata:
        bm = bitmask [mdata.index (i)] if isinstance (bitmask, list) else bitmask
        if _match (i, data [0:len (i)], bm):
            return True
