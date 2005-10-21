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
import CPSOOoTestCase
from difflib import unified_diff
from os.path import join, abspath, dirname
from zipfile import ZipFile
from StringIO import StringIO
from OFS.Image import File

class TestOOoDocbookDocument(CPSOOoTestCase.CPSOOoTestCase):

    def afterSetUp(self):
        self.doc_type = 'OOoDocbookDocument'
        self.doc_id = self.doc_type.lower()
        self.login('manager')
        self.ws = self.portal.workspaces

        f = open(join(abspath(dirname(__file__)), 'input', 'test.sxw'), 'rb')
        self.file = File('test', 'test.sxw', f)
        self.file.content_type = 'application/vnd.sun.xml.writer'
        f.close()

    def beforeTearDown(self):
        self.logout()

    def testAddOOoDocbookDocument(self):
        """Test creation of OOoDocbookDocument instance in root of workspaces.
        """
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 0)
        self.ws.invokeFactory(type_name = self.doc_type,
                              id = self.doc_id)
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 1)
        self.assert_(hasattr(self.ws, self.doc_id))

        doc = getattr(self.ws, self.doc_id).getContent()
        self.assertEqual(doc.title, '')


    def testRemoveOOoDocbookDocument(self):
        """Test removal of OOoDocbookDocument instance in root of workspaces.
        """
        proxy, doc = self._createOOoDocbookDoc()
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 1)
        self.ws._delObject(self.doc_id)
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 0)
        self.failIf(hasattr(self.ws, self.doc_id))


    def testEditOOoDocbookDocument(self):
        proxy, doc = self._createOOoDocbookDoc()
        props = {
            'Title' : 'The title',
            'Description' : 'The description',
            }
        doc.edit(proxy=proxy, **props)

        for prop in props.keys():
            value = getattr(doc, prop.lower())
            self.assertEqual(str(value), str(props[prop]))

        # when changing at one metadata an putting 'file', file has precedence
        props = {
            'Title' : 'The title',
            'Description' : 'The description',
            'file' : self.file,
            }
        doc.edit(proxy=proxy, **props)
        self.assertEqual(str(getattr(doc, 'file')), str(self.file))
        self.assertEqual(doc.title, "Dix raisons d'utiliser OpenOffice.org")
        self.failIf(doc.description == props['Description'])


    def testExportXmlDocbook(self):
        proxy, doc = self._createOOoDocbookDoc()
        doc.edit(proxy=proxy, file=self.file)
        out = doc.exportXmlDocbook()

        resp = self.app.REQUEST.RESPONSE
        self.assertEqual(resp.headers['content-type'], 'application/zip')
        self.assertEqual(resp.headers['content-disposition'],
                         'filename=test.zip')

        res_archive = ZipFile(StringIO(out), 'r')
        res_archive_entries_count = len(res_archive.namelist())

        arch_path = join(abspath(dirname(__file__)), 'output', 'test.zip')
        out_archive = ZipFile(arch_path, 'r')
        out_archive_nameslist = out_archive.namelist()
        out_archive_entries_count = len(out_archive_nameslist)

        self.assertEqual(res_archive_entries_count,
                         out_archive_entries_count,
                         ("Input has %s entries "
                          "while output has %s entries")
                         % (res_archive_entries_count,
                            out_archive_entries_count))

        for fname in res_archive.namelist():
            self.failUnless(fname in out_archive_nameslist,
                            "File %s is not present in output"
                            % fname)

        for fname in out_archive_nameslist:
            res_content = str(res_archive.read(fname))
            out_content = str(out_archive.read(fname))
            diff = unified_diff(res_content.split('\n'),
                                out_content.split('\n'))
            msg = "Input and output content does not match for file %s: %s"%(
                fname, '\n'.join(diff))
            self.assertEqual(res_content, out_content, msg)

    def _createOOoDocbookDoc(self):
        self.ws.invokeFactory(type_name = self.doc_type,
                              id = self.doc_id)
        proxy = getattr(self.ws, self.doc_id)
        return proxy, proxy.getEditableContent()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOOoDocbookDocument))
    return suite
