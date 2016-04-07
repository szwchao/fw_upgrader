# -*- coding: utf-8 -*-
import os
import sys
import re
import socket
import threading
import logging
from .lib.progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, RotatingMarker
from .firmware import Firmware_Downloader, warning, info

py3 = sys.version_info[0] >= 3
if py3:
    from .lib.tftpy import setLogLevel, TftpServer
else:
    from .lib.tftpy2 import setLogLevel, TftpServer


class MyError(Exception):
    pass


def fw_upgrader(path, server_ip, client_ip, route_ip=None, timeout=10, web_response_timeout=20, reboot=True, loglevel=logging.NOTSET):
    setLogLevel(loglevel)
    route_ip = route_ip if route_ip else server_ip
    checkip(server_ip)
    checkip(client_ip)
    info("server ip: %s" % (server_ip))
    info("controller ip: %s" % (client_ip))
    if route_ip is not server_ip:
        info("route ip: %s" % (route_ip))

    f = Firmware_Downloader(url=client_ip, server_ip=route_ip, response_timeout=web_response_timeout)
    info('old firmware version is: ' + f.get_version())

    widgets = ['transferring: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=3670000).start()

    server = TftpServer(path, hook=pbar.update)
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
            info('new firmware version is: ' + f.get_version())
        else:
            info('download complete, please reboot!')
    finally:
        server.stop(now=False)
        server_thread.join()


def checkip(ip):
    if not re.match('^(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])$', ip):
        raise MyError('not a valid ip address!')


def guess_local_ip():
    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip


def guess_eth1_ip():
    ip = None
    local_ip = guess_local_ip()
    ip_list = socket.gethostbyname_ex(socket.gethostname())
    lst = [l for l in ip_list if local_ip in l][0]
    for i in lst:
        if i.startswith('192.168.'):
            ip = i
    return ip
