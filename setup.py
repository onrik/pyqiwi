#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pyqiwi import __version__

setup(
    name='pyqiwi',
    version=__version__,
    author='Andrey',
    author_email='and@rey.im',
    description='Client for QIWI payment system',
    license='MIT',
    url='https://github.com/onrik/pyqiwi',
    packages=['pyqiwi'],
    test_suite='tests',
    tests_require=[
        'mock'
    ],
)
