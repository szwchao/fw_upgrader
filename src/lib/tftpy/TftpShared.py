"""This module holds all objects shared by all other modules in tftpy."""

import logging

LOG_LEVEL = logging.NOTSET
MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
TIMEOUT_RETRIES = 5
DEF_TFTP_PORT = 69

# Initialize the logger.
def setup_logger(logger_name, log_file=None, level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d]    %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    # l.addHandler(fileHandler)
    # l.addHandler(streamHandler)  

# Initialize the logger.
# logging.basicConfig(filename='log.log', filemode='w')
# The logger used by this library. Feel free to clobber it with your own, if you like, as
# long as it conforms to Python's logging.
setup_logger('tftpy')
# setup_logger('log2', r'C:\temp\log2.log')
log = logging.getLogger('tftpy')

def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException(msg)

def setLogLevel(level):
    """This function is a utility function for setting the internal log level.
    The log level defaults to logging.NOTSET, so unwanted output to stdout is
    not created."""
    if level != logging.NOTSET:
        formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d]    %(message)s')
        fileHandler = logging.FileHandler('tftpy.log', mode='w', encoding='UTF-8')
        fileHandler.setFormatter(formatter)
        log.addHandler(fileHandler)
    log.setLevel(level)

class TftpErrors(object):
    """This class is a convenience for defining the common tftp error codes,
    and making them more readable in the code."""
    NotDefined = 0
    FileNotFound = 1
    AccessViolation = 2
    DiskFull = 3
    IllegalTftpOp = 4
    UnknownTID = 5
    FileAlreadyExists = 6
    NoSuchUser = 7
    FailedNegotiation = 8

class TftpException(Exception):
    """This class is the parent class of all exceptions regarding the handling
    of the TFTP protocol."""
    pass

class TftpServerWriteMode(object):
    """This class defines the server write modes."""
    Overwrite = 0
    WriteNew = 1
    DenyWrite = 2
