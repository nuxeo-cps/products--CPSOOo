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
from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CPSCore.interfaces import ICPSSite


ModuleSecurityInfo('copy').declarePublic('deepcopy')

imports_ok = True
try:
    # Trying all the not usual imports on which CPSOOo relies
    import xml.dom.minidom
    import xml.dom.ext
    try:
        from elementtree.ElementTree import ElementTree
    except ImportError:
        from lxml.etree import ElementTree
except ImportError, err:
    LOG(log_key, PROBLEM,
        "CPSOOo cannot be loaded because there are some dependencies missing: "
        "%s" % str(err))
    imports_ok = False

if imports_ok:
    import Field
    from Products.CPSOOo.OOoDocbookDocument import \
         OOoDocbookDocument, addOOoDocbookDocumentInstance

    fti = ()
    contentClasses = (OOoDocbookDocument,)
    contentConstructors = (addOOoDocbookDocumentInstance,)

    registerDirectory('skins', globals())

    def initialize(registrar):
        ContentInit('CPSOOo Types',
                    content_types=contentClasses,
                    permission=AddPortalContent,
                    extra_constructors=contentConstructors,
                    fti=fti,
                    ).initialize(registrar)
    profile_registry.registerProfile(
        'default',
        'CPS OOo',
        "CPSOOo product for CPS.",
        'profiles/default',
        'CPSOOo',
        EXTENSION,
        for_=ICPSSite)
