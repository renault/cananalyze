#!/usr/bin/env python3
"""
Unified Diagnostic Services : **Diagnostic Session module**

Start a diagnostic session control session.\n
Optionally run a background thread to check presence.

Implement :

* DiagnosticSessionControl
* TesterPresent
"""

import threading
import time

from . import context 
from . import uds


def __tester_present_daemon (ctx):
    while ctx.get_diag_session() != 1:
        if time.time() -  ctx.get_last_timestamp()  > 0.5:
            context.debug(2, "TesterPresent needed %lf\n" % (time.time() -  ctx.get_last_timestamp()))
            uds.write(ctx, [0x3e, 0])
            ctx.set_last_timestamp(time.time())
        else:
            context.debug(10, "TesterPresent not need")

        time.sleep (0.25)

def pause_tester_present (ctx):
    """Pause background thread to check presence
    :param ctx: application context
    """
    tester = ctx.get_diag_tester_thread()
    if tester != None:
        tester.stop()
        ctx.set_diag_tester_thread(None)

def resume_tester_present (ctx):
    """Resume background thread to check presence
    :param ctx: application context
    """
    tester = ctx.get_diag_tester_thread()
    if tester == None:
        tester = threading.Thread (target = __tester_present_daemon, args =  (ctx,))
        tester.start()
        ctx.set_diag_tester_thread(tester)

def start (ctx, session_nr, tester_present = True):
    """Switch to session numbered session-nr and keep sending
    TesterPresent packets if desired, depending on tester_present 
    parameter value
 
    :param ctx: application context
    :param session_nr: UDS session number
    :param tester_present: to activate TesterPresent thread
    :return: -1 if an error occured else 0
    """

    if -1 == uds.write (ctx, [0x10, session_nr]):
        return -1

    err, data = uds.read (ctx, "session", 0x10)
    if err == -1 or data == None:
        return -1

    if data [0] == 0x50:
        ctx.set_diag_session(session_nr)
        if tester_present:
            resume_tester_present(ctx)
        return 0
    else:
        context.output ("diagnostic session control: error occured")
    return -1
