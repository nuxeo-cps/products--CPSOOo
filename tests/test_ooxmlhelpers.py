# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from os.path import join, abspath, dirname
import xml.dom.minidom
from Products.CPSOOo.OOoDocbookDocument import iterDoc, toUnicode, \
     replaceKeywords, replaceBiblio


class TestOOXMLHelpers(unittest.TestCase):

    def _getExpectedResult(self, fname):
        s = open(join(abspath(dirname(__file__)), 'input', fname), 'r').read()
        doc = xml.dom.minidom.parseString(s)
        return doc

    def _getOriginalXML(self):
        return self._getExpectedResult('orig.xml')

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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOOXMLHelpers))
    return suite
