"""Core Zope Toolkit helpers and layers
"""

from plone.testing import Layer
from plone.testing import zca

class Placeless(Layer):
    """Sets up a basic, non-location-aware ("placeless"") ZTK environment.
    This includes ZCA tear-down after each test, "eventtesting" support,
    basic ``zope.container`` support, a password manager, the IAbsoluteURL
    view, an empty vocabulary registry, and a new interaction per test.
    """
    
    __bases__ = (zca.EVENT_TESTING,)
    
    def testSetUp(self):
        
        # This is basically what zope.app.testing.placelesssetup does, except 
        # we don't want to duplicate what we already have EVENT_TESTING
        # and SANDBOX, and we don't want to depend on zope.app.testing
        
        import zope.container.testing
        zope.container.testing.PlacelessSetup().setUp()
        
        import zope.i18n.testing
        zope.i18n.testing.setUp()
        
        import zope.password.testing

        zope.password.testing.setUpPasswordManagers()
        
        from zope.component import provideAdapter
        from zope.interface import Interface
        
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        
        from zope.traversing.browser.interfaces import IAbsoluteURL
        from zope.traversing.browser.absoluteurl import AbsoluteURL
        
        provideAdapter(AbsoluteURL, adapts=(Interface, IDefaultBrowserLayer,), provides=Interface, name="absolute_url")
        provideAdapter(AbsoluteURL, adapts=(Interface, IDefaultBrowserLayer,), provides=IAbsoluteURL)

        from zope.security.testing import addCheckerPublic
        addCheckerPublic()

        from zope.security.management import newInteraction
        newInteraction()

PLACELESS = Placeless()

class ZCMLDirectives(Layer):
    """Enables the use of the ZCML directives from ``zope.app.publisher``
    (most of the ``browser`` namespace, excluding viewlets), and
    ``zope.security`` (the ``permission`` directive).
    
    Extends ``zca.ZCML_DIRECTIVES`` and uses its ``configurationContext``
    resource.
    """
    
    __bases__ = (zca.ZCML_DIRECTIVES,)
    
    def setUp(self):
        from zope.configuration import xmlconfig
        
        # From the zca.ZCML_DIRECTIVES base layer
        context = self['configurationContext']
        
        # XXX: In Zope 2.13, this has split into zope.publisher,
        # zope.browserresource, zope.browsermenu and zope.browserpage
        import zope.app.publisher
        xmlconfig.file('meta.zcml', zope.app.publisher, context=context)
        
        import zope.security
        xmlconfig.file('meta.zcml', zope.security, context=context)
    
    def tearDown(self):
        # XXX: No proper tear-down
        pass

ZCML_DIRECTIVES = ZCMLDirectives()
