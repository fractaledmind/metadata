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
import metadata
from metadata import functions as md
from metadata import MDAttribute, MDComparison, MDExpression


def setUp():
    pass


def tearDown():
    pass


class MDTests(unittest.TestCase):

    def setUp(self):
        # `MDAttribute` objects
        tag_info = {'aliases': '(null)',
                    'name': 'Example Attribute',
                    'id': 'kMDItemExampleAttribute',
                    'description': 'This is a test attribute'}
        self.attr1 = MDAttribute(tag_info,
                                 ignore_case=False,
                                 ignore_diacritics=False)
        self.attr2 = metadata.name
        self.attr3 = metadata.authors
        self.attr4 = metadata.content_type
        # `MDComparison` objects
        self.comp1 = (metadata.name == '*Blank*')
        self.comp2 = (metadata.authors == '*stark*')
        self.comp3 = (metadata.content_type == 'com.adobe.pdf')
        self.comp4 = (metadata.creator == 'python')
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
        metadata.name.ignore_case = True
        metadata.name.ignore_diacritics = True

    #  ------------------------------------------------------------------------

    def test_attributes(self):
        self.assertFalse(self.attr1.ignore_case)
        # test module `MDAttribute` objects
        self.assertIsInstance(self.attr2, MDAttribute)
        self.assertIsInstance(self.attr3, MDAttribute)
        self.assertIsInstance(self.attr4, MDAttribute)

    def test_mdattribute_formatting(self):
        self.assertEqual(unicode(self.attr1), 'kMDItemExampleAttribute')
        self.assertEqual(unicode(self.attr2), 'kMDItemFSName')
        self.assertEqual(unicode(self.attr3), 'kMDItemAuthors')
        self.assertEqual(unicode(self.attr4), 'kMDItemContentType')

    def test_mdcomparisons(self):
        self.assertIsInstance(self.comp1, MDComparison)
        self.assertIsInstance(self.comp2, MDComparison)
        self.assertIsInstance(self.comp3, MDComparison)

    def test_comparison_formatting(self):
        # test basic formatting
        self.assertEqual(unicode(self.comp1), 'kMDItemFSName == "*Blank*"cd')
        # alter `MDComparison` object
        metadata.name.ignore_case = False
        comp1_1 = (metadata.name == '*Blank*')
        self.assertEqual(unicode(comp1_1), 'kMDItemFSName == "*Blank*"d')
        # double alter `MDComparison` object
        metadata.name.ignore_case = False
        metadata.name.ignore_diacritics = False
        comp1_2 = (metadata.name == '*Blank*')
        self.assertEqual(unicode(comp1_2), 'kMDItemFSName == "*Blank*"')

    def test_expressions(self):
        self.assertIsInstance(self.exp1, MDExpression)
        self.assertIsInstance(self.exp2, MDExpression)
        self.assertIsInstance(self.exp3, MDExpression)
        self.assertIsInstance(self.exp4, MDExpression)

    def test_expression_formatting(self):
        exp1 = ('kMDItemAuthors == "*stark*"cd'
                ' && kMDItemFSName == "*Blank*"cd')
        self.assertEqual(unicode(self.exp1), exp1)
        exp2 = ('kMDItemFSName == "*Blank*"cd'
                ' || kMDItemAuthors == "*stark*"cd')
        self.assertEqual(unicode(self.exp2), exp2)
        exp3 = ('kMDItemAuthors == "*stark*"cd'
                ' && (kMDItemFSName == "*Blank*"cd'
                ' || kMDItemContentType == "com.adobe.pdf"cd)')
        self.assertEqual(unicode(self.exp3), exp3)
        exp4 = ('(kMDItemFSName == "*Blank*"cd'
                ' || kMDItemAuthors == "*stark*"cd)'
                ' && (kMDItemContentType == "com.adobe.pdf"cd'
                ' || kMDItemCreator == "python"cd)')
        self.assertEqual(unicode(self.exp4), exp4)

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
        comp = (metadata.creation_date >= '3 days ago')
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
