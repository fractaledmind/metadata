#!/usr/bin/python
# encoding: utf-8
from __future__ import unicode_literals

import unicodedata
import subprocess
import os
import re


## Subprocess wrapper  --------------------------------------------------------

def run_process(cmd, stdin=None):
    """Run ``cmd`` in shell

    :param cmd: shell command to be run
    :type cmd: ``unicode`` or ``list``
    :param stdin: input data for shell command
    :type stdin: ``unicode``
    :returns: normalized list of output
    :rtype: ``list``

    """
    # is command shell string or list of args?
    shell = True
    if isinstance(cmd, list):
        shell = False
    # set shell lang to UTF8
    os.environ['LANG'] = 'en_US.UTF-8'
    # open pipes
    proc = subprocess.Popen(cmd,
                            shell=shell,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    # Run command, with optional input
    if stdin:
        stdout, stderr = proc.communicate(input=decode(stdin).encode('utf-8'))
    else:
        stdout, stderr = proc.communicate()
    # Convert newline delimited str into clean list
    output = filter(None, [s.strip()
                           for s in decode(stdout).split('\n')])
    return output


## Text Encoding  ---------------------------------------------------------

def decode(text, encoding='utf-8', normalization='NFC'):
    """Return ``text`` as normalised unicode.

    :param text: string
    :type text: encoded or Unicode string. If ``text`` is already a
        Unicode string, it will only be normalised.
    :param encoding: The text encoding to use to decode ``text`` to
        Unicode.
    :type encoding: ``unicode`` or ``None``
    :param normalization: The nomalisation form to apply to ``text``.
    :type normalization: ``unicode`` or ``None``
    :returns: decoded and normalised ``unicode``

    """
    # convert string to Unicode
    if isinstance(text, basestring):
        if not isinstance(text, unicode):
            text = unicode(text, encoding)
    # decode Cocoa/CoreFoundation Unicode to Python Unicode
    if re.search(r'\\U\d{3,}', text):
        text = text.replace('\\U', '\\u').decode('unicode-escape')
    return unicodedata.normalize(normalization, text)


## Text Formatting  -------------------------------------------------------

def convert_camel(camel_case):
    """Convert CamelCase to underscore_format

    :param camel_case: string in CamelCase format
    :type camel_case: ``unicode`` or ``str``
    :returns: string in under_score format

    """
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
    var = b'To\U0304ny\U0308 Sta\U030ark'
    print(decode(var).encode('utf-8'))
