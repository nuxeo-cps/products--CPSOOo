# $id$

from Testing import ZopeTestCase
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('CPSOOo')

CPSTestCase.setupPortal()

CPSOOoTestCase = CPSTestCase.CPSTestCase
