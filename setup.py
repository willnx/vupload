#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(name="vupload",
      author="Nicholas Willhite",
      version='0.0.1',
      packages=find_packages(),
      description="A CLI tool for VMware's InitiateFileTransferToGuest",
      entry_points={'console_scripts' : 'vupload=vupload.script:main'},
      install_requires=['vlab-inf-common'],
      )
