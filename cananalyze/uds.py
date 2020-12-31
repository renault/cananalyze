#!/usr/bin/env python3
"""
Unified Diagnostic Services module
"""

from . import context 
from . import isotp 

serivice_generic = {
    0x10: "Diagnostic Session Control",
    0x11: "ECU Reset",
    0x14: "Clear Diagnostic Information",
    0x19: "Read DTC Information",
    0x22: "Read Data By Identifier",
    0x23: "Read Memory By Address",
    0x24: "Read Scaling Data By Identifier",
    0x27: "Security Access",
    0x28: "Communication Control",
    0x2A: "Read Data By Periodic Identifier",
    0x2C: "Dynamically Define Data Identifier",
    0x2E: "Write Data By Identifier",
    0x2F: "Input Output Control By Identifier",
    0x31: "Routine Controle",
    0x34: "Request Donwload",
    0x35: "Request Upload",
    0x36: "Transfer Data",
    0x37: "Request Transfer Exit",
    0x38: "Request File Transfer",
    0x3D: "Write Memory By Address",
    0x3E: "Tester Present",
    0x83: "Access Timing Parameters",
    0x84: "Secured Data Transmission",
    0x85: "Control DTC Settings",
    0x86: "Response On Event",
    0x87: "Link Control"
}


nrc_generic = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subfunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x22: "conditionsNotCorrect",
    0x24: "requestSequenceError",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x35: "invalidKey",
    0x36: "exceededNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
    0x70: "uploadDownloadNotAccepted",
    0x71: "transferDataSuspended",
    0x72: "generalProgrammingFailure",
    0x73: "wrongBlockSequenceCounter",
    0x7e: "sub-functionNotSupportedInActiveSession",
    0x7f: "serviceNotSupportedInActiveSession",
    0x88: "vehiculeSpeedTooHigh",
    0x92: "voltageTooHigh",
    0x93: "voltageTooLow"
}

nrc = { 0x10: {}, 0x31: {},
        0x34: { 0x70:  "conditionsNotCorrectForDownload" },
        0x36: { 0x73: "wrongBlockSequenceCounter" }}
    
def read (ctx, func_name, sid, limit = 10):
    """Wait until ECU responds to SID request

    :param ctx: application context
    :param func_name: used for debugging purpose, as a prefix when an error message is printed
    :param sid: the SID request
    :param limit: seconds to wait for the given packet
    :return: error status (-1 = problem to read request, -2 =  UDS error, 0 = success), data
    """
    prc = sid + 0x40
    err78 = True
    while err78:
        err78 = False
        (err, data) = isotp.read (ctx, can_id = ctx.canid_recv(),
                                 mdata = [[0, 0x7f, sid], [0, prc], [0, 0, prc]],
                                 bitmask = [6, 2, 4], limit = limit)
        if err == -1 or data == None:
            context.output ( func_name + ": error or no response received to sid {0:#x} request".format (sid))
            return err, data

        if 0x7f == data [0] and 0x78 == data [2]:
            context.output ( func_name + ": Error 0x78 need to execute the request again".format (sid))
            err78 = True

    if 0x7f == data [0]:
        code = data [2]
        code_s = "unknown"
        if sid in nrc and code in nrc [sid]:
            code_s = nrc [sid][code]
        elif code in nrc_generic:
            code_s = nrc_generic [code]

        context.output ( func_name \
                + ": NRC received for sid %x (%s) with nrc %x (%s)"%(sid, 
                                                                              serivice_generic[sid] if sid in serivice_generic else "unkn", 
                                                                              code, 
                                                                              code_s))
        return -2, data
        
    return 0, data
    
def  write(ctx, data):
    """Data emission

    :param ctx: application context
    :param data: data buffer to write
    :return: -1 on error else 0
    """
    return isotp.write (ctx, data)
