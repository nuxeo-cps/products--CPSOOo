# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
import CPSOOoTestCase

class TestGlobalInstall(CPSOOoTestCase.CPSOOoTestCase):

    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    def testInstallerScript(self):
        from Products.ExternalMethod.ExternalMethod import ExternalMethod
        installer = ExternalMethod('cpsooo_installer', 'CPSOOo Install',
                                   'CPSOOo.install', 'install')
        self.portal._setObject('cpsooo_installer', installer)
        self.assert_('cpsooo_installer' in self.portal.objectIds())
        self.portal.cpsooo_installer()

    def testOOoDocbookDocumentPortalTypes(self):
        ttool = self.portal.portal_types
        self.failUnless('OOoDocbookDocument' in ttool.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGlobalInstall))
    return suite
