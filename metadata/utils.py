#!/usr/bin/python
# encoding: utf-8
#
# Copyright © 2014 stephen.margheim@gmail.com
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 17-05-2014
#
from __future__ import unicode_literals

# Standard Library
import unicodedata
import subprocess
import os
import re


## Subprocess wrapper  --------------------------------------------------------

def run_process(cmd, stdin=None):
    # Is command shell string or list of args?
    shell = True
    if isinstance(cmd, list):
        shell = False
    # Set shell lang to UTF8
    os.environ['LANG'] = 'en_US.UTF-8'
    # Open pipes
    proc = subprocess.Popen(cmd,
                            shell=shell,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    # Run command, with optional input
    if stdin:
        (stdout, stderr) = proc.communicate(input=stdin.encode('utf-8'))
    else:
        (stdout, stderr) = proc.communicate()
    if '\\U' in stdout:
        stdout = stdout.replace('\\U', '\\u').decode('unicode-escape')
    # Convert newline delimited str into clean list
    output = filter(None, [s.strip()
                           for s in decode(stdout).split('\n')])
    if len(output) == 0:
        return None
    elif len(output) == 1:
        return output[0]
    else:
        return output


## Text Encoding  ---------------------------------------------------------

def decode(text, encoding='utf-8', normalization='NFC'):
    """Convert `text` to unicode

    """
    if isinstance(text, basestring):
        if not isinstance(text, unicode):
            text = unicode(text, encoding)
    return unicodedata.normalize(normalization, text)


## Text Formatting  -------------------------------------------------------

def convert_camel(camel_case):
    """Convert CamelCase to underscore_format."""
    camel_re = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    under = camel_re.sub(r'_\1', decode(camel_case)).lower()
    return under.replace('__', '_')


def clean_attribute(key):
    """Convert CamelCase to underscore_format

    :param key: name of OS X metadata attribute
    :type key: ``unicode`` or ``str``
    :returns: Pythonic attribute name

    """
    uid = key.replace('kMDItemFS', '')\
             .replace('kMDItem', '')\
             .replace('kMD', '')\
             .replace('com_', '')\
             .replace(' ', '')
    return convert_camel(uid)


if __name__ == '__main__':
    pass
