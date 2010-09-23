# -*- coding: utf-8 -*-
from unittest import TestCase
from plone.testing import Layer
import transaction

from plone.testing.z2 import FUNCTIONAL_TESTING, login


class TestZope210Layer(Layer):
    defaultBases = (FUNCTIONAL_TESTING, )

    def setUp(self):
        print "Assembling space ship"

    def tearDown(self):
        print "Disasembling space ship"

    def testSetUp(self):
        print "Fuelling space ship in preparation for test"

    def testTearDown(self):
        print "Emptying the fuel tank"

ZOPE210LAYER = TestZope210Layer()


class Zope210TestCase(TestCase):
    layer = ZOPE210LAYER

    def testRootPage(self):
        from plone.testing import z2
        app = self.layer['app']
        browser = z2.Browser(app)
        uf = app['acl_users']
        uf.userFolderAddUser('admin', 'admin', ['Manager'], [])
        transaction.commit()
        browser.addHeader('AUTHORIZATION',
                          'Basic %s:%s' % ('admin', 'admin'))
        url = app.absolute_url()
        browser.open("%s/Control_Panel" % url)
