# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
import CPSOOoTestCase
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
        doc = self._createOOoDocbookDoc()
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 1)
        self.ws._delObject(self.doc_id)
        self.assertEqual(len([o for o in self.ws.contentValues()
                              if o.getContent().meta_type == self.doc_type]), 0)
        self.failIf(hasattr(self.ws, self.doc_id))


    def testEditOOoDocbookDocument(self):
        doc = self._createOOoDocbookDoc()
        props = {
            'Title' : 'The title',
            'Description' : 'The description',
            }
        doc.edit(**props)

        for prop in props.keys():
            value = getattr(doc, prop.lower())
            self.assertEqual(str(value), str(props[prop]))

        # when changing at one metadata an putting 'file', file has precedence
        props = {
            'Title' : 'The title',
            'Description' : 'The description',
            'file' : self.file,
            }
        doc.edit(**props)
        self.assertEqual(str(getattr(doc, 'file')), str(self.file))
        self.assertEqual(doc.title, "Dix raisons d'utiliser OpenOffice.org")
        self.failIf(doc.description == props['Description'])


    def testExportXmlDocbook(self):
        doc = self._createOOoDocbookDoc()
        doc.edit(file=self.file)
        out = doc.exportXmlDocbook()

        resp = self.app.REQUEST.RESPONSE
        self.assertEqual(resp.headers['content-type'], 'application/zip')
        self.assertEqual(resp.headers['content-disposition'],
                         'filename=test.zip')

        res_archive = ZipFile(StringIO(out), 'r')
        arch_path = join(abspath(dirname(__file__)), 'output', 'test.zip')
        out_archive = ZipFile(arch_path, 'r')
        out_archive_nameslist = out_archive.namelist()

        for fname in res_archive.namelist():
            self.failUnless(fname in out_archive_nameslist)

        for fname in out_archive_nameslist:
            self.assertEqual(str(res_archive.read(fname)),
                             str(out_archive.read(fname)))

        self.assertEqual(len(out_archive.namelist()),
                         len(res_archive.namelist()))

    def _createOOoDocbookDoc(self):
        self.ws.invokeFactory(type_name = self.doc_type,
                              id = self.doc_id)
        return getattr(self.ws, self.doc_id).getContent()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOOoDocbookDocument))
    return suite
