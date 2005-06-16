# (C) Copyright 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche (Nuxeo)
# Ruslan Spivak (Nuxeo)
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
""" Init """

log_key = 'CPSOOo.__init__'

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.permissions import AddPortalContent
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, \
     TRACE, DEBUG, BLATHER, INFO, PROBLEM, WARNING, ERROR, PANIC

ModuleSecurityInfo('copy').declarePublic('deepcopy')

# Register field classes
import Field


fti = ()

imports_ok = True
try:
    from elementtree.ElementTree import ElementTree
    from Products.CPSOOo.OOoDocbookDocument import \
         OOoDocbookDocument, addOOoDocbookDocumentInstance

    contentClasses = (OOoDocbookDocument,)
    contentConstructors = (addOOoDocbookDocumentInstance,)

except ImportError:
    LOG(log_key, PROBLEM,
        "CPSOOo cannot be loaded because the elementtree module is missing")
    imports_ok = False

registerDirectory('skins', globals())
if imports_ok:
    def initialize(registrar):
        ContentInit('CPSOOo Types',
                    content_types=contentClasses,
                    permission=AddPortalContent,
                    extra_constructors=contentConstructors,
                    fti=fti,
                    ).initialize(registrar)
