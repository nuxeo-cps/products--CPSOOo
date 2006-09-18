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

from zLOG import LOG, DEBUG, WARNING
from Globals import InitializeClass

from OFS.Image import cookId, File

from Products.CMFCore.Expression import Expression

from Products.CPSSchemas.Field import CPSField, FieldRegistry
from Products.CPSSchemas.Field import ValidationError
from Products.CPSSchemas.FileUtils import convertFileToHtml
from Products.CPSSchemas.FileUtils import convertFileToDocbook
from Products.CPSSchemas.FileUtils import convertFileToText

class CPSOOoDocbookFileField(CPSField):
    """File field."""
    log_key = 'CPSOOoDocbookFileField'
    meta_type = "CPS OpenOffice.org Docbook Field"

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    _properties = CPSField._properties + (
        {'id': 'suffix_text', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing Text conversion'},
        {'id': 'suffix_xml', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing DocBook XML conversion'},
        {'id': 'suffix_xml_subfiles', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing DocBook XML conversion subobjects'},
        {'id': 'suffix_html', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion'},
        {'id': 'suffix_html_subfiles', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion subobjects'},
        )
    suffix_text = ''
    suffix_xml = ''
    suffix_xml_subfiles = ''
    suffix_html = ''
    suffix_html_subfiles = ''

    def _getDependantFieldId(self, schemas, suffix):
        """Get a dependant field id described by the suffix."""
        if not suffix:
            return None
        id = self.getFieldId() + suffix
        for schema in schemas:
            if schema.has_key(id):
                return id
        return None

    def computeDependantFields(self, schemas, data, context=None):
        """Compute dependant fields.

        schemas is the list of schemas

        data is the dictionnary of the datamodel
        """
        field_id = self.getFieldId()
        file = data[field_id] # May be None.

        xml_field_id = self._getDependantFieldId(schemas, self.suffix_xml)
        xml_subfiles_field_id = self._getDependantFieldId(schemas,
                                                          self.suffix_xml_subfiles)
        if xml_field_id is not None:
            xml_conversion = convertFileToDocbook(file, context=context)
            if xml_conversion is not None:
                xml_string = xml_conversion.getData()
##                 LOG('log_key', DEBUG, "xml_string = %s..." % xml_string[:1000])
                fileid = cookId('', '', file)[0]
                if '.' in fileid:
                    fileid = fileid[:fileid.rfind('.')]
                if not fileid:
                    fileid = 'document'
                fileid = fileid + '.docb'
                xml_file = File(fileid, '', xml_string,
                                 content_type='application/docbook+xml')

                # getSubObjects returns a dict of sub-objects, each sub-object
                # being a file but described as a string.
                subobjects_dict = xml_conversion.getSubObjects()
                files_dict = {}
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
##                 LOG('log_key', DEBUG, "files_dict = %s" % `files_dict`)
            else:
                xml_file = None
                files_dict = {}
            data[xml_field_id] = xml_file
            data[xml_subfiles_field_id] = files_dict

        html_field_id = self._getDependantFieldId(schemas, self.suffix_html)
        html_subfiles_field_id = self._getDependantFieldId(schemas,
                                                           self.suffix_html_subfiles)
        if html_field_id is not None:
            html_conversion = convertFileToHtml(xml_file, context=context,
                                                subobjects=data[xml_subfiles_field_id])
            if html_conversion is not None:
                html_string = html_conversion.getData()
##                 LOG('log_key', DEBUG, "html_string = %s..." % html_string[:1000])
                fileid = cookId('', '', xml_file)[0]
                if '.' in fileid:
                    fileid = fileid[:fileid.rfind('.')]
                if not fileid:
                    fileid = 'document'
                fileid = fileid + '.html'
                html_file = File(fileid, '', html_string,
                                 content_type='text/html')

                # getSubObjects returns a dict of sub-objects, each sub-object
                # being a file but described as a string.
                subobjects_dict = html_conversion.getSubObjects()
                files_dict = {}
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
##                 LOG('log_key', DEBUG, "files_dict = %s" % `files_dict`)
            else:
                html_file = None
                files_dict = {}
            data[html_field_id] = html_file
            data[html_subfiles_field_id] = files_dict

        text_field_id = self._getDependantFieldId(schemas, self.suffix_text)
        if text_field_id is not None:
            data[text_field_id] = convertFileToText(html_file, context=context)

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if isinstance(value, File):
            return value
        raise ValidationError('Not a file: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return None
        if len(values) != 1:
            raise ValidationError("Incorrect File value from LDAP: "
                                  "(%d-element list)" % len(values))
        return File(self.getFieldId(), '', values[0])


InitializeClass(CPSOOoDocbookFileField)


# Register field classes
FieldRegistry.register(CPSOOoDocbookFileField)
