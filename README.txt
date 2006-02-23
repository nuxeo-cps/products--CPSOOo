======
README
======

:Author: Marc-Aurèle DARCHE
:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4


Presentation
============

CPSOOo is a product that installs a new document type which holds an
OpenOffice.org file to generate a DocBook XML semantic document from it and
the associated DocBook XML high-quality normative HTML output.

All the dependencies of CPSOOo are described in DEPENDENCIES.txt_. Be sure to
read this file.

.. _DEPENDENCIES.txt: DEPENDENCIES.txt


Logic
=====

CPSOOo relies on 2 chained transformations from PortalTransforms:

`ooo_to_docbook` -> `docbook_to_html`

CPSOOo does not use nor rely on the `ooo_to_html` transform.

Preview and indexation
----------------------

The "preview" link will only appear if the `docbook_to_html` has been successful
and thus that an HTML preview of an OpenOffice.org DocBook DocBook exists.

Also note that the indexation of an OpenOffice.org DocBook Document will only
happen if the "preview" link is present. This is because indexation if made
through the `html_to_text` transform after the HTML preview of the document.


Troubleshooting
===============

Check the dependencies
----------------------

All the dependencies of CPSOOo are described in DEPENDENCIES.txt_. Be sure to
read this file since missing dependencies are a usual cause of errors.

Problems might lie in one of the transforms ooo_to_docbook, docbook_to_html, or
both.

Check transforms presence
-------------------------

Check that both of those transforms are available in the portal_transforms tool
at the root of your CPS instance. If there are some missing you should reinstall
the portal_transforms tool. With CPS version < 3.4.0 you can do this through the
External Method "portal_transforms_installer" located at the root of the CPS
instance. With CPS >= 3.4.0 : TODO
 
Check transforms transformation logs
------------------------------------

If you have all those needed components and transforms the error might be deeper
and debugging through log reading might be needed. This is easy to do and doing
this, it is easy to spot where problems lie.

You just have to comment the following line which appears both in
`PortalTransforms/transforms/ooo_to_docbook.py` and
`PortalTransforms/transforms/docbook_to_html.py`::

  self.cleanDir(tmpdir)

Then you need to reload the transforms you have modified. This can be achieved
by either restarting your Zope instance or selecting the "Reload transforms" tab
of the portal_transforms tool at the root of your CPS instance.

Finally you can create a new OpenOffice.org DocBook Document in CPS and read the
log (which are usually in log/event.log) for lines such as::

  2006-02-15T17:10:02 DEBUG(-200) ooo_to_docbook cmd = cd "/tmp/tmpJ8WHg_" &&
  /usr/local/zope/instance/cps1/Products/PortalTransforms/transforms/ooo2dbk/ooo2dbk
  --dbkfile unknown.docb.xml /tmp/tmpJ8WHg_/unknown.sxw 2>"unknown.log-xsltproc"

  2006-02-15T17:10:03 DEBUG(-200) docbook_to_html cmd = cd "/tmp/tmp-77uq_" &&
  /usr/bin/xsltproc --novalid
  /usr/local/zope/instance/cps1/Products/PortalTransforms/transforms/docbook/custom-xhtml.xsl
  /tmp/tmp-77uq_/unknown.docb.xml>>"unknown.docb.html" 2>"unknown.docb.log-xsltproc"


You can then read the files in `/tmp/tmpJ8WHg_/` and `/tmp/tmp-77uq_`
to find out where the problem lies. The files `unknown.log-xsltproc` and
`unknown.docb.log-xsltproc` contain the output of the ooo2dbk and xsltproc
programs.

Note that the files `/tmp/tmpJ8WHg_/` and `/tmp/tmp-77uq_` are temporary files
with random generated names that are different each time a new transformation
runs.



.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:
