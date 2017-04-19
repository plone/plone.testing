# -*- coding: utf-8 -*-
"""Helpers for working with common Zope publisher operations
"""
from plone.testing import Layer
from plone.testing import security
from plone.testing import zca


class PublisherDirectives(Layer):
    """Enables the use of the ZCML directives from ``zope.browsermenu``,
    ``zope.browserpage``, ``zope.browserresource`` and ``zope.publisher`` (most
    of the ``browser`` namespace, excluding viewlets), and ``zope.security``
    (the ``permission`` directive).

    Extends ``zca.ZCML_DIRECTIVES`` and uses its ``configurationContext``
    resource.
    """

    defaultBases = (zca.ZCML_DIRECTIVES, security.CHECKERS)

    def setUp(self):
        from zope.configuration import xmlconfig

        # Stack a new configuration context
        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext'))

        import zope.security
        xmlconfig.file('meta.zcml', zope.security, context=context)

        import zope.browsermenu
        xmlconfig.file('meta.zcml', zope.browsermenu, context=context)
        import zope.browserpage
        xmlconfig.file('meta.zcml', zope.browserpage, context=context)
        import zope.browserresource
        xmlconfig.file('meta.zcml', zope.browserresource, context=context)
        import zope.publisher
        xmlconfig.file('meta.zcml', zope.publisher, context=context)

    def tearDown(self):
        # Zap the stacked configuration context
        del self['configurationContext']


PUBLISHER_DIRECTIVES = PublisherDirectives()
