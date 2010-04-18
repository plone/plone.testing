import unittest2 as unittest
import doctest

import zope.component.testing

# This is somewhat retarted. We execute README.txt as a doctest, mainly just
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
        return "<Dummy utility>"

class DummyView(object):
    def __init__(self, context, request):
        pass
    def __call__(self):
        return u""

def setUp(self):
    zope.component.testing.setUp()

def tearDown(self):
    zope.component.testing.tearDown()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            'layer.txt',
            'zca.txt',
            'publisher.txt',
            'zodb.txt',
            'z2.txt',
            setUp=setUp,
            tearDown=tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
        doctest.DocFileSuite(
            '../../../README.txt',
            globs={'canOutrunKlingons': _canOutrunKlingons,},
            setUp=setUp,
            tearDown=tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
    ])
    return suite
