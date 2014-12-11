#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import utils


def find(query_expression, only_in=None):
    """Wrapper for OS X `mdfind` command.

    :param query_expression: file metadata query expression
    :type query_expression: :class:`MDExpression` object or
        :class:`MDComparison` object.
    :param only_in: limit search scope to directory tree path
    :type only_in: ``unicode``
    :returns: full paths to files of any results
    :rtype: ``list``

    """
    cmd = ['mdfind']
    # add option to limit search scoe
    if only_in:
        cmd.append('-onlyin')
        cmd.append(only_in)
    # convert `query_expression` into file metadata query expression syntax
    query = "'" + unicode(query_expression) + "'"
    cmd.append(query)
    # run `mdfind` command as shell string, since otherwise it breaks
    #print(' '.join(cmd))
    return utils.run_process(' '.join(cmd))


def list(file_path):
    """Wrapper for OS X `mdls` command.

    :param file_path: full path to file
    :type file_path: ``unicode``
    :returns: dictionary of metadata attributes and values
    :rtype: ``dict``

    """
    output = utils.run_process(['mdls', file_path])
    # get metadata into list, allowing for nested attributes
    md = [[y.strip()
           for y in line.split('=')]
          for line in output]
    # iterate over list to deal with nested attributes
    # then build dictionary
    listed_item, md_dict = [], {}
    for item in md:
        # item is pair
        if len(item) == 2:
            k, v = item
            # if second item is parens, then first is key
            if v == '(':
                listed_key = utils.clean_attribute(k)
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
                key = utils.clean_attribute(k)
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


def write(file_path, tag_list, attr_name='kMDItemUserTags'):
    """Writes the list of tags to xattr field of ``file_path``

    :param file_path: full path to file
    :type file_path: ``unicode``
    :param tag_list: values to write to attributes
    :type tag_list: ``list``
    :param attr_name: full name of OS X file metadata attribute
    :type attr_name: ``unicode``

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
    return utils.run_process(cmd)


if __name__ == '__main__':
    pass
