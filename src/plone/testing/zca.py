"""Core Zope Component Architecture helpers and layers
"""

from plone.testing import Layer

# Contains a stack of installed global registries (but not the default one)
_REGISTRIES = []

def loadRegistry(name):
    for reg in reversed(_REGISTRIES):
        if reg.__name__ == name:
            return reg
    raise KeyError(name)

def pushGlobalRegistry(new=None):
    """Set a new global component registry that uses the current registry as
    a a base. If you use this, you *must* call ``popGlobalRegistry()`` to
    restore the original state.
    
    If ``new`` is not given, a new registry is created. If given, you must
    provide a ``zope.component.globalregistry.BaseGlobalComponents`` object.
    
    Returns the new registry.
    """
    
    from zope.component import _api
    from zope.component import globalregistry
    
    # Save the current top of the stack in a registry
    current = globalregistry.base
    
    # The first time we're called, we need to put the default global
    # registry at the bottom of the stack, and then patch the class to use
    # the stack loading for pickling
    if len(_REGISTRIES) == 0:
        _REGISTRIES.append(current)
        globalregistry.BaseGlobalComponents._old__reduce__ = globalregistry.BaseGlobalComponents.__reduce__
        globalregistry.BaseGlobalComponents.__reduce__ = lambda self: (loadRegistry, (self.__name__,))
    
    if new is None:
        name = 'test-stack-%d' % len(_REGISTRIES)
        new = globalregistry.BaseGlobalComponents(name=name, bases=(current,))
    
    _REGISTRIES.append(new)
    
    # Monkey patch this into the three (!) places where zope.component
    # references it as a module global variable
    _api.base = new
    globalregistry.base = new
    globalregistry.globalSiteManager = new
    
    # And the one in five.localsitemanager, if applicable
    try:
        from five import localsitemanager
    except ImportError:
        pass
    else:
        localsitemanager.base = new
    
    # Reset the site manager hook so that getSiteManager() returns the base
    # again
    from zope.component import getSiteManager
    getSiteManager.reset()
    
    try:
        from zope.site.hooks import setSite, setHooks
    except ImportError:
        pass
    else:
        setSite()
        setHooks()
    
    return new

def popGlobalRegistry():
    """Restore the global component registry form the top of the stack, as
    set with ``pushGlobalRegistry()``.
    """
    
    from zope.component import _api
    from zope.component import globalregistry
    
    if not _REGISTRIES or not _REGISTRIES[-1] is globalregistry.base:
        raise ValueError(u"popGlobalRegistry() called out of sync with pushGlobalRegistry()")
    
    current = _REGISTRIES.pop()
    previous = current.__bases__[0]
    
    # If we only have the default registry on the stack, return it to its
    # original state and empty the stack
    if len(_REGISTRIES) == 1:
        assert _REGISTRIES[0] is previous
        _REGISTRIES.pop()
        globalregistry.BaseGlobalComponents.__reduce__ = globalregistry.BaseGlobalComponents._old__reduce__
    
    _api.base = previous
    globalregistry.base = previous
    globalregistry.globalSiteManager = previous
    
    try:
        from five import localsitemanager
    except ImportError:
        pass
    else:
        localsitemanager.base = previous
    
    # Reset the site manager hook so that getSiteManager() returns the base
    # again
    from zope.component import getSiteManager
    getSiteManager.reset()
    
    try:
        from zope.site.hooks import setSite, setHooks
    except ImportError:
        pass
    else:
        setSite()
        setHooks()
    
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
