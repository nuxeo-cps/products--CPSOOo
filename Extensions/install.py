# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com/>
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

"""
CPSOOo Installer

Howto use the CPSOOo installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpsooo_install (or whatever)
     title         : CPSOOo Install (or whatever)
     Module Name   : CPSOOo.install
     Function Name : install

 - save it
 - then click on the test tab of this external method
"""

from Products.CPSOOo.Field import CPSOOoDocbookFileField

from Products.CPSOOo.document_structures import \
    getDocumentTypes, getDocumentSchemas, getDocumentLayouts

from Products.CPSCore.CPSWorkflow import \
     TRANSITION_BEHAVIOR_FREEZE, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_DELETE, TRANSITION_ALLOWSUB_MOVE, \
     TRANSITION_ALLOWSUB_COPY

from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from Products.PythonScripts.PythonScript import PythonScript

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CMFCore.CMFCorePermissions import \
     View, ModifyPortalContent, ManageProperties
WebDavLockItem = 'WebDAV Lock items'
WebDavUnlockItem = 'WebDAV Unlock items'

LAYERS = {
    'cpsooo': 'Products/CPSOOo/skins/cpsooo',
    }

class ClientInstaller(CPSInstaller):

    product_name = 'CPSOOo'

    def install(self):
        """Converting a CPS Default Site to a client site"""
        self.log("Starting %s installation" % self.product_name)

        self.log("Installing layers and configure Basic skin")
        self.verifySkins(LAYERS)

        self.log("Installing custom types")
        custom_types = getDocumentTypes(self.portal)
        self.log("custom types = %s" % str(custom_types))
        self.verifyFlexibleTypes(custom_types)

        self.log("Installing custom schemas")
        custom_schemas = getDocumentSchemas(self.portal)
        self.log("custom schemas = %s" % str(custom_schemas))
        self.verifySchemas(custom_schemas)

        self.log("Installing custom layouts")
        custom_layouts = getDocumentLayouts(self.portal)
        self.verifyLayouts(custom_layouts)

        self.allowContentTypes('OOoDocbookDocument', ('Workspace', 'Section'))

        ########################################
        #   WORKFLOW ASSOCIATIONS
        ########################################
        ws_chains = { 'OOoDocbookDocument': 'workspace_content_wf' }
        se_chains = { 'OOoDocbookDocument': 'section_content_wf' }

        self.verifyLocalWorkflowChains(self.portal['workspaces'],
                                       ws_chains)
        self.verifyLocalWorkflowChains(self.portal['sections'],
                                       se_chains)

        self.setupTranslations()

        self.log("Ending %s installation" % self.product_name)


def install(self):
    """Installation function for use by a Zope External Method

    @return: C{None}
    @rtype: C{None}

    @param self: CPSPortal Linked by External Method
    @type self: L{CPSDefaultSite}
    """

    installer = ClientInstaller(self)

    installer.install()

    return installer.logResult()
