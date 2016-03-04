# -*- coding: utf-8 -*-

import os, sys, re
import socket
import threading
import tools.tftpy as tftpy
from tools.progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, RotatingMarker
import logging
import argparse
from fw import Firmware_Downloader
from tools.colorama import init
from tools.colorama import Fore, Back, Style

init(autoreset=True)

def comment(str):
    print(Fore.GREEN + str)

class MyError(Exception):
    pass

def run(server_ip, client_ip, timeout, web_response_timeout, reboot):
    f = Firmware_Downloader(url=client_ip, server_ip=server_ip, response_timeout = web_response_timeout)
    comment('Old firmware version is: ' + f.get_version())

    widgets = ['Transferring: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=3670000).start()

    server = tftpy.TftpServer('.', hook=pbar.update)
    server_thread = threading.Thread(target=server.listen, kwargs={'listenip': server_ip, 'listenport': 69, 'timeout': timeout})
    server_thread.start()
    try:
        server.is_running.wait()
        f.download()
        f.wait()
        pbar.finish()
        if reboot:
            f.reboot()
            f.confirm()
            comment('New firmware version is: ' + f.get_version())
        else:
            comment('Download complete, please reboot!')
    finally:
        server.stop(now=False)
        server_thread.join()

def checkip(ip):
    if not re.match('^(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])$', ip):
        raise MyError, 'Not a valid ip address!'

def guess_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    local_ip = s.getsockname()[0]
    return local_ip

def main(args):
    if args.server:
        server_ip = args.server
    else:
        server_ip = guess_local_ip()
    client_ip = args.controller
    checkip(server_ip)
    checkip(client_ip)

    comment("server ip: %s" % (server_ip))
    comment("controller ip: %s" % (client_ip))
    if not client_ip.startswith('http://'):
        client_ip = 'http://' + client_ip

    if args.loglevel == 0:
        tftpy.setLogLevel(logging.NOTSET)
    elif args.loglevel == 1:
        tftpy.setLogLevel(logging.INFO)
    elif args.loglevel == 2:
        tftpy.setLogLevel(logging.DEBUG)
    run(server_ip, client_ip, args.timeout, args.web_response_timeout, args.reboot)

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
