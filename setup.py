#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import os
import sys
import codecs

import metadata

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = ['parsedatetime']

with codecs.open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=metadata.__title__,
    version=metadata.__version__,
    description='Python wrapper for OS X `mdfind`.',
    long_description=readme,
    author='Stephen Margheim',
    author_email='stephen.margheim@gmail.com',
    url='https://github.com/smargh/metadata',
    packages=['metadata'],
    install_requires=requires,
    license='MIT'
)
