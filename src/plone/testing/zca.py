"""Core Zope Component Architecture helpers and layers
"""

from plone.testing import Layer

# Contains a stack of installed global registries (but not the default one)
_REGISTRIES = []

def loadRegistry(name):
    """Unpickling helper
    """
    for reg in reversed(_REGISTRIES):
        if reg.__name__ == name:
            return reg
    raise KeyError(name)

def _hookRegistry(reg):
    from zope.component import _api
    from zope.component import globalregistry
    
    _api.base = reg
    globalregistry.base = reg
    globalregistry.globalSiteManager = reg
    
    # Set the default global site manager for new threads when zope.site's
    # hooks are in place
    
    try:
        from zope.app.component.hooks import SiteInfo, siteinfo
    except ImportError:
        pass
    else:
        SiteInfo.sm = reg
        siteinfo.sm = reg

    # Set the five.localsitemanager hook, too, if applicable
    try:
        from five import localsitemanager
    except ImportError:
        pass
    else:
        localsitemanager.base = reg

# Helper functions

def pushGlobalRegistry(new=None):
    """Set a new global component registry that uses the current registry as
    a a base. If you use this, you *must* call ``popGlobalRegistry()`` to
    restore the original state.
    
    If ``new`` is not given, a new registry is created. If given, you must
    provide a ``zope.component.globalregistry.BaseGlobalComponents`` object.
    
    Returns the new registry.
    """
    
    from zope.component import globalregistry
    
    # Save the current top of the stack in a registry
    current = globalregistry.base
    
    # The first time we're called, we need to put the default global
    # registry at the bottom of the stack, and then patch the class to use
    # the stack for loading pickles. Otherwise, we end up with POSKey and
    # pickling errors when dealing with persistent registries that have the
    # global registry (globalregistry.base) as a baes
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
    _hookRegistry(new)
    
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
    
    _hookRegistry(previous)
    
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

def stackConfigurationContext(context=None):
    """Return a new ``ConfigurationMachine`` configuration context that 
    is a clone of the passed-in context. If no context is passed in, a fresh
    configuration context is returned.
    """
    
    from copy import deepcopy
    
    from zope.interface import Interface
    from zope.interface.adapter import AdapterRegistry
    
    from zope.configuration.config import ConfigurationMachine
    from zope.configuration.xmlconfig import registerCommonDirectives
    
    clone = ConfigurationMachine()
    
    # Prime this so that the <meta:redefinePermission /> directive won't lose
    # track of it across our stacked configuration machines
    clone.permission_mapping = {}
    
    if context is None:
        registerCommonDirectives(clone)
        return clone
    
    # Copy over simple attributes
    clone.info         = deepcopy(context.info)
    clone.i18n_strings = deepcopy(context.i18n_strings)
    clone.package      = deepcopy(context.package)
    clone.basepath     = deepcopy(context.basepath)
    clone.includepath  = deepcopy(context.includepath)
    
    clone._seen_files  = deepcopy(context._seen_files)
    clone._features    = deepcopy(context._features)
    
    if hasattr(context, 'permission_mapping'):
        clone.permission_mapping = deepcopy(context.permission_mapping)
    
    # Note: We don't copy ``stack`` or ``actions`` since these are used during
    # ZCML file processing only
    
    # Copy over documentation registry
    clone._docRegistry = [tuple(list(entry))for entry in context._docRegistry]
    
    # Copy over the directive registry
    for key, registry in context._registry.items():
        newRegistry = clone._registry.setdefault(key, AdapterRegistry())
        for adapterRegistration in registry._adapters:
            if adapterRegistration not in newRegistry._adapters:
                for interface, info in adapterRegistration.items():
                    if Interface in info:
                        factory = info[Interface][u'']
                        newRegistry.register([interface], Interface, '', factory)
    
    return clone
    
# Layers

class UnitTesting(Layer):
    """Zope Component Architecture unit testing sandbox: The ZCA is cleared
    for each test and torn down after each test.
    """
    
    defaultBases = ()
    
    def testSetUp(self):
        import zope.component.testing
        zope.component.testing.setUp()
    
    def testTearDown(self):
        import zope.component.testing
        zope.component.testing.tearDown()

UNIT_TESTING = UnitTesting()

class EventTesting(Layer):
    """Set up event testing for each test. This allows use of the helper
    function ``zope.component.eventtesting.getEvent()`` to obtain and inspect
    events fired during the test run.
    
    Since the ``Sandbox`` tear-down executes ``zope.testing.cleanup.cleanUp``,
    the event testing events list is emptied for each test.
    """
    
    defaultBases = (UNIT_TESTING,)
    
    def testSetUp(self):
        import zope.component.eventtesting
        zope.component.eventtesting.setUp()
    
EVENT_TESTING = EventTesting()

class LayerCleanup(Layer):
    """A base layer which uses ``zope.testing.cleanup`` to restore the
    state of the environment on test setup and cleanup.
    """
    
    defaultBases = ()
    
    def setUp(self):
        import zope.testing.cleanup
        zope.testing.cleanup.cleanUp()
    
    def tearDown(self):
        import zope.testing.cleanup
        zope.testing.cleanup.cleanUp()

LAYER_CLEANUP = LayerCleanup()

class ZCMLDirectives(Layer):
    """Enables the use of the basic ZCML directives from ``zope.component``.
    
    Exposes a ``zope.configuration`` configuration context as the resource
    ``configurationContext``.
    """
    
    defaultBases = (LAYER_CLEANUP,)
    
    def setUp(self):
        
        from zope.configuration import xmlconfig
        import zope.component
        
        self['configurationContext'] = context = stackConfigurationContext(self.get('configurationContext'))
        xmlconfig.file('meta.zcml', zope.component, context=context)
    
    def tearDown(self):
        del self['configurationContext']
    
ZCML_DIRECTIVES = ZCMLDirectives()
