# -*- coding: utf-8 -*-

import os, sys, re
import socket
import threading
import logging
from .lib.progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, RotatingMarker
from .firmware import Firmware_Downloader

py3 = sys.version_info[0] >= 3
if py3:
    from .lib.tftpy import setLogLevel, TftpServer 
else:
    from .lib.tftpy2 import setLogLevel, TftpServer 

def comment(str):
    print(str)

class MyError(Exception):
    pass

def fw_upgrader(path, server_ip, client_ip, timeout=10, web_response_timeout=20, reboot=True, loglevel=logging.NOTSET):
    setLogLevel(loglevel)
    checkip(server_ip)
    checkip(client_ip)
    comment("server ip: %s" % (server_ip))
    comment("controller ip: %s" % (client_ip))

    f = Firmware_Downloader(url=client_ip, server_ip=server_ip, response_timeout = web_response_timeout)
    comment('Old firmware version is: ' + f.get_version())

    widgets = ['Transferring: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
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
            comment('New firmware version is: ' + f.get_version())
        else:
            comment('Download complete, please reboot!')
    finally:
        server.stop(now=False)
        server_thread.join()

def checkip(ip):
    if not re.match('^(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])$', ip):
        raise MyError('Not a valid ip address!')

def guess_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    local_ip = s.getsockname()[0]
    return local_ip
