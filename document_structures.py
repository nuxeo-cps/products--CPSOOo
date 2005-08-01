# -*- coding: ISO-8859-15 -*-
# $Id$
"""Return custom document types."""

ooo_docbook_document_type = {
    'title': "portal_type_OOoDocbookDocument_title",
    'description': "portal_type_OOoDocbookDocument_description",
    'content_icon': 'ooo_docbook_document_icon.png',
    #'content_meta_type': 'CPS Document',
    'content_meta_type': 'OOoDocbookDocument',
    #'product': 'CPSDocument',
    'product': 'CPSOOo',
    #'factory': 'addCPSDocument',
    'factory': 'addOOoDocbookDocumentInstance',
    #'immediate_view': 'cpsdocument_edit_form',
    'immediate_view': 'cpsdocument_view',
    'global_allow': 1,
    'filter_content_types': 1,
    'allowed_content_types': [],
    'allow_discussion': 1,
    'cps_is_searchable': 1,
    # Choose between 'document', 'folder' or 'folderishdocument'
    # according to the need to store objects in your document or not.
    'cps_proxy_type': 'document',
    #'cps_proxy_type': 'folderishdocument',
    #'cps_proxy_type': 'folder',
    'schemas': ['metadata', 'common', 'ooo_docbook_document'],
    'layouts': ['common', 'ooo_docbook_document'],
    'layout_clusters': ['metadata:metadata'],
    'flexible_layouts': [],
    'storage_methods': [],
    #'cps_workspace_wf': 'workspace_structured_document_wf',
    'cps_workspace_wf': 'workspace_content_wf',
    'cps_section_wf': 'section_content_wf',
    'use_content_status_history': 1,
    'actions_add': ({'id': 'edit_online',
                     'name': 'action_edit_online',
                     'action': 'python:portal.getExternalEditorPath(object, "file", "file")',
                     'condition': ('python:object is not None '
                                   'and object.getContent().file is not None '
                                   'and modules["Products.CPSUtil.integration"].isProductPresent("Products.ExternalEditor")'),
                     'permissions': ('Modify portal content',)
                     },
                    {'id': 'xml_docbook_export',
                     'name': 'action_xml_docbook_export',
                     'action': 'string:${object_url}/exportXmlDocbook',
                     'condition' : 'python:object.getContent().file',
                     'permissions': ('View',),
                     },
                    ),
    }

def getDocumentTypes(portal=None):
    types = {}
    types['OOoDocbookDocument'] = ooo_docbook_document_type
    return types


ooo_docbook_document_schema = {
    'file': {
        'type': 'CPS OpenOffice.org Docbook Field',
        'data': {
                'default_expr': 'nothing',
                'is_searchabletext': 0,
                'suffix_text': '_text',
                'suffix_html': '_html',
                'suffix_html_subfiles': '_html_subfiles',
                'suffix_xml': '_xml',
                'suffix_xml_subfiles': '_xml_subfiles',
            },
        },
    'file_text': {
        'type': 'CPS String Field',
        'data': {
                'default_expr': 'string:',
                'is_searchabletext': 1,
            },
        },
    'file_xml': {
        'type': 'CPS File Field',
        'data': {
                'default_expr': 'nothing',
                'is_searchabletext': 0,
            },
        },
    'file_xml_subfiles': {
        'type': 'CPS SubObjects Field',
        'data': {
                'default_expr': 'nothing',
                'is_searchabletext': 0,
            },
        },
    'file_html': {
        'type': 'CPS File Field',
        'data': {
                'default_expr': 'nothing',
                'is_searchabletext': 0,
            },
        },
    'file_html_subfiles': {
        'type': 'CPS SubObjects Field',
        'data': {
                'default_expr': 'nothing',
                'is_searchabletext': 0,
            },
        },
    }

def getDocumentSchemas(portal=None):
    schemas = {}
    schemas['ooo_docbook_document'] = ooo_docbook_document_schema
    return schemas


ooo_docbook_document_layout = {
    'widgets': {
        'Source': {
            'type': 'String Widget',
            'data': {
                'fields': ['Source'],
                'hidden_layout_modes': ['view'],
                'is_i18n': 1,
                'label_edit': 'label_source',
                'label': '',
                'display_width': 30,
                'size_max': 80,
            },
        },
        'Rights': {
            'type': 'String Widget',
            'data': {
                'fields': ['Rights'],
                'hidden_layout_modes': ['view'],
                'is_i18n': 1,
                'label_edit': 'label_rights',
                'label': '',
                'display_width': 30,
                'size_max': 80,
            },
        },
        'file': {
            'type': 'AttachedFile Widget',
            'data': {
                'fields': ['file',
                           'file_text',
                           'file_html'],
                'is_i18n': 1,
                'label_edit': 'cpsdoc_attachedFile_label',
                'label': 'cpsdoc_attachedFile_label',
                'hidden_empty': 1,
                'description': 'cpsdoc_attachedFile_description',
                'deletable': 1,
                'size_max': 5*1024*1024,
                'allowed_suffixes': ('.sxw',),
            },

        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'ncols': 2,
        'rows': [
            [{'widget_id': 'Source'},
             {'widget_id': 'Rights'},],
            [{'widget_id': 'file'}, ],
            ],
        },
    }

def getDocumentLayouts(portal=None):
    layouts = {}
    layouts['ooo_docbook_document'] = ooo_docbook_document_layout
    return layouts
