#!/usr/bin/env python3
'''
This script detects the UDS services (before executing the script you must change the CANid)
'''

import sys
import argparse
import cananalyze.scan as scan
import cananalyze.context as context
import cananalyze.diag_session as session

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="detect the UDS services")
    parser.add_argument("channel", help="\"A\", \"B\", \"vcanX\" depending if bustype is komodo or socketcan")
    parser.add_argument("bustype", help="\"komodo\",  \"socketcan\", ... ")
    parser.add_argument("canid_recv", help="canid recv")
    parser.add_argument("canid_send", help="canid send")
    parser.add_argument("scanType", help="Scan type (sessions or services)")
    parser.add_argument("--count", help="the number of packets to get")
    args = parser.parse_args()



    ctx = context.create_ctx (channel = args.channel,
                              bustype = args.bustype,
                              port_nr = 0,
                              bitrate = 500000,
                              canid_recv =int(args.canid_recv,16),
                              canid_send =int(args.canid_send,16),
                              timeout = 1)
    if ctx == None: 
        context.output("Error occured during create_ctx") 
        sys.exit (-1)
    session.pause_tester_present(ctx)


    if (args.scanType == 'sessions'):
        scan.sessions(ctx)
    elif (args.scanType == 'services'):
        scan.services(ctx)
    elif (args.scanType == 'dbis'):
        scan.dbis(ctx)
    else:
        print("Invalid scan mode")
