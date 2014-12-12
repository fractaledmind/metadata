#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

__title__ = 'metadata'
__version__ = '0.4.1'
__author__ = 'Stephen Margheim'
__license__ = 'MIT'
__copyright__ = 'Copyright © 2014 Stephen Margheim'

import sys
import itertools

import utils
from functions import find, list, write
from classes import MDAttribute, MDComparison, MDExpression


def attributes_generator():
    """Generate dictionaries with data for all OS X metadata attributes

    :returns: data on all OS X metadata attributes
    :rtype: ``generator`` of ``dict``s

    """
    # get all OS X metadata attributes
    attributes = utils.run_process(['mdimport', '-A'])
    # prepare key names for the four columns
    keys = ('id', 'name', 'description', 'aliases')
    # create list of dicts, mapping ``keys`` to an item's columns
    for attribute in attributes:
        attribute_data = [item.replace("'", "")
                          for item in attribute.split('\t\t')]
        keyed_data = itertools.izip(keys, attribute_data)
        yield dict(keyed_data)

# dynamically generate module attribute objects
__module = sys.modules[__name__]
for __info in attributes_generator():
    __name = utils.clean_attribute(__info['id'])
    setattr(__module, __name, MDAttribute(__info))

# set ``attributes``, filtering out non metadata
attributes = [attr
              for attr in __module.__dict__.keys()
              if not attr.startswith('__')
              if not attr.startswith('MD')
              if not attr in ('find', 'list', 'write',
                              'utils', 'sys', 'itertools',
                              'unicode_literals')]


if __name__ == '__main__':
    pass
