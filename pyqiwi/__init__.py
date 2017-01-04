# coding: utf-8
from __future__ import absolute_import, unicode_literals
from .client import Qiwi, QiwiError


def get_version():
    return '.'.join(map(str, VERSION))

VERSION = (0, 2, 0)
__version__ = get_version()
