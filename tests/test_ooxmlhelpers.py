# (C) Copyright 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Ruslan Spivak (Nuxeo)
# M.-A. Darche (Nuxeo)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from os.path import join, abspath, dirname
import xml.dom
import xml.dom.minidom
from Products.CPSOOo.OOoDocbookDocument import iterDoc, toUnicode, \
     replaceKeywords, replaceBiblio, replaceTextElementsByStyleName, \
     replaceCopyright


def docorder_iter_filter(node, filter_func, **kw):
    if filter_func(node, **kw):
        yield node
    for child in node.childNodes:
        for cn in docorder_iter_filter(child, filter_func, **kw):
            yield cn
    return

class TestOOXMLHelpers(unittest.TestCase):

    def _getExpectedResult(self, fname):
        s = open(join(abspath(dirname(__file__)), 'input', fname), 'r').read()
        doc = xml.dom.minidom.parseString(s)
        return doc

    def _getOriginalXML(self):
        return self._getExpectedResult('orig.xml')

    def _getElementsByStyleName(self, doc, style_name):
        stylename_filter = lambda node, style_name='': \
            (node.nodeType == xml.dom.Node.ELEMENT_NODE and
             style_name == node.getAttribute('text:style-name'))
        return list(docorder_iter_filter(doc, stylename_filter,
                                         style_name=style_name))

    def test_replaceKeywords(self):
        doc = self._getOriginalXML()
        expected = self._getExpectedResult('replacekeywords.xml')
        iter_context = {
            'keywords' : [toUnicode(k) for k in ['Nuxeo', 'CPS', 'Zope']]
            }
        iterDoc(doc, replaceKeywords, iter_context)
        self.assertEqual(doc.toxml(), expected.toxml(), 'Results do not match')

    def test_replaceBiblio(self):
        doc = self._getOriginalXML()
        expected = self._getExpectedResult('replacebiblio.xml')
        iter_context = {
            'bibliorelation' : [toUnicode('http://www.indesko.com')]
            }
        iterDoc(doc, replaceBiblio, iter_context)
        self.assertEqual(doc.toxml(), expected.toxml(), 'Results do not match')

    def test_replaceTextElementsByStyleName(self):
        doc = self._getOriginalXML()
        iter_context = {
            'textnodes': (
                ('text:p', 'text:style-name', 'Title',
                 toUnicode('The Title')),
                ('text:p', 'text:style-name', 'Abstract',
                 toUnicode('The Abstract')),
                ('text:p', 'text:style-name', 'Bibliocoverage',
                 toUnicode('The Bibliocoverage')),
                ('text:p', 'text:style-name', 'Bibliosource',
                 toUnicode('The Bibliosource')),
                ),
            }
        title_elements = self._getElementsByStyleName(doc, 'Title')
        self.assertEqual(len(title_elements), 8)

        abstract_elements = self._getElementsByStyleName(doc, 'Abstract')
        self.assertEqual(len(abstract_elements), 1)

        bibliocoverage_elements = self._getElementsByStyleName(doc,
                                                               'Bibliocoverage')
        self.assertEqual(len(bibliocoverage_elements), 1)

        bibliosource_elements = self._getElementsByStyleName(doc,
                                                             'Bibliosource')
        self.assertEqual(len(bibliosource_elements), 1)

        iterDoc(doc, replaceTextElementsByStyleName, iter_context)

        title_elements = self._getElementsByStyleName(doc, 'Title')
        self.assertEqual(len(title_elements), 1)

        node = self._getElementsByStyleName(doc, 'Title')[0]
        text_val = node.firstChild.nodeValue
        self.assertEqual(text_val, 'The Title')

        node = self._getElementsByStyleName(doc, 'Abstract')[0]
        text_val = node.firstChild.nodeValue
        self.assertEqual(text_val, 'The Abstract')

        node = self._getElementsByStyleName(doc, 'Bibliocoverage')[0]
        text_val = node.firstChild.nodeValue
        self.assertEqual(text_val, 'The Bibliocoverage')

        node = self._getElementsByStyleName(doc, 'Bibliosource')[0]
        text_val = node.firstChild.nodeValue
        self.assertEqual(text_val, 'The Bibliosource')


    def test_replaceCopyright(self):
        doc = self._getOriginalXML()
        iter_context = {
            'copyright': 'The Copyright',
            'year': 'year 2004',
            'holder': 'Indesko Nuxeo',
            }
        iterDoc(doc, replaceCopyright, iter_context)

        copyright_node = self._getElementsByStyleName(doc, 'Copyright')[0]
        copyrights =  copyright_node.firstChild.nodeValue
        self.assertEqual(copyrights, iter_context['copyright'] + ' ')

        # 'Year' node is inside 'Copyright'
        node = self._getElementsByStyleName(copyright_node, 'Year')[0]
        year = node.firstChild.nodeValue
        self.assertEqual(year, iter_context['year'])

        # 'Holder' node is inside 'Copyright'
        node = self._getElementsByStyleName(copyright_node, 'Holder')[0]
        year = node.firstChild.nodeValue
        self.assertEqual(year, iter_context['holder'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOOXMLHelpers))
    return suite
