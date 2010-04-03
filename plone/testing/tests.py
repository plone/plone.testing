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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            'layer.txt',
        ),
        doctest.DocFileSuite(
            '../../README.txt',
            globs={'canOutrunKlingons': _canOutrunKlingons,},
            tearDown=zope.component.testing.tearDown(),
        ),
    ])
    return suite
