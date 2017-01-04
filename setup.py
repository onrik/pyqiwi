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
        'httpretty'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
