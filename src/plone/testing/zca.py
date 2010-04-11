"""Core Zope Component Architecture helpers and layers
"""

from plone.testing import Layer

class Sandbox(Layer):
    """Zope Component Architecture sandbox: The ZCA is cleared for each
    test and torn down after each test.
    """
    
    __bases__ = ()
    
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
    
    __bases__ = (SANDBOX,)
    
    def testSetUp(self):
        import zope.component.eventtesting
        zope.component.eventtesting.setUp()
    
EVENT_TESTING = EventTesting()

class ZCMLDirectives(Layer):
    """Enables the use of the basic ZCML directives from ``zope.component``.
    
    Exposes a ``zope.configuration`` configuration context as the resource
    ``configurationContext``.
    """
    
    __bases__ = ()
    
    def setUp(self):
        
        from zope.configuration import xmlconfig
        import zope.component
        
        self['configurationContext'] = xmlconfig.file('meta.zcml', zope.component)
    
    def tearDown(self):
        del self['configurationContext']
    
ZCML_DIRECTIVES = ZCMLDirectives()
