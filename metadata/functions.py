#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from utils import io, text


def ls(file_path):
    output = io.run_process(['mdls', file_path])
    # get metadata into list, allowing for nested attributes
    md = [[y.strip()
           for y in line.split('=')]
          for line in output]
    listed_item = []
    md_dict = {}
    # iterate over list to deal with nested attributes
    # then build dictionary
    for item in md:
        if len(item) == 2:
            k, v = item
            # if second item is parens, then first is key
            if v == '(':
                listed_key = text.clean_key(k)
            # else, it's a simple `key: value` pair
            else:
                # attempt to convert to `int`
                try:
                    val = int(v)
                except (ValueError, TypeError):
                    val = v.replace('"', '')
                # convert shell nulls to Python `None`
                if val in ('""', '(null)'):
                    val = None
                key = text.clean_key(k)
                md_dict[key] = val
        # single item is part of a nested attribute
        elif len(item) == 1 and item[0] != ')':
            value = item[0].replace('"', '')
            listed_item.append(value)
        # single item marks end of a nested attribute
        elif len(item) == 1 and item[0] == ')':
            md_dict[listed_key] = listed_item
            listed_item = []
    return md_dict


def find(query_expression, only_in=None):
    cmd = ['mdfind']
    # add option to limit search scoe
    if only_in:
        cmd.append('-onlyin')
        cmd.append(only_in)
    # convert `query_expression` into file metadata query expression syntax
    query = "'" + query_expression.format() + "'"
    cmd.append(query)
    # run `mdfind` command as shell string, since otherwise it breaks
    #print(' '.join(cmd))
    return io.run_process(' '.join(cmd))


def write(file_path, tag_list, attr_name='kMDItemUserTags'):
    """Writes the list of tags to xattr field of `file_path`
    """
    tag_data = ['<string>{}</string>'.format(tag) for tag in tag_list]
    tag_data.insert(0, ('<!DOCTYPE plist PUBLIC'
                        '"-//Apple//DTD PLIST 1.0//EN"'
                        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
                        '<plist version="1.0"><array>'))
    tag_data.append('</array></plist>')
    tag_text = ''.join(tag_data)

    xattr = "com.apple.metadata:{}".format(attr_name)
    # Other attributes you might want to try:
    # ['kMDItemOMUserTags', 'kOMUserTags',
    #  'kMDItemkeywords', 'kMDItemFinderComment']
    cmd = ['xattr',
           '-w',
           xattr,
           tag_text.encode("utf8"),
           file_path]
    return io.run_process(cmd)


if __name__ == '__main__':
    pass
