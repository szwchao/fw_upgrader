"""
This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.

As a client of tftpy, this is the only module that you should need to import
directly. The TftpClient and TftpServer classes can be reached through it.
"""

import sys


from .TftpShared import *
from .TftpPacketTypes import *
from .TftpPacketFactory import *
from .TftpClient import *
from .TftpServer import *
