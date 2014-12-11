#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 stephen.margheim@gmail.com
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on November 18, 2014
#
from __future__ import unicode_literals

import os
import sys
import unittest

if __name__ == '__main__':
    # add path to module root to `$PATH`
    root = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, root)

from metadata import attributes
from metadata import functions as md


def setUp():
    pass


def tearDown():
    pass


class MDTests(unittest.TestCase):

    def setUp(self):
        self.all_attributes = attributes.get_all_attributes()
        # `MDAttribute` objects
        tag_info = {'aliases': 'tag',
                    'name': 'Tags',
                    'id': 'kMDItemUserTags',
                    'description': 'Tags associated with this item'}
        self.attr1 = attributes.MDAttribute(tag_info,
                                            ignore_case=False,
                                            ignore_diacritics=False)
        self.attr2 = attributes.name
        self.attr3 = attributes.authors
        self.attr4 = attributes.content_type
        # `MDComparison` objects
        self.comp1 = (attributes.name == '*Blank*')
        self.comp2 = (attributes.authors == '*stark*')
        self.comp3 = (attributes.content_type == 'com.adobe.pdf')
        self.comp4 = (attributes.creator == 'python')
        # `MDExpression` objects
        self.exp1 = self.comp2 & self.comp1
        self.exp2 = self.comp1 | self.comp2
        self.exp3 = self.comp2 & (self.comp1 | self.comp3)
        self.exp4 = (self.comp1 | self.comp2) & (self.comp3 | self.comp4)
        # Test PDFs
        self.pdf_dir = os.path.dirname(__file__)
        self.blank_pdf = os.path.abspath('./blank.pdf')
        self.essay_pdf = os.path.abspath('./lorem_essay.pdf')
        self.visual_pdf = os.path.abspath('./lorem_visual.pdf')

    def tearDown(self):
        attributes.name.ignore_case = True
        attributes.name.ignore_diacritics = True

    #  ------------------------------------------------------------------------

    def test_attributes(self):
        self.assertFalse(self.attr1.ignore_case)
        # test module `MDAttribute` objects
        self.assertIsInstance(self.attr2, attributes.MDAttribute)
        self.assertIsInstance(self.attr3, attributes.MDAttribute)
        self.assertIsInstance(self.attr4, attributes.MDAttribute)

    def test_mdattribute_formatting(self):
        self.assertEqual(self.attr1.format(), 'kMDItemUserTags')
        self.assertEqual(self.attr2.format(), 'kMDItemFSName')
        self.assertEqual(self.attr3.format(), 'kMDItemAuthors')
        self.assertEqual(self.attr4.format(), 'kMDItemContentType')

    def test_mdcomparisons(self):
        self.assertIsInstance(self.comp1, attributes.MDComparison)
        self.assertIsInstance(self.comp2, attributes.MDComparison)
        self.assertIsInstance(self.comp3, attributes.MDComparison)

    def test_comparison_formatting(self):
        # test basic formatting
        self.assertEqual(self.comp1.format(), 'kMDItemFSName == "*Blank*"cd')
        # alter `MDComparison` object
        attributes.name.ignore_case = False
        comp1_1 = (attributes.name == '*Blank*')
        self.assertEqual(comp1_1.format(), 'kMDItemFSName == "*Blank*"d')
        # double alter `MDComparison` object
        attributes.name.ignore_case = False
        attributes.name.ignore_diacritics = False
        comp1_2 = (attributes.name == '*Blank*')
        self.assertEqual(comp1_2.format(), 'kMDItemFSName == "*Blank*"')

    def test_expressions(self):
        self.assertIsInstance(self.exp1, attributes.MDExpression)
        self.assertIsInstance(self.exp2, attributes.MDExpression)
        self.assertIsInstance(self.exp3, attributes.MDExpression)
        self.assertIsInstance(self.exp4, attributes.MDExpression)

    def test_expression_formatting(self):
        exp1 = ('kMDItemAuthors == "*stark*"cd'
                ' && kMDItemFSName == "*Blank*"cd')
        self.assertEqual(self.exp1.format(), exp1)
        exp2 = ('kMDItemFSName == "*Blank*"cd'
                ' || kMDItemAuthors == "*stark*"cd')
        self.assertEqual(self.exp2.format(), exp2)
        exp3 = ('kMDItemAuthors == "*stark*"cd'
                ' && (kMDItemFSName == "*Blank*"cd'
                ' || kMDItemContentType == "com.adobe.pdf"cd)')
        self.assertEqual(self.exp3.format(), exp3)
        exp4 = ('(kMDItemFSName == "*Blank*"cd'
                ' || kMDItemAuthors == "*stark*"cd)'
                ' && (kMDItemContentType == "com.adobe.pdf"cd'
                ' || kMDItemCreator == "python"cd)')
        self.assertEqual(self.exp4.format(), exp4)

    def test_find_blank(self):
        exp = self.comp1 & self.comp3
        blank_path = md.find(exp, only_in=self.pdf_dir)
        self.assertEqual(blank_path, [self.blank_pdf])

    def test_find_essay(self):
        essay_path = md.find(self.comp2, only_in=self.pdf_dir)
        self.assertEqual(essay_path, [self.essay_pdf])

    def test_find_visual(self):
        visual_path = md.find(self.comp4, only_in=self.pdf_dir)
        self.assertEqual(visual_path, [self.visual_pdf])

    def test_find_all(self):
        # test time comparisons
        comp = (attributes.creation_date >= '3 days ago')
        exp = comp & self.comp3
        paths = md.find(exp, only_in=self.pdf_dir)
        all_pdfs = [self.blank_pdf, self.visual_pdf, self.essay_pdf]
        self.assertEqual(sorted(paths), sorted(all_pdfs))

    def test_list_visual(self):
        meta = md.list(self.visual_pdf)
        logical_size = meta['logical_size']
        self.assertEqual(logical_size, 149385)

    def test_list_essay(self):
        meta = md.list(self.essay_pdf)
        author = meta['authors'][0]
        self.assertEqual(author, 'Tōnÿ Stårk')

    def test_list_blank(self):
        meta = md.list(self.blank_pdf)
        creation = meta['content_creation_date']
        self.assertEqual(creation, '2014-12-10 17:05:10 +0000')

if __name__ == '__main__':
    unittest.main()
