# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" Init """

log_key = 'CPSOOo.__init__'

from zLOG import LOG, \
     TRACE, DEBUG, BLATHER, INFO, PROBLEM, WARNING, ERROR, PANIC

try:
    from elementtree.ElementTree import ElementTree

    from Products.CPSOOo.OOoDocbookDocument import \
         OOoDocbookDocument, addOOoDocbookDocumentInstance

    from Products.CPSSchemas.ExtendedWidgets import CPSTextWidget

    from Products.CMFCore.utils import ContentInit
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore.CMFCorePermissions import AddPortalContent

    from AccessControl import ModuleSecurityInfo

    import AllowModules

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
except ImportError:
    LOG(log_key, PROBLEM,
        "CPSOOo cannot be loaded because the elementtree module is missing")


def initialize(registrar):
    try:
        from elementtree.ElementTree import ElementTree

        ContentInit('CPSOOo Types',
                    content_types = contentClasses,
                    permission = AddPortalContent,
                    extra_constructors = contentConstructors,
                    fti = fti,
                    ).initialize(registrar)
    except ImportError:
        LOG(log_key, PROBLEM,
            "CPSOOo cannot be loaded because the elementtree module is missing")
