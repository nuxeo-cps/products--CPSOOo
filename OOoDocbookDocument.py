# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
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

import re
import os
import os.path
import shutil
import tempfile
import xml.dom.minidom
import xml.dom.ext
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from zipfile import BadZipfile
from cStringIO import StringIO


from Globals import InitializeClass
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from OFS.Image import File

from Products.CMFCore.CMFCorePermissions import View
from Products.CPSDocument.CPSDocument import CPSDocument

from App.Common import rfc1123_date

from elementtree.ElementTree import XML, ElementTree, Element, SubElement
from elementtree.ElementPath import findall as xpath_findall
from elementtree.ElementPath import find as xpath_find

from zLOG import LOG, \
     TRACE, DEBUG, BLATHER, INFO, PROBLEM, WARNING, ERROR, PANIC

logKey = 'OOoDocbookDocument'

def toLatin9(s):
    if s is None:
        return None
    else:
        # Replace RIGHT SINGLE QUOTATION MARK (unicode only)
        # bythe APOSTROPHE (ascii and latin1).
        # cf. http://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
        s = s.replace(u'\u2019', u'\u0027')
        #&#8217;
        return s.encode('iso-8859-15', 'ignore')

def toUnicode(s):
    return unicode(s, 'iso-8859-15')

def mktempdir():
    """Make a temporary directory, returns its filename."""
    fd, filename = tempfile.mkstemp(suffix='dir')
    os.close(fd)
    os.unlink(filename)
    os.mkdir(filename, 0700)
    return filename

def findFirstText(inElement, elementName):
    elts = xpath_findall(inElement, elementName)
    text = ''
    for elt in elts:
        if elt.text:
            text = toLatin9(elt.text)
            break
    return text

def findText(inElement, elementName):
    elt = xpath_find(inElement, elementName)
    if elt is not None:
        text = toLatin9(elt.text)
    else:
        text = ''
    return text

def iterDoc(parent_node, func, iter_context):
    """Iterate on all element nodes of a document

    Calls func for each node, passing it an iteration context.
    """
    for node in parent_node.childNodes:
        #print node.nodeName
        if node.nodeType != xml.dom.Node.ELEMENT_NODE:
            continue
        func(node, iter_context)
        iterDoc(node, func, iter_context)

def replaceTextElements(node, iter_context):
    """Replace text elements."""
    document = node.ownerDocument

    for nodename, attr, attrval, newval in iter_context['textnodes']:
##         LOG(logKey, DEBUG, "nodename = %s" % repr(nodename))
##         LOG(logKey, DEBUG, "attr = %s" % repr(attr))
##         LOG(logKey, DEBUG, "attrval = %s" % repr(attrval))
##         LOG(logKey, DEBUG, "newval = %s" % repr(newval))
        if node.nodeName != nodename:
            continue
        if node.getAttribute(attr) != toUnicode(attrval):
            continue

        done = attrval + '_done'
        if iter_context.get(done):
            # remove spurious additional element
            node.parentNode.removeChild(node)
        else:
            # replace existing
            iter_context[done] = 1

            # Remove all children (old text nodes, maybe none)
            for n in list(node.childNodes):
                node.removeChild(n)

            # Add new text child
            node.appendChild(document.createTextNode(newval))

def replaceTextElementsByStyleName(node, iter_context):
    """Replace text elements."""
    document = node.ownerDocument

    for nodename, attr, style_name, newval in iter_context['textnodes']:
##         LOG(logKey, DEBUG, "nodename = %s" % repr(nodename))
##         LOG(logKey, DEBUG, "attr = %s" % repr(attr))
##         LOG(logKey, DEBUG, "style_name = %s" % repr(style_name))
##         LOG(logKey, DEBUG, "newval = %s" % repr(newval))
        style_name = toUnicode(style_name)
        if node.nodeName != nodename:
            continue
        node_style_name = node.getAttribute(attr)
        if not (node_style_name == style_name
                or nodeParentStyleNameMatchesStyleName(node, style_name)):
            continue

        done = style_name + '_done'
        if iter_context.get(done):
            # remove spurious additional element
            node.parentNode.removeChild(node)
        else:
            # replace existing
            iter_context[done] = 1

            # Remove all children (old text nodes, maybe none)
            for n in list(node.childNodes):
                node.removeChild(n)

            # Add new text child
            node.appendChild(document.createTextNode(newval))


def nodeParentStyleNameMatchesStyleName(node, style_name):
    document = node.ownerDocument
    node_style_name = node.getAttribute('text:style-name')
    automaticStylesElt = document.getElementsByTagName('office:automatic-styles')[0]
    styleElts = automaticStylesElt.getElementsByTagName('style:style')
    for styleElt in styleElts:
        automatic_style_name = styleElt.getAttribute('style:name')
        parent_style_name = styleElt.getAttribute('style:parent-style-name')
        LOG(logKey, DEBUG, "node_style_name = %s" % repr(node_style_name))
        LOG(logKey, DEBUG, "automatic_style_name = %s" % repr(automatic_style_name))
        LOG(logKey, DEBUG, "parent_style_name = %s" % repr(parent_style_name))
        if (node_style_name == automatic_style_name
            and parent_style_name == style_name):
            LOG(logKey, DEBUG, "True for style_name = %s" % repr(style_name))
            return True
    return False


def replaceKeywords(node, iter_context):
    if node.nodeName != 'text:p':
        return
    if node.getAttribute('text:style-name') != toUnicode('Mots clés'):
        return

    document = node.ownerDocument

    # remove existing
    for n in list(node.childNodes):
        node.removeChild(n)

    keywords = iter_context['keywords']
    nb = len(keywords)
    n = 0
    for k in keywords:
        n += 1
        span_node = document.createElement('text:span')
        span_node.setAttribute('text:style-name', toUnicode('Mot clé'))
        span_node.appendChild(document.createTextNode(k))
        node.appendChild(span_node)
        if n != nb:
            node.appendChild(document.createTextNode(', '))


def replaceContributors(contributors, document):
    LOG(logKey, DEBUG, "contributors = %s" % str(contributors))
    officeBodyElt = document.getElementsByTagName('office:body')[0]
    paraElts = officeBodyElt.getElementsByTagName('text:p')
    for elt in paraElts:
        if elt.getAttribute('text:style-name') == 'Contributeur':
            officeBodyElt.removeChild(elt)
        if (elt.getAttribute('text:style-name') == 'Heading'
            and elt.hasChildNodes()
            and elt.childNodes[0].nodeValue == 'Contributeurs'):
            officeBodyElt.removeChild(elt)

    contributorsCount = len(contributors)
    if contributorsCount == 0:
        return

    # Then let's add the new Contributeur elements after the Title, Author or
    # Authorblurb elements if we find any.
    officeBodyEltElts = officeBodyElt.childNodes
    whereElt = None
    for elt in officeBodyEltElts:
        if elt.getAttribute('text:style-name') == 'Title':
            whereElt = elt
        if elt.getAttribute('text:style-name') == 'Author':
            whereElt = elt
        if elt.getAttribute('text:style-name') == 'Authorblurb':
            whereElt = elt
        if elt.getAttribute('text:style-name') == 'Source':
            whereElt = elt
        if elt.getAttribute('text:style-name') == 'Relation':
            whereElt = elt
            break

    headingCreditElt = document.createElement('text:p')
    headingCreditElt.setAttribute('text:style-name', 'Heading')
    headingCreditElt.appendChild(document.createTextNode("Contributeurs"))
    if whereElt is None:
        officeBodyElt.appendChild(headingCreditElt)
    else:
        # In insertBefore(Node newChild, Node refChild) if refChild is null,
        # it inserts newChild at the end of the list of children.
        officeBodyElt.insertBefore(headingCreditElt, whereElt.nextSibling)

    # It is needed to reverse the list so that the insertion in the DOM keeps
    # the contributors in the same order as they were specified in the
    # OOo document.
    contributors.reverse()
    for k in contributors:
        pElt = document.createElement('text:p')
        pElt.setAttribute('text:style-name', 'Contributeur')
        officeBodyElt.insertBefore(pElt, headingCreditElt.nextSibling)

        # Here we only want to split the contributor's fullname in 2 parts
        fullname = k.split(None, 1)
        LOG(logKey, DEBUG, "fullname = %s" % str(fullname))
        if fullname:
            if len(fullname) == 2:
                firstname = fullname[0]
                surname = fullname[1]
            else:
                firstname = ""
                surname = fullname[0]

            LOG(logKey, DEBUG, "firstname = %s" % firstname)
            LOG(logKey, DEBUG, "surname = %s" % surname)
            if firstname:
                spanElt = document.createElement('text:span')
                spanElt.setAttribute('text:style-name', 'Firstname')
                spanElt.appendChild(document.createTextNode(firstname))
                pElt.appendChild(spanElt)
                pElt.appendChild(document.createTextNode(' '))
            if surname:
                spanElt = document.createElement('text:span')
                spanElt.setAttribute('text:style-name', 'Surname')
                spanElt.appendChild(document.createTextNode(surname))
                pElt.appendChild(spanElt)


def replaceBiblio(node, iter_context):
    if node.nodeName != 'text:p':
        return
    if node.getAttribute('text:style-name') != 'Relation':
        return

    document = node.ownerDocument

    # remove existing
    for n in list(node.childNodes):
        node.removeChild(n)

    urls = iter_context['bibliorelation']
    n = 0
    for url in urls:
        n += 1
        span_node = document.createElement('text:span')
        span_node.setAttribute('text:style-name', 'Text body') # XXX
        span_node.appendChild(document.createTextNode(url))
        node.appendChild(span_node)

def replaceCopyright(node, iter_context):
    if node.nodeName != 'text:p':
        return
    if node.getAttribute('text:style-name') != 'Copyright':
        return

    document = node.ownerDocument

    # remove existing
    for n in list(node.childNodes):
        node.removeChild(n)

    copyright = iter_context['copyright']
    year = iter_context['year']
    holder = iter_context['holder']

    if copyright:
        if year or holder:
            copyright += ' '
        node.appendChild(document.createTextNode(copyright))
    if year:
        span_node = document.createElement('text:span')
        span_node.setAttribute('text:style-name', 'Year')
        span_node.appendChild(document.createTextNode(year))
        node.appendChild(span_node)
    if year and holder:
        node.appendChild(document.createTextNode(' '))
    if holder:
        span_node = document.createElement('text:span')
        span_node.setAttribute('text:style-name', 'Holder')
        span_node.appendChild(document.createTextNode(holder))
        node.appendChild(span_node)

def parseCopyright(s):
    """Parse a copyright string.

    Returns the copyright, year and holder.
    """
    m = re.match('([^\d]*)([-\d\s,]*)(.*)', s)
    if m is None:
        return s, '', ''

    groups = m.groups()
    if len(groups) != 3:
        return s, '', ''

    copyright, year, holder = groups
    copyright = copyright.strip()
    year = year.strip()
    holder = holder.strip()
    return copyright, year, holder


# factory_type_information is useless for a class that fits in
# the CPSDocument framework.
## factory_type_information = (
##     )

class OOoDocbookDocument(CPSDocument):
    """A CPSDocument that holds many information and especially many metadata
    about enclosed files.
    """

    # Too ease debugging
    meta_type = 'OOoDocbookDocument'
    portal_type = meta_type

    security = ClassSecurityInfo()

    security.declareProtected(View, 'duplicate')
    def duplicate(self, proxy, selected_folders=[]):
        """Duplicate a StructuredDoducment with a resulting copy that has all
        its metadata fields empty except for the reference field which corresponds
        to the original document.
        """
        LOG(logKey, DEBUG, "selected_folders = %s" % str(selected_folders))
        portal = self.portal_url.getPortalObject()
        folders = []
        for selected_folder_path in selected_folders:
            folders.append(portal.unrestrictedTraverse(selected_folder_path))

        proxyId = proxy.getId()
        proxyContainer = aq_parent(aq_inner(proxy))
        for folder in folders:
            ref = proxyContainer.manage_CPScopyObjects([proxyId])
            pastedIdsDict = folder.manage_CPSpasteObjects(ref)
            #LOG(logKey, DEBUG, "pastedIdsDict = %s" % str(pastedIdsDict))
            duplicateProxyId = pastedIdsDict[0]['new_id']
            duplicateProxy = getattr(folder, duplicateProxyId)

            duplicateDocument = duplicateProxy.getEditableContent()
            duplicateDocument.edit(
                Title="(Duplicata) " + self.Title(),
                Subject=[],
                Contributors=[],
                Rights='',
                Source='',
                Relation=self.Reference,
                Reference='',
                Coverage='',
                Keywords=[])

    security.declareProtected(View, 'exportXmlDocbook')
    def exportXmlDocbook(self, REQUEST=None, **kw):
        """Export XML, in the Docbook XML format, for this document.
        """
        tmpDirName = tempfile.mktemp()
        tmpDirPath = os.path.join(tempfile.tempdir, tmpDirName)
        os.mkdir(tmpDirPath)

        filePaths = []

        # Regexp to replace "xxx.sxw" by "xxx.docb.xml"
        dbFileName = re.sub('\..+?$', '.docb.xml', self.file.title)
        dbFilePath = os.path.join(tmpDirPath, dbFileName)
        LOG(logKey, DEBUG, "DocBook file path = %s" % dbFilePath)
        filePaths.append(dbFilePath)
        dbFile = open(dbFilePath, 'w+c')
        dbFile.write(str(self.file_xml))
        dbFile.flush()

        imageFileNames = self.file_xml_subfiles
        for imageFileName in imageFileNames:
            imageFilePath = os.path.join(tmpDirPath, imageFileName)
            LOG(logKey, DEBUG, "Image file path = %s" % imageFilePath)
            filePaths.append(imageFilePath)
            imageFile = open(imageFilePath, 'w+c')
            imageFile.write(str(getattr(self, imageFileName)))
            imageFile.flush()

        # Regexp to replace "xxx.sxw" by "xxx.zip"
        archiveFileName = re.sub('\..+?$', '.zip', self.file.title)
        archiveFilePath = os.path.join(tmpDirPath, archiveFileName)
        LOG(logKey, DEBUG, "Archive file path = %s" % archiveFilePath)
        # Create a ZipFile object to write into
        archiveFile = ZipFile(archiveFilePath, 'w')
        archiveInternalSubDirName = dbFileName.split('.')[0]
        for filePath in filePaths:
            LOG(logKey, DEBUG, "adding file to archive = %s" % filePath)
            if filePath != dbFilePath:
                filePathInTheArchive = os.path.join(archiveInternalSubDirName,
                                                    'images', os.path.split(filePath)[1])
            else:
                filePathInTheArchive = os.path.join(archiveInternalSubDirName,
                                                    os.path.split(filePath)[1])

            # The second parameter is to specify another path than the given
            # file path. This has effect on the tree structures produced when
            # the archived is uncompressed later on.
            archiveFile.write(filePath, filePathInTheArchive)
        archiveFile.close()
        dbFile.close()

        archiveFile = open(archiveFilePath, 'r')
        archiveFile.flush()
        out = archiveFile.read()
        archiveFile.close()

        shutil.rmtree(tmpDirPath)

        resp = self.REQUEST.RESPONSE
        resp.setHeader('Content-Type', 'application/zip')
        resp.setHeader('Content-Disposition', 'filename=' + archiveFileName)
        # The "no-cache" headers hit a bug when using MSIE on SSL so we need to use the
        # approach of using the Last-Modified header.
        # http://support.microsoft.com/default.aspx?scid=http://support.microsoft.com:80/support/kb/articles/q316/4/31.asp&NoWebContent=1&NoWebContent=&NoWebContent=1
        #resp.setHeader('Pragma', 'no-cache')
        #resp.setHeader('Cache-Control', 'no-cache')
        resp.setHeader('Last-Modified', rfc1123_date())

        return out


    security.declarePrivate('postCommitHook')
    def postCommitHook(self, datamodel=None):
        """This method is called just after the datamodel commit.

        Here we have to update:

        - the metadata from the document if a document was uploaded,

        - the document from the metadata if some metadata was modified.

        If both document and metadata have been modified, the document
        takes precedence.
        """
        # Call base class
        CPSDocument.inheritedAttribute('postCommitHook')(
            self, datamodel=datamodel)

        LOG(logKey, DEBUG, 'postCommitHook: dm.dirty=%s' %
            datamodel.dirty.keys())

        if datamodel.isDirty('file'):
            self._updateMetadataFromDocument(datamodel)
        else:
            self._updateDocumentFromMetadata(datamodel)


    def _updateMetadataFromDocument(self, datamodel):
        """Update the object's metadata from the document."""

        LOG(logKey, DEBUG, "_updateMetadataFromDocument")

        if not self.file_xml:
            LOG(logKey, PROBLEM,
                "_updateMetadataFromDocument no file_xml -> no update")
            return

        file_xml_string = str(self.file_xml)
        if not file_xml_string:
            LOG(logKey, PROBLEM,
                "_updateMetadataFromDocument no file_xml_string -> no update")
            return

        doc = ElementTree(XML(file_xml_string))
        rootElt = doc.getroot()
        articleInfoElt = xpath_find(rootElt, 'articleinfo')

        title = findFirstText(articleInfoElt, 'title')
        elts = xpath_findall(articleInfoElt, 'abstract/para')
        abstract = ''
        delimiter = ''
        for elt in elts:
            if elt.text:
                abstract = '%s%s%s' % (abstract, delimiter, toLatin9(elt.text))
                delimiter = '\n\n'

        LOG(logKey, DEBUG, "_updateMetadataFromDocument abstract = %s" % abstract)

        year = findText(articleInfoElt, 'copyright/year')
        holder = findText(articleInfoElt, 'copyright/holder')
        rights = " ".join(filter(None, [year, holder]))
        if rights:
            rights = "Copyright © " + rights

        coverage = findFirstText(articleInfoElt, 'bibliocoverage')
        LOG(logKey, DEBUG, "_updateMetadataFromDocument coverage = %s" % coverage)
        source = findFirstText(articleInfoElt, 'bibliosource')
        LOG(logKey, DEBUG, "_updateMetadataFromDocument source = %s" % source)
        relation = ''
        relationElts = xpath_findall(articleInfoElt,
                                     'bibliorelation/ulink')
        for elt in relationElts:
            if elt.get('url'):
                relation = elt.get('url')
                break

        contributors = []
        contributorsElts = xpath_findall(articleInfoElt, 'othercredit')
        for contributorsElt in contributorsElts:
            firstname = findFirstText(contributorsElt, 'firstname')
            surname = findFirstText(contributorsElt, 'surname')
            contributor = " ".join(filter(None, [firstname, surname]))
            if contributor:
                contributors.append(contributor)

        keywordElts = xpath_findall(articleInfoElt, 'keywordset/keyword')
        keywords = [toLatin9(x.text) for x in keywordElts or ()]
        LOG(logKey, DEBUG, "_updateMetadataFromDocument keywords = %s" % ", ".join(keywords))

        # Do not use unfilled data from an OOo document on to the
        # portal. Unfilled data is marked up as <xxxxx>.
        if (title is not None and title is not ''
            and not title.startswith('<') and not title.endswith('>')):
            self.setTitle(title)
        if (abstract is not None
            and not abstract.startswith('<') and not abstract.endswith('>')):
            self.setDescription(abstract)
        if (rights is not None
            and not rights.startswith('<') and not rights.endswith('>')):
            self.setRights(rights)
        if (coverage is not None
            and not coverage.startswith('<') and not coverage.endswith('>')):
            self.setCoverage(coverage)
        if (source is not None
            and not source.startswith('<') and not source.endswith('>')):
            self.setSource(source)
        if (relation is not None
            and not relation.startswith('<') and not relation.endswith('>')):
            self.setRelation(relation)
        self.setContributors(contributors)
        self.Keywords = keywords

        # Parse XML into DOM and modify it.
        document = xml.dom.minidom.parseString(file_xml_string)
        articleinfoElt = document.getElementsByTagName('articleinfo')[0]
        paraElts = articleinfoElt.getElementsByTagName('para')
        for elt in paraElts:
            if elt.getAttribute('role') == 'demandeur':
                demandeur = elt.childNodes[0].nodeValue
                self.Demandeur = demandeur
            if elt.getAttribute('role') == 'rapporteur':
                rapporteur = elt.childNodes[0].nodeValue
                self.Rapporteur = rapporteur


    def _updateDocumentFromMetadata(self, datamodel):
        """Update the document from the object's metadata."""
        LOG(logKey, DEBUG, '_updateDocumentFromMetadata')

        file = getattr(aq_base(self), 'file', None)
        if file is None:
            return

        # These filenames always cleaned up
        dirname = mktempdir()
        all_filenames = {} # map of inzip-filename to fs-filename
        zipfilename = None

        try:
            # Uncompress zipfile into a flat structure.
            # Keep content_xml for later treatment
            content_xml = None
            try:
                z = ZipFile(StringIO(str(file)), 'r')
            except BadZipfile:
                LOG(logKey, DEBUG, "Attached file is not a zipfile")
                return
            for zfilename in z.namelist():
                filename = zfilename.replace('/', '_')
                all_filenames[zfilename] = filename
                fstr = z.read(zfilename)
                if filename == 'content.xml':
                    content_xml = fstr
                else:
                    full_filename = os.path.join(dirname, filename)
                    f = open(full_filename, 'w')
                    f.write(fstr)
                    f.close()
                del fstr
            z.close()

            if content_xml is None:
                LOG(logKey, DEBUG,
                    "Document does not have any content.xml")
                return

            # Parse XML into DOM and modify it.
            document = xml.dom.minidom.parseString(content_xml)

            self._updateDomFromMetadata(document)

            # Write the final doc.
            full_filename = os.path.join(dirname, 'content.xml')
            f = open(full_filename, 'w')
            xml.dom.ext.Print(document, f)
            f.close()

            # Recompress all into a zipfile.
            fd, zipfilename = tempfile.mkstemp(suffix='.sxw')
            os.close(fd)
            os.unlink(zipfilename)
            z = ZipFile(zipfilename, 'w', ZIP_DEFLATED)
            for zfilename, filename in all_filenames.items():
                full_filename = os.path.join(dirname, filename)
                z.write(full_filename, zfilename)
            z.close()

            # Now read the zipfile into memory
            f = open(zipfilename, 'rb')
            file = File(file.getId(), file.title, f)
            file.content_type = 'application/vnd.sun.xml.writer'
            f.close()

            # Set file back in datamodel and recommit
            # (this recomputes dependent fields).
            datamodel['file'] = file
            datamodel._commitData()

        finally:
            # Cleanup temp files
            for zfilename, filename in all_filenames.items():
                full_filename = os.path.join(dirname, filename)
                try:
                    os.unlink(full_filename)
                except OSError:
                    pass
            try:
                os.rmdir(dirname)
            except OSError:
                pass
            if zipfilename:
                try:
                    os.unlink(zipfilename)
                except OSError:
                    pass

        return


    def _updateDomFromMetadata(self, document):
        """Update a DOM tree from the current metadata."""
        iter_context = {
            'textnodes': (
                ('text:p', 'text:style-name', 'Title',
                 toUnicode(self.Title())),
                ('text:p', 'text:style-name', 'Résumé/Abstract',
                 toUnicode(self.Description())),
                ('text:p', 'text:style-name', 'Bibliocoverage',
                 toUnicode(self.Coverage())),
                ('text:p', 'text:style-name', 'Source',
                 toUnicode(self.Source())),
                ),
            }
        #iterDoc(document, replaceTextElements, iter_context)
        iterDoc(document, replaceTextElementsByStyleName, iter_context)

        iter_context = {
            'keywords': [toUnicode(k) for k in self.Keywords],
            }
        iterDoc(document, replaceKeywords, iter_context)

        iter_context = {
            'bibliorelation': [toUnicode(self.Relation())],
            }
        iterDoc(document, replaceBiblio, iter_context)

        copyright, year, holder = parseCopyright(toUnicode(self.Rights()))
        iter_context = {
            'copyright': copyright,
            'year': year,
            'holder': holder,
            }
        iterDoc(document, replaceCopyright, iter_context)

        replaceContributors([toUnicode(k) for k in self.Contributors()], document)


InitializeClass(OOoDocbookDocument)


def addOOoDocbookDocumentInstance(container, id, REQUEST=None, **kw):
    """Factory method
    """

    instance = OOoDocbookDocument(id, **kw)
    container._setObject(id, instance)

    # It's mandatory then after to get the object through its parent, for the
    # object to have a reference on its parent. Having the object know about its
    # parent is mandatory if one wants to be able to call some methods like
    # manage_addProduct() on it.
    #object = getattr(container, id)

    if REQUEST:
        object = container._getOb(id)
        LOG(logKey, DEBUG, "object = %s" % object)
        REQUEST.RESPONSE.redirect(object.absolute_url() + '/manage_main')
