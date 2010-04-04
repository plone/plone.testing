"""Core Zope Component Architecture helpers and layers
"""

from plone.testing import Layer

class Sandbox(Layer):
    """Zope Component Architecture sandbox: The ZCA is cleared for each
    test and torn down after each test.
    """
    
    def setUpTest(self):
        import zope.component.testing
        zope.component.testing.setUp()
    
    def tearDownTest(self):
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
    
    __bases__ = (SANDBOX,)
    
    def setUpTest(self):
        import zope.component.eventtesting
        zope.component.eventtesting.setUp()
    
EVENT_TESTING = EventTesting()

class ZCMLDirectives(Layer):
    """Enables the use of the basic ZCML directives from ``zope.component``.
    
    Exposes a ``zope.configuration`` configuration context as the resource
    ``configurationContext``. If such a resource exists already, it will be
    re-used. Otherwise, a new one is created.
    """
    
    __bases__ = (SANDBOX,)
    
    def setUp(self):
        
        from zope.configuration import xmlconfig
        import zope.component
        
        context = self['configurationContext']
        if context is not None:
            xmlconfig.file(
                    'meta.zcml',
                    zope.component,
                    context=context
                )
        else:
            self['configurationContext'] = xmlconfig.file(
                    'meta.zcml',
                    zope.component
                )
    
ZCML_DIRECTIVES = ZCMLDirectives()
