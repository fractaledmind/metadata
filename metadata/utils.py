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


ASCII_REPLACEMENTS = {
    'À': 'A',
    'Á': 'A',
    'Â': 'A',
    'Ã': 'A',
    'Ä': 'A',
    'Å': 'A',
    'Æ': 'AE',
    'Ç': 'C',
    'È': 'E',
    'É': 'E',
    'Ê': 'E',
    'Ë': 'E',
    'Ì': 'I',
    'Í': 'I',
    'Î': 'I',
    'Ï': 'I',
    'Ð': 'D',
    'Ñ': 'N',
    'Ò': 'O',
    'Ó': 'O',
    'Ô': 'O',
    'Õ': 'O',
    'Ö': 'O',
    'Ø': 'O',
    'Ù': 'U',
    'Ú': 'U',
    'Û': 'U',
    'Ü': 'U',
    'Ý': 'Y',
    'Þ': 'Th',
    'ß': 'ss',
    'à': 'a',
    'á': 'a',
    'â': 'a',
    'ã': 'a',
    'ä': 'a',
    'å': 'a',
    'æ': 'ae',
    'ç': 'c',
    'è': 'e',
    'é': 'e',
    'ê': 'e',
    'ë': 'e',
    'ì': 'i',
    'í': 'i',
    'î': 'i',
    'ï': 'i',
    'ð': 'd',
    'ñ': 'n',
    'ò': 'o',
    'ó': 'o',
    'ô': 'o',
    'õ': 'o',
    'ö': 'o',
    'ø': 'o',
    'ù': 'u',
    'ú': 'u',
    'û': 'u',
    'ü': 'u',
    'ý': 'y',
    'þ': 'th',
    'ÿ': 'y',
    'Ł': 'L',
    'ł': 'l',
    'Ń': 'N',
    'ń': 'n',
    'Ņ': 'N',
    'ņ': 'n',
    'Ň': 'N',
    'ň': 'n',
    'Ŋ': 'ng',
    'ŋ': 'NG',
    'Ō': 'O',
    'ō': 'o',
    'Ŏ': 'O',
    'ŏ': 'o',
    'Ő': 'O',
    'ő': 'o',
    'Œ': 'OE',
    'œ': 'oe',
    'Ŕ': 'R',
    'ŕ': 'r',
    'Ŗ': 'R',
    'ŗ': 'r',
    'Ř': 'R',
    'ř': 'r',
    'Ś': 'S',
    'ś': 's',
    'Ŝ': 'S',
    'ŝ': 's',
    'Ş': 'S',
    'ş': 's',
    'Š': 'S',
    'š': 's',
    'Ţ': 'T',
    'ţ': 't',
    'Ť': 'T',
    'ť': 't',
    'Ŧ': 'T',
    'ŧ': 't',
    'Ũ': 'U',
    'ũ': 'u',
    'Ū': 'U',
    'ū': 'u',
    'Ŭ': 'U',
    'ŭ': 'u',
    'Ů': 'U',
    'ů': 'u',
    'Ű': 'U',
    'ű': 'u',
    'Ŵ': 'W',
    'ŵ': 'w',
    'Ŷ': 'Y',
    'ŷ': 'y',
    'Ÿ': 'Y',
    'Ź': 'Z',
    'ź': 'z',
    'Ż': 'Z',
    'ż': 'z',
    'Ž': 'Z',
    'ž': 'z',
    'ſ': 's',
    'Α': 'A',
    'Β': 'B',
    'Γ': 'G',
    'Δ': 'D',
    'Ε': 'E',
    'Ζ': 'Z',
    'Η': 'E',
    'Θ': 'Th',
    'Ι': 'I',
    'Κ': 'K',
    'Λ': 'L',
    'Μ': 'M',
    'Ν': 'N',
    'Ξ': 'Ks',
    'Ο': 'O',
    'Π': 'P',
    'Ρ': 'R',
    'Σ': 'S',
    'Τ': 'T',
    'Υ': 'U',
    'Φ': 'Ph',
    'Χ': 'Kh',
    'Ψ': 'Ps',
    'Ω': 'O',
    'α': 'a',
    'β': 'b',
    'γ': 'g',
    'δ': 'd',
    'ε': 'e',
    'ζ': 'z',
    'η': 'e',
    'θ': 'th',
    'ι': 'i',
    'κ': 'k',
    'λ': 'l',
    'μ': 'm',
    'ν': 'n',
    'ξ': 'x',
    'ο': 'o',
    'π': 'p',
    'ρ': 'r',
    'ς': 's',
    'σ': 's',
    'τ': 't',
    'υ': 'u',
    'φ': 'ph',
    'χ': 'kh',
    'ψ': 'ps',
    'ω': 'o',
    'А': 'A',
    'Б': 'B',
    'В': 'V',
    'Г': 'G',
    'Д': 'D',
    'Е': 'E',
    'Ж': 'Zh',
    'З': 'Z',
    'И': 'I',
    'Й': 'I',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'У': 'U',
    'Ф': 'F',
    'Х': 'Kh',
    'Ц': 'Ts',
    'Ч': 'Ch',
    'Ш': 'Sh',
    'Щ': 'Shch',
    'Ъ': "'",
    'Ы': 'Y',
    'Ь': "'",
    'Э': 'E',
    'Ю': 'Iu',
    'Я': 'Ia',
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'i',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': "'",
    'ы': 'y',
    'ь': "'",
    'э': 'e',
    'ю': 'iu',
    'я': 'ia',
    # 'ᴀ': '',
    # 'ᴁ': '',
    # 'ᴂ': '',
    # 'ᴃ': '',
    # 'ᴄ': '',
    # 'ᴅ': '',
    # 'ᴆ': '',
    # 'ᴇ': '',
    # 'ᴈ': '',
    # 'ᴉ': '',
    # 'ᴊ': '',
    # 'ᴋ': '',
    # 'ᴌ': '',
    # 'ᴍ': '',
    # 'ᴎ': '',
    # 'ᴏ': '',
    # 'ᴐ': '',
    # 'ᴑ': '',
    # 'ᴒ': '',
    # 'ᴓ': '',
    # 'ᴔ': '',
    # 'ᴕ': '',
    # 'ᴖ': '',
    # 'ᴗ': '',
    # 'ᴘ': '',
    # 'ᴙ': '',
    # 'ᴚ': '',
    # 'ᴛ': '',
    # 'ᴜ': '',
    # 'ᴝ': '',
    # 'ᴞ': '',
    # 'ᴟ': '',
    # 'ᴠ': '',
    # 'ᴡ': '',
    # 'ᴢ': '',
    # 'ᴣ': '',
    # 'ᴤ': '',
    # 'ᴥ': '',
    'ᴦ': 'G',
    'ᴧ': 'L',
    'ᴨ': 'P',
    'ᴩ': 'R',
    'ᴪ': 'PS',
    'ẞ': 'Ss',
    'Ỳ': 'Y',
    'ỳ': 'y',
    'Ỵ': 'Y',
    'ỵ': 'y',
    'Ỹ': 'Y',
    'ỹ': 'y',
}


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


def clean_key(key):
    uid = key.replace('kMDItemFS', '')\
             .replace('kMDItem', '')\
             .replace('kMD', '')\
             .replace('com_', '')\
             .replace(' ', '')
    return convert_camel(uid)


if __name__ == '__main__':
    pass
