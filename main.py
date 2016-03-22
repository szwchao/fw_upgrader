# -*- coding: utf-8 -*-
import logging
import argparse
from src.fw_upgrader import fw_upgrader, guess_local_ip

def main(args):
    if args.server:
        server_ip = args.server
    else:
        server_ip = guess_local_ip()
    client_ip = args.controller

    if args.loglevel == 0:
        loglevel = logging.NOTSET
    elif args.loglevel == 1:
        loglevel = logging.INFO
    elif args.loglevel == 2:
        loglevel = logging.DEBUG
    fw_upgrader('.', server_ip, client_ip, args.timeout, args.web_response_timeout, args.noreboot, loglevel)

if __name__ == '__main__':
    des = 'a tool which can help to download firmware to DC'
    parser = argparse.ArgumentParser(description = des)
    parser.add_argument('-s', '--server', type=str, help='server ip')
    parser.add_argument('-c', '--controller', type=str, help='controller ip', required=True)
    parser.add_argument('-l', '--loglevel', type=int, default=0, help='log level, 0=no log, 1=info, 2=debug')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='timeout for tftp server')
    parser.add_argument('-w', '--web_response_timeout', type=int, default=20, help='timeout for web response')
    parser.add_argument('-r', '--noreboot', action='store_false', help='reboot controller if enable')
 
    args = parser.parse_args();
    main(args)
