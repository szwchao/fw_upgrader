# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import time
import socket

if sys.version_info < (2, 7):
    raise RuntimeError('At least Python 2.7 is required')
try:  # python2
    from urllib import urlencode as urlencode
    import urllib2 as request
except ImportError:  # python3
    from urllib.parse import urlencode as urlencode
    import urllib.request as request

# Constants from the Windows API
STD_OUTPUT_HANDLE = -11
FOREGROUND_RED = 0x000c  # text color contains red.
FOREGROUND_GREEN = 0x0002  # text color contains dark green.


def get_csbi_attributes(handle):
    # Based on IPython's winconsole.py, written by Alexander Belchenko
    import struct
    csbi = ctypes.create_string_buffer(22)
    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
    assert res

    (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
    return wattr

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
reset = get_csbi_attributes(handle)


def info(str):
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, FOREGROUND_GREEN)
    print(str)
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, reset)


def warning(str):
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, FOREGROUND_RED)
    print(str)
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, reset)


class FwError(Exception):

    def __init__(self, message):
        self.message = message


class Firmware_Downloader(object):
    username = 'admin'
    cmd = {'form_id': 'firmware_update', 'reboot_value': '', 'tftp_server_ip_address': '192.168.0.1', 'submit': 'Start', 'reboot': 'Reboot'}

    def __init__(self, url=None, server_ip='192.168.0.1', response_timeout=20, password='admin'):
        self.password = password
        self.response_timeout = response_timeout
        # self.url = url if url else self.guess_ip()
        self.url = "http://" + url
        self.cmd['tftp_server_ip_address'] = server_ip

    def auth(self, url):
        p = request.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, self.username, self.password)
        handler = request.HTTPBasicAuthHandler(p)
        opener = request.build_opener(handler)
        request.install_opener(opener)

    def post(self, posturl, params):
        '''
            do the POST action of form in html

        :param posturl: POST url
        :param params: dict to orgnize the parameters that needed in post action
        :return:
        '''
        # self.auth(posturl)
        data = urlencode(params)
        binary_data = data.encode('utf-8')
        req = request.Request(posturl, binary_data)
        response = request.urlopen(req, timeout=self.response_timeout)

    def get(self, url):
        '''
            do the GET action of form in html

        :param url: GET url
        :return:
        '''
        self.auth(url)
        return request.urlopen(url, timeout=self.response_timeout).read()

    def guess_ip(self):
        begin_ip = "http://192.168.0."
        found = False
        for i in range(0, 256):
            if found:
                break
            url = begin_ip + str(i) + "/firmware_update.html"
            self.auth(url)
            try:
                result = request.urlopen(url, timeout=1).read()
                found = True
            except:
                found = False
        if found:
            url = begin_ip + str(i - 1)
            info("found correct ip: %s" % url)
        else:
            raise FwError("can't find controller's ip")
        return url

    def get_version(self):
        url = self.url + "/firmware_update.html"
        result = self.get(url)
        # '<div style="border-bottom:2px solid #D3D3D3; padding:0px 0px 5px 0px; margin-bottom:15px"><a href="index.html">Home</a> &middot; <a href="firmware_update.html">Firmware</a> &middot; <small>v03.17.00, compiled:&nbsp;Feb  4 2016/09:10:31<br/></small></div>'
        compiled_index = result.index(b"compiled")
        version = result[compiled_index - 11:compiled_index - 2]
        # info(version)
        return version.decode('utf-8')

    def wait(self, timeout=300):
        '''
            wait the download procedure complete

        :param timeout: timeout of download procedure
        :return:
        '''
        start_time = time.time()
        geturl = self.url + "/get.cgi?firmware_update=status"
        current_time = time.time()
        result = self.get(geturl)
        while b'SUCCESS' not in result and (current_time - start_time) < timeout:
            if b'ERROR' in result:
                warning("something error, can't download firmware!!!")
                raise FwError(result)
            time.sleep(5)
            current_time = time.time()
            result = self.get(geturl)
            # info(result)

        if (current_time - start_time) >= timeout:
            raise FwError("Timeout!!!")

        # info("Download complete, elapsed time: %ds" % (current_time-start_time))

    def download(self):
        # auth this url to connect firstly, otherwise post timeout
        url = self.url + "/firmware_update.html"
        self.auth(url)
        posturl = self.url + "/post.cgi"
        download_cmd = self.cmd
        self.post(posturl, download_cmd)

    def reboot(self):
        ''' send reboot command to controller '''
        posturl = self.url + "/post.cgi"
        reboot_cmd = self.cmd
        reboot_cmd['reboot_value'] = 'do_it'
        try:
            self.post(posturl, reboot_cmd)
        except:
            # after reboot, controller will lost response
            warning("rebooting...")

    def confirm(self):
        ''' Poll request from url after reboot to confirm that firmware upgrade is complete.  '''
        start_time = time.time()
        eplapsed_time = start_time
        while (eplapsed_time - start_time) < 120:
            geturl = self.url + "/get.cgi?firmware_update=status"
            try:
                result = self.get(geturl)
            except:
                result = b"error"
            finally:
                if b"idle" in result.lower():
                    info("download successful!!!")
                    break
            eplapsed_time = time.time()

    def get_dhcp(self):
        geturl = self.url + "/ipconfig.html"
        result = self.get(geturl)
        if b'DHCP status:</td>\r\n  <td width="25px"> </td>\r\n  <td>Enabled' in result:
            print("DHCP enabled")
        else:
            print("DHCP disabled")
        return result


def firmware_download(server, client):
    f = Firmware_Downloader(url=client, server_ip=server)
    # f.get_version()
    # f.download()
    # f.wait()
    # f.reboot()
    # f.confirm()
    f.get_dhcp()


if __name__ == '__main__':
    # get local ip
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    # local_ip = s.getsockname()[0]
    # print(local_ip)
    # firmware_download('192.168.0.1', '10.208.32.125')
    firmware_download('192.168.0.1', '192.168.0.2')
