#!/usr/bin/env python

from distutils.core import setup

setup(
    name='progTiroc',
    version='1.0',
    description='',
    author='Enrico Soprana',
    author_email='esoprana@gmail.com',
    url='https://localhost/sigs/progTiroc/',
    packages=['progTiroc'],
    entry_points={'console_scripts': [
        'server = progTiroc:start_server'
        ]}
)

