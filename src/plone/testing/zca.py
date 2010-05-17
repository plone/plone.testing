"""Core Zope Component Architecture helpers and layers
"""

from plone.testing import Layer

# Contains a stack of previously installed global registries (but not the
# current one)
_REGISTRY_STACK = []

def pushGlobalRegistry(new=None):
    """Set a new global component registry that uses the current registry as
    a a base. If you use this, you *must* call ``popGlobalRegistry()`` to
    restore the original state.
    
    If ``new`` is not given, a new registry is created. If given, you must
    provide a ``zope.component.registry.Components`` object.
    
    Returns the new registry.
    """
    
    global _REGISTRY_STACK
    
    from zope.component import _api
    from zope.component import globalregistry
    from zope.component.registry import Components
    
    # Save the current top of the stack in a registry
    current = globalregistry.base
    _REGISTRY_STACK.append(current)
    
    if new is None:
        new = Components(name='stacked-test-%d' % len(_REGISTRY_STACK), bases=(current,))
    
    # Monkey patch this into the three (!) places where zope.component references
    # it as a module global variable
    _api.base = globalregistry.base = globalregistry.globalSiteManager = new
    
    # Reset the site manager hook so that getSiteManager() returns the base
    # again
    from zope.component import getSiteManager
    getSiteManager.reset()
    
    try:
        from zope.site.hooks import setSite
        setSite()
    except ImportError:
        pass
    
    return new

def popGlobalRegistry():
    """Restore the global component registry form the top of the stack, as
    set with ``pushGlobalRegistry()``.
    """
    
    global _REGISTRY_STACK
    
    from zope.component import _api
    from zope.component import globalregistry
    
    previous = _REGISTRY_STACK.pop()
    _api.base = globalregistry.base = globalregistry.globalSiteManager = previous
    
    # Reset the site manager hook so that getSiteManager() returns the base
    # again
    from zope.component import getSiteManager
    getSiteManager.reset()
    
    try:
        from zope.site.hooks import setSite
        setSite()
    except ImportError:
        pass
    
    return previous

class Sandbox(Layer):
    """Zope Component Architecture sandbox: The ZCA is cleared for each
    test and torn down after each test.
    """
    
    defaultBases = ()
    
    def testSetUp(self):
        import zope.component.testing
        zope.component.testing.setUp()
    
    def testTearDown(self):
        import zope.component.testing
        zope.component.testing.tearDown()

SANDBOX = Sandbox()

class EventTesting(Layer):
    """Set up event testing for each test. This allows use of the helper
    function ``zope.component.eventtesting.getEvent()`` to obtain and inspect
    events fired during the test run.
    
    Since the ``Sandbox`` tear-down executes ``zope.testing.cleanup.cleanUp``,
    the event testing events list is emptied for each test.
    """
    
    defaultBases = (SANDBOX,)
    
    def testSetUp(self):
        import zope.component.eventtesting
        zope.component.eventtesting.setUp()
    
EVENT_TESTING = EventTesting()

class ZCMLDirectives(Layer):
    """Enables the use of the basic ZCML directives from ``zope.component``.
    
    Exposes a ``zope.configuration`` configuration context as the resource
    ``configurationContext``.
    """
    
    defaultBases = ()
    
    def setUp(self):
        
        from zope.configuration import xmlconfig
        import zope.component
        
        self['configurationContext'] = xmlconfig.file('meta.zcml', zope.component)
    
    def tearDown(self):
        del self['configurationContext']
    
ZCML_DIRECTIVES = ZCMLDirectives()
