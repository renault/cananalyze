#!/usr/bin/env python3
'''
This script provide informations about Security Access service
'''

import sys
import argparse
import cananalyze.scan as scan
import cananalyze.context as context
import cananalyze.diag_session as session
import cananalyze.security_access as sa
import cananalyze.uds as uds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="analyze SA service")
    parser.add_argument("channel", help="\"A\", \"B\", \"vcanX\" depending if bustype is komodo or socketcan")
    parser.add_argument("bustype", help="\"komodo\",  \"socketcan\", ... ")
    parser.add_argument("canid_recv", help="canid recv")
    parser.add_argument("canid_send", help="canid send")
    parser.add_argument("scanType", help="Scan type (len or seeds)")
    args = parser.parse_args()


    ctx = context.create_ctx (channel = args.channel,
                              bustype = args.bustype,
                              port_nr = 0,
                              bitrate = 500000,
                              canid_recv =int(args.canid_recv,16),
                              canid_send =int(args.canid_send,16),
                              timeout = 1,
                              extended = context.Ctx.ExtendedMode.FORCED_NOT_EXTENDED)


    if ctx == None: 
        context.output("Error occured during create_ctx") 
        sys.exit (-1)
    
    session.pause_tester_present(ctx)
    session.start(ctx, 0x1, False )
    session.start(ctx, 0x2, False )
   
    nsa = 1

    if (args.scanType == 'len'):
        challenges = list()
        for kSize in range(0,40):
            err, data = sa.request_seed(ctx,nsa)
            uds.write (ctx, [0x27, nsa + 1] + [0] * kSize)
            err, data = uds.read (ctx, "sa_send_key", 0x27)
            
            if (err == -2):
                challenges.append([kSize, uds.nrc_string(data)])

        for challenge in challenges:
            print("Size = %02x, NRC = %s" % (challenge[0], challenge[1]))
    
    elif (args.scanType == 'seeds'):
        seeds = list()
        for i in range(0,100):
            err, data = sa.request_seed(ctx,0x1)
            if data != None and len(data) > 2:
                seeds.append(data[2:])
        
        for seed in seeds:
            print(''.join(format(x, '02x') for x in seed))
    else:
        print("Invalid scan mode")


