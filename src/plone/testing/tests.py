from OFS.SimpleItem import SimpleItem
from pathlib import Path
from ZPublisher.Iterators import filestream_iterator

import doctest
import inspect
import os.path
import plone.testing
import unittest
import zope.component.testing


try:
    import ZServer  # noqa
except ImportError:
    HAS_ZSERVER = False
else:
    HAS_ZSERVER = True

# This is somewhat restarted. We execute README.rst as a doctest, mainly just
# to test that the code samples import cleanly and are valid Python. However,
# in there we also have a code sample of a doctest, which gets executed by the
# doctest runner. Since the method inside the example code block is not yet
# defined when the doctest example is encountered, we get a NameError.
#
# To get around this, we define a fake method and stick it into the globs for
# the doctest.


def _canOutrunKlingons(warpDrive):
    return warpDrive.maxSpeed > 8.0


class DummyUtility:
    def __repr__(self):
        return "<Dummy utility>"


class DummyView:
    def __init__(self, context, request):
        pass

    def __call__(self):
        return ""


class DummyFile(SimpleItem):
    def __call__(self):
        path = Path(inspect.getfile(plone.testing))
        path = path.parent / "zope.rst"

        request = self.REQUEST
        response = request.response
        response.setHeader("Content-Type", "text/plain")
        response.setHeader("Content-Length", os.path.getsize(path))
        return filestream_iterator(path)


def setUp(self):
    zope.component.testing.setUp()


def tearDown(self):
    zope.component.testing.tearDown()


class TestZ2(unittest.TestCase):
    """Testing plone.testing.z2."""

    def test_z2(self):
        """It can be imported. (It contains only BBB imports.)"""
        import plone.testing.z2

        self.assertIsNotNone(plone.testing.z2.ZSERVER)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            doctest.DocFileSuite(
                "layer.rst",
                "zca.rst",
                "security.rst",
                "publisher.rst",
                "zodb.rst",
                "zope.rst",
                setUp=setUp,
                tearDown=tearDown,
                optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            ),
            doctest.DocFileSuite(
                "README.rst",
                globs={
                    "canOutrunKlingons": _canOutrunKlingons,
                },
                setUp=setUp,
                tearDown=tearDown,
                optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            ),
        ]
    )
    if HAS_ZSERVER:
        suite.addTests(
            [
                doctest.DocFileSuite(
                    "zserver.rst",
                    setUp=setUp,
                    tearDown=tearDown,
                    optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
                ),
                unittest.TestLoader().loadTestsFromTestCase(TestZ2),
            ]
        )
    return suite
