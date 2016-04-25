# -*- coding: utf-8 -*-
import os
import logging
import argparse
from src.fw_upgrader import fw_upgrader, guess_local_ip

__VERSION__ = "0.3"


def main(args):
    if args.server:
        server_ip = args.server
    else:
        server_ip = guess_local_ip()
    client_ip = args.controller
    route_ip = args.route_ip if args.route_ip else server_ip
    path = os.path.relpath(args.folder)

    if args.loglevel == 0:
        loglevel = logging.NOTSET
    elif args.loglevel == 1:
        loglevel = logging.INFO
    elif args.loglevel == 2:
        loglevel = logging.DEBUG
    fw_upgrader(path, server_ip, client_ip, route_ip, args.timeout, args.web_response_timeout, args.noreboot, loglevel, args.password)

if __name__ == '__main__':
    des = 'A tool used to download firmware to Cu3x2.'
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument('-v', '--version', action='version', version=__VERSION__)
    parser.add_argument('-p', '--password', type=str, default='admin', help='password for the Ethernet loggin')
    parser.add_argument('-f', '--folder', type=str, default='.', help='folder path to the directory which contains MPC folder and firmware bin file inside')
    parser.add_argument('-s', '--server', type=str, help='server ip')
    parser.add_argument('-r', '--route_ip', type=str, help='route ip, same as server ip if not set')
    parser.add_argument('-c', '--controller', type=str, help='controller ip', required=True)
    parser.add_argument('-l', '--loglevel', type=int, default=0, help='log level, 0=no log, 1=info, 2=debug')
    parser.add_argument('-t', '--timeout', type=int, default=20, help='timeout for tftp server, default=20s')
    parser.add_argument('-w', '--web_response_timeout', type=int, default=20, help='timeout for web response, default=20s')
    parser.add_argument('-n', '--noreboot', action='store_false', help='enable this to skip reboot')

    args = parser.parse_args()
    main(args)
