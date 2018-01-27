# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest
from OFS.SimpleItem import SimpleItem
from pkg_resources import get_distribution
from ZPublisher.Iterators import filestream_iterator
from zope.testing import renormalizing

import doctest
import os.path
import re
import zope.component.testing


# This is somewhat retarted. We execute README.rst as a doctest, mainly just
# to test that the code samples import cleanly and are valid Python. However,
# in there we also have a code sample of a doctest, which gets executed by the
# doctest runner. Since the method inside the example code block is not yet
# defined when the doctest example is encountered, we get a NameError.
#
# To get around this, we define a fake method and stick it into the globs for
# the doctest.


def _canOutrunKlingons(warpDrive):
    return warpDrive.maxSpeed > 8.0


class DummyUtility(object):

    def __repr__(self):
        return '<Dummy utility>'


class DummyView(object):

    def __init__(self, context, request):
        pass

    def __call__(self):
        return u''


class DummyFile(SimpleItem):

    def __call__(self):
        path = get_distribution('plone.testing').location
        path = os.path.join(path, 'plone', 'testing', 'z2.rst')

        request = self.REQUEST
        response = request.response
        response.setHeader('Content-Type', 'text/plain')
        response.setHeader('Content-Length', os.path.getsize(path))
        return filestream_iterator(path)


def setUp(self):
    zope.component.testing.setUp()


def tearDown(self):
    zope.component.testing.tearDown()


checker = renormalizing.RENormalizing([
    # normalize py2 output to py3
    (re.compile(r'__buildin__'), r'buildins'),

    (re.compile(
        r"'Unknown directive', u'http://namespaces.zope.org/zope', u'"),
     r"'Unknown directive', 'http://namespaces.zope.org/zope', '"),

    # normalize py3 output to py3
    (re.compile(
        r"zope\.configuration\.xmlconfig\.ZopeXMLConfigurationError"),
     r"ZopeXMLConfigurationError"),
    (re.compile(r"builtins\.PopulatedZODB"), r"PopulatedZODB"),
    (re.compile(r"builtins\.ExpandedZODB"), r"ExpandedZODB"),
])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            'layer.rst',
            'zca.rst',
            'security.rst',
            'publisher.rst',
            'zodb.rst',
            'z2.rst',
            checker=checker,
            setUp=setUp,
            tearDown=tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
        doctest.DocFileSuite(
            'README.rst',
            globs={'canOutrunKlingons': _canOutrunKlingons, },
            setUp=setUp,
            tearDown=tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
    ])
    return suite
