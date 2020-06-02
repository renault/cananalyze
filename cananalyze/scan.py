import sys
import threading
import time
import can

import cananalyze.abstract_can as vcan
import cananalyze.uds as uds
import cananalyze.diag_session as session
import cananalyze.data_by_identifier as dbi
import cananalyze.context as context
from cananalyze.tools import *

def routines (ctx):
    """Probe implemented routines by analyzing error codes returned when we stop a routine not started.
    :param ctx: application context
    :return: list of discovered routines
    """

    lroutines = list()
    for i in range (0x10000):
        context.output ("scan.routines: probing for %x" % i)
        if -1 == uds.write (ctx, [0x31, 0x03, (i & 0xff00) >> 8, i & 0xff]):
            context.output ("scan.routines: Error writing request")
            return lroutines

        (r, d) = uds.read (ctx, "scan.routines", 0x31)
        if r == -2:
            context.debug(1, "scan.routines: NRC receive for %04x id routine : %02x " % (i, d[2]))
            if d[2] == 0x24:
                lroutines.append(i)

    for r in lroutines:
        context.output ("scan.routines detected with %04x " % (r) )


    return lroutines

def services (ctx, rge = list(range(0xbf))):
    """Probe implemented services by analyzing error codes returned when we send UDS request.
    :param ctx: application context
    :param rge: list of services to scan
    :return: list of discovered services
    """
    lservices = list()
    for i in rge:
        time.sleep(0.01)
        if -1 == uds.write (ctx, [i]):
            context.output ("scan.services: Error writing UDS request")
            return lservices
        (e, d) = uds.read (ctx, "scan.services", i)

        if -1 == e or ( e == -2 and d[2] == 0x11 ):
            continue
        lservices.append(i)

    for i in lservices:
        name = "unknown"
        if i in uds.serivice_generic:
            name = uds.serivice_generic[i]

        context.output ("scan.services discovered %x %s " %(i, name) )
    return lservices

def services_sessions(ctx):
    """Probe implemented sessions for each session by analyzing error codes returned when we start a new session.
    :param ctx: application context
    :return: list of discovered services [service, session, Tru == Protected by SA]
    """

    lresult   = list ()
    lservices = services(ctx)
    lsessions = sessions(ctx)

    for i in lsessions:
        while session.start(ctx, i, False) != 0:
            context.output("scan.services_sessions: Try again to start a  session")

        for j in lservices:
            if -1 == uds.write (ctx, [j]):
                context.output("scan.services_sessions: Error writing request")
                return lresult
            (e, d) = uds.read (ctx, "scan.services", j)

            if e == -1 or ( e == -2 and d[2] == 0x11 ):
                continue

            if  e == - 2 and ( d[2] == 0x7e or d[2] == 0x7f ):
                context.output ("scan.services_sessions: INFO " + hex(j) + " in session " + hex(i) + " NOT" )
            elif  e == - 2 and d[2] == 0x33:
                context.output ("scan.services_sessions: INFO " + hex(j) + " in session " + hex(i) + " SA")
                lresult.append([j , i, True])
            else:
                context.output ("scan.sessions_sessions: INFO " + hex(j) + " in session " + hex(i) + " OK")
                lresult.append([j , i, False])
    return lresult

def sessions (ctx):
    """Probe implemented sessions  by analyzing error codes returned when we start a new session.
    :param ctx: application context
    :return: list of discovered sessions
    """
    lsessions = list()
    for i in range (0xFF):
        if -1 == uds.write (ctx, [0x10, i]):
            context.output ("scan.sessions: Error to write UDS request")
            return lsessions

        (err, data) = uds.read (ctx, "scan.sessions", 0x10)
        
        if err == -1 or ( err == -2 and data[2] == 0x12 ):
            continue
        
        lsessions.append(i)
        time.sleep(0.001)        

    for i in lsessions:
        context.output ("scan.sessions discovered %x " % i )
    return lsessions

def dbis (ctx, rge = list(range(0xffff))):
    """Read all dbi for a specific range.
    :param ctx: application context
    :rge: list of dbi to read
    """
    for i in rge:
        dbi.read (ctx, i) 
      


