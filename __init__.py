# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" Init """

from Products.CPSOOo.OOoDocbookDocument import \
     OOoDocbookDocument, addOOoDocbookDocumentInstance

from Products.CPSSchemas.ExtendedWidgets import CPSTextWidget

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

from AccessControl import ModuleSecurityInfo

import AllowModules

#import CookieLogger

from zLOG import LOG, INFO, DEBUG

logKey = 'CPSOOo.__init__'

# Removing the 'stx' render format as it is not wanted
if 'stx' in CPSTextWidget.all_render_formats:
    index = CPSTextWidget.all_render_formats.index('stx')
    del CPSTextWidget.all_render_formats[index]

ModuleSecurityInfo('copy').declarePublic('deepcopy')

contentClasses = (
    OOoDocbookDocument,
    )

contentConstructors = (
    addOOoDocbookDocumentInstance,
    )

fti = ()

registerDirectory('skins', globals())

def initialize(registrar):
    ContentInit('CPSOOo Types',
                content_types = contentClasses,
                permission = AddPortalContent,
                extra_constructors = contentConstructors,
                fti = fti,
                ).initialize(registrar)

##     registrar.registerClass(CookieLogger.CookieLogger,
##                       constructors=(CookieLogger.manage_addCLForm,
##                                     CookieLogger.manage_addCL,))
