# coding: utf-8
from client import Qiwi, QiwiError


def get_version():
    return '.'.join(map(str, VERSION))

VERSION = (0, 1, 0)
__version__ = get_version()
