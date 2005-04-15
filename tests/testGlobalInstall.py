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

class TestGlobalInstall(CPSOOoTestCase.CPSOOoTestCase):

    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    # CPSOOo is now installed by default so this doesn't work
    def XXXtestInstallerScript(self):
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
