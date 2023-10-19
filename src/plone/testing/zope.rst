Zope WSGI layers
----------------

The Zope WSGI layers are found in the module ``plone.testing.zope``:::

    >>> from plone.testing import zope

For testing, we need a testrunner:::

    >>> from zope.testrunner import runner

Startup
~~~~~~~

``STARTUP`` is the base layer for all Zope WSGI testing.
It sets up a Zope WSGI sandbox environment that is suitable for testing.
It extends the ``zca.LAYER_CLEANUP`` layer to maximise the chances of having and leaving a pristine environment.

**Note**: You should probably use at least ``INTEGRATION_TESTING`` for any real test, although ``STARTUP`` is a useful base layer if you are setting up your own fixture.
See the description of ``INTEGRATION_TESTING`` below.::

    >>> "%s.%s" % (zope.STARTUP.__module__, zope.STARTUP.__name__,)
    'plone.testing.zope.Startup'

    >>> zope.STARTUP.__bases__
    (<Layer 'plone.testing.zca.LayerCleanup'>,)

On layer setup, Zope is initialised in a lightweight manner.
This involves certain patches to global modules that Zope manages, to reduce setup time, a database based on ``DemoStorage``, and a minimal set of products that must be installed for Zope 2 to work.
A minimal set of ZCML is loaded, but packages in the ``Products`` namespace are not automatically configured.

Let's just verify that we have an empty component registry before the test:::

    >>> from zope.component import getSiteManager
    >>> list(getSiteManager().registeredAdapters())
    []

Five sets a special vocabulary registry upon the layer setup, but there's a default one set before:::

    >>> from zope.schema.vocabulary import getVocabularyRegistry
    >>> getVocabularyRegistry()
    <zope.schema.vocabulary.VocabularyRegistry object ...>

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zope.STARTUP, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.

After layer setup, the ``zodbDB`` resource is available, pointing to the default ZODB.::

    >>> zope.STARTUP['zodbDB']
    <ZODB.DB.DB object at ...>

    >>> zope.STARTUP['zodbDB'].storage
    Startup

In addition, the resources ``host`` and ``port`` are set to the default hostname and port that are used for URLs generated from Zope.
These are hardcoded, but shadowed by layers that provide actual running Zope instances.::

    >>> zope.STARTUP['host']
    'nohost'
    >>> zope.STARTUP['port']
    80

At this point, it is also possible to get hold of a Zope application root.
If you are setting up a layer fixture, you can obtain an application root with the correct database that is properly closed by using the ``zopeApp()`` context manager.::

    >>> with zope.zopeApp() as app:
    ...     'acl_users' in app.objectIds()
    True

If you want to use a specific database, you can pass that to ``zopeApp()`` as the ``db`` parameter.
A new connection will be opened and closed.::

    >>> with zope.zopeApp(db=zope.STARTUP['zodbDB']) as app:
    ...     'acl_users' in app.objectIds()
    True

If you want to reuse an existing connection, you can pass one to ``zopeApp()`` as the ``connection`` argument.
In this case, you will need to close the connection yourself.::

    >>> conn = zope.STARTUP['zodbDB'].open()
    >>> with zope.zopeApp(connection=conn) as app:
    ...     'acl_users' in app.objectIds()
    True

    >>> conn.opened is not None
    True

    >>> conn.close()

If an exception is raised within the ``with`` block, the transaction is aborted, but the connection is still closed (if it was opened by the context manager):::

    >>> with zope.zopeApp() as app:
    ...     raise Exception("Test error")
    Traceback (most recent call last):
    ...
    Exception: Test error

It is common to combine the ``zopeApp()`` context manager with a stacked ``DemoStorage`` to set up a layer-specific fixture.
As a sketch:::

    from plone.testing import Layer, zope, zodb

    class MyLayer(Layer):
        defaultBases = (zope.STARTUP,)

        def setUp(self):
            self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name='MyLayer')
            with zope.zopeApp() as app:

                # Set up a fixture, e.g.:
                app.manage_addFolder('folder1')
                folder = app['folder1']
                folder._addRole('role1')
                folder.manage_addUserFolder()

                userFolder = folder['acl_users']
                ignore = userFolder.userFolderAddUser('user1', 'secret', ['role1'], [])
                folder.manage_role('role1', ('Access contents information',))

        def tearDown(self):
            self['zodbDB'].close()
            del self['zodbDB']

Note that you would normally *not* use the ``zope.zopeApp()`` in a test or in a ``testSetUp()`` or ``testTearDown()`` method.
The ``IntegrationTesting`` and ``FunctionalTesting`` layer classes manage the application object for you, exposing them as the resource ``app`` (see below).

After layer setup, the global component registry contains a number of components needed by Zope.::

    >>> len(list(getSiteManager().registeredAdapters())) > 1 # in fact, > a lot
    True

And Five has set a ``Zope2VocabularyRegistry`` vocabulary registry:::

    >>> getVocabularyRegistry()
    <....Zope2VocabularyRegistry object at ...>

To load additional ZCML, you can use the ``configurationContext`` resource:::

    >>> zope.STARTUP['configurationContext']
    <zope.configuration.config.ConfigurationMachine object ...>

See ``zca.rst`` for details about how to use ``zope.configuration`` for this purpose.

The ``STARTUP`` layer does not perform any specific test setup or tear-down.
That is left up to the ``INTEGRATION_TESTING`` and ``FUNCTIONAL_TESTING`` layers, or other layers using their layer classes - ``IntegrationTesting`` and ``FunctionalTesting``.::

    >>> zope.STARTUP.testSetUp()
    >>> zope.STARTUP.testTearDown()

Layer tear-down resets the environment.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> import Zope2
    >>> Zope2._began_startup
    0
    >>> Zope2.DB is None
    True
    >>> Zope2.bobo_application is None
    True

    >>> list(getSiteManager().registeredAdapters())
    []

    >>> getVocabularyRegistry()
    <zope.schema.vocabulary.VocabularyRegistry object at ...>

Integration test
~~~~~~~~~~~~~~~~

``INTEGRATION_TESTING`` is intended for simple Zope WSGI integration testing.
It extends ``STARTUP`` to ensure that a transaction is begun before and rolled back after each test.
Two resources, ``app`` and ``request``, are available during testing as well.
It does not manage any layer state - it implements the test lifecycle methods only.

**Note:** You would normally *not* use ``INTEGRATION_TESTING`` as a base layer.
Instead, you'd use the ``IntegrationTesting`` class to create your own layer with the testing lifecycle semantics of ``INTEGRATION_TESTING``.
See the ``plone.testing`` ``README`` file for an example.

``app`` is the application root.
In a test, you should use this instead of the ``zopeApp`` context manager (which remains the weapon of choice for setting up persistent fixtures), because the ``app`` resource is part of the transaction managed by the layer.

``request`` is a test request. It is the same as ``app.REQUEST``.::

    >>> "%s.%s" % (zope.INTEGRATION_TESTING.__module__, zope.INTEGRATION_TESTING.__name__,)
    'plone.testing.zope.IntegrationTesting'

    >>> zope.INTEGRATION_TESTING.__bases__
    (<Layer 'plone.testing.zope.Startup'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zope.INTEGRATION_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.testing.zope.IntegrationTesting in ... seconds.

Let's now simulate a test.
On test setup, the ``app`` resource is made available.
In a test, you should always use this to access the application root.::

    >>> zope.STARTUP.testSetUp()
    >>> zope.INTEGRATION_TESTING.testSetUp()

The test may now inspect and modify the environment.::

    >>> app = zope.INTEGRATION_TESTING['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')
    >>> 'acl_users' in app.objectIds() and 'folder1' in app.objectIds()
    True

The request is also available:::

    >>> zope.INTEGRATION_TESTING['request'] # would normally be self.layer['request']
    <HTTPRequest, URL=http://nohost>

We can create a user and simulate logging in as that user, using the ``zope.login()`` helper:::

    >>> app._addRole('role1')
    >>> ignore = app['acl_users'].userFolderAddUser('user1', 'secret', ['role1'], [])
    >>> zope.login(app['acl_users'], 'user1')

The first argument to ``zope.login()`` is the user folder that contains the relevant user.
The second argument is the user's name.
There is no need to give the password.::

    >>> from AccessControl import getSecurityManager
    >>> getSecurityManager().getUser()
    <User 'user1'>

You can change the roles of a user using the ``zope.setRoles()`` helper:::

    >>> sorted(getSecurityManager().getUser().getRolesInContext(app))
    ['Authenticated', 'role1']

    >>> zope.setRoles(app['acl_users'], 'user1', [])
    >>> getSecurityManager().getUser().getRolesInContext(app)
    ['Authenticated']

To become the anonymous user again, use ``zope.logout()``:::

    >>> zope.logout()
    >>> getSecurityManager().getUser()
    <SpecialUser 'Anonymous User'>

On tear-down, the transaction is rolled back:::

    >>> zope.INTEGRATION_TESTING.testTearDown()
    >>> zope.STARTUP.testTearDown()

    >>> 'app' in zope.INTEGRATION_TESTING
    False

    >>> 'request' in zope.INTEGRATION_TESTING
    False

    >>> with zope.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True


Let's tear down the layers:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zope.IntegrationTesting in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

Functional testing
~~~~~~~~~~~~~~~~~~

The ``FUNCTIONAL_TESTING`` layer is very similar to ``INTEGRATION_TESTING``, and exposes the same fixture and resources.
However, it has different transaction semantics.
``INTEGRATION_TESTING`` creates a single database storage, and rolls back the transaction after each test.
``FUNCTIONAL_TESTING`` creates a whole new database storage (stacked on top of the basic fixture) for each test.
This allows testing of code that performs an explicit commit, which is usually required for end-to-end testing.
The downside is that the set-up and tear-down of each test takes longer.

**Note:** Again, you would normally *not* use ``FUNCTIONAL_TESTING`` as a base layer.
Instead, you'd use the ``FunctionalTesting`` class to create your own layer with the testing lifecycle semantics of ``FUNCTIONAL_TESTING``.
See the ``plone.testing`` ``README`` file for an example.

Like ``INTEGRATION_TESTING``, ``FUNCTIONAL_TESTING`` is based on ``STARTUP``.::

    >>> "%s.%s" % (zope.FUNCTIONAL_TESTING.__module__, zope.FUNCTIONAL_TESTING.__name__,)
    'plone.testing.zope.FunctionalTesting'

    >>> zope.FUNCTIONAL_TESTING.__bases__
    (<Layer 'plone.testing.zope.Startup'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zope.FUNCTIONAL_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.testing.zope.FunctionalTesting in ... seconds.

Let's now simulate a test.
On test setup, the ``app`` resource is made available.
In a test, you should always use this to access the application root.
The ``request`` resource can be used to access the test request.::

    >>> zope.STARTUP.testSetUp()
    >>> zope.FUNCTIONAL_TESTING.testSetUp()

The test may now inspect and modify the environment.
It may also commit things.::

    >>> app = zope.FUNCTIONAL_TESTING['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')
    >>> 'acl_users' in app.objectIds() and 'folder1' in app.objectIds()
    True

    >>> import transaction
    >>> transaction.commit()

On tear-down, the database is torn down.::

    >>> zope.FUNCTIONAL_TESTING.testTearDown()
    >>> zope.STARTUP.testTearDown()

    >>> 'app' in zope.FUNCTIONAL_TESTING
    False

    >>> 'request' in zope.FUNCTIONAL_TESTING
    False

    >>> with zope.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True

Let's tear down the layer:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zope.FunctionalTesting in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

The test browser
~~~~~~~~~~~~~~~~

The ``FUNCTIONAL_TESTING`` layer and ``FunctionalTesting`` layer class are the basis for functional testing using ``zope.testbrowser``.
This simulates a web browser, allowing an application to be tested "end-to-end" via its user-facing interface.

To use the test browser with a ``FunctionalTesting`` layer (such as the default ``FUNCTIONAL_TESTING`` layer instance), we need to use a custom browser client, which ensures that the test browser uses the correct ZODB and is appropriately isolated from the test code.::

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zope.FUNCTIONAL_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.testing.zope.FunctionalTesting in ... seconds.

Let's simulate a test:::

    >>> zope.STARTUP.testSetUp()
    >>> zope.FUNCTIONAL_TESTING.testSetUp()

In the test, we can create a test browser client like so:::

    >>> app = zope.FUNCTIONAL_TESTING['app'] # would normally be self.layer['app']
    >>> browser = zope.Browser(app)

It is usually best to let Zope errors be shown with full tracebacks:::

    >>> browser.handleErrors = False

We can add to the test fixture in the test.
For those changes to be visible to the test browser, however, we need to commit the transaction.::

    >>> _ = app.manage_addDTMLDocument('dtml-doc-1')
    >>> import transaction; transaction.commit()

We can now view this via the test browser:::

    >>> browser.open(app.absolute_url() + '/dtml-doc-1')
    >>> 'This is the dtml-doc-1 Document.' in browser.contents
    True

The test browser integration converts the URL into a request and passes control to Zope's publisher.
Let's check that query strings are available for input processing:::

    >>> from urllib.parse import urlencode
    >>> _ = app.manage_addDTMLDocument('dtml-doc-2', file='<dtml-var foo>')
    >>> import transaction; transaction.commit()
    >>> qs = urlencode({'foo': 'boo, bar & baz'})  # sic: the ampersand.
    >>> browser.open(app.absolute_url() + '/dtml-doc-2?' + qs)
    >>> browser.contents
    'boo, bar & baz'

The test browser also works with iterators.
Let's test that with a simple file implementation that uses an iterator.::

    >>> from plone.testing.tests import DummyFile
    >>> app._setObject('file1', DummyFile('file1'))
    'file1'

    >>> import transaction; transaction.commit()

    >>> browser.open(app.absolute_url() + '/file1')
    >>> 'The test browser also works with iterators' in browser.contents
    True

See the ``zope.testbrowser`` documentation for more information about how to use the browser client.

On tear-down, the database is torn down.::

    >>> zope.FUNCTIONAL_TESTING.testTearDown()
    >>> zope.STARTUP.testTearDown()

    >>> 'app' in zope.FUNCTIONAL_TESTING
    False

    >>> 'request' in zope.FUNCTIONAL_TESTING
    False

    >>> with zope.zopeApp() as app:
    ...     'acl_users' in app.objectIds()\
    ...         and 'folder1' not in app.objectIds()\
    ...         and 'file1' not in app.objectIds()
    True

Let's tear down the layer:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zope.FunctionalTesting in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

HTTP server
~~~~~~~~~~~

The ``WSGI_SERVER_FIXTURE`` layer extends ``STARTUP`` to start a single-threaded Zope server in a separate thread.
This makes it possible to connect to the test instance using a web browser or a testing tool like Selenium or Windmill.

The ``WSGI_SERVER`` layer provides a ``FunctionalTesting`` layer that has ``WSGI_SERVER_FIXTURE`` as its base.::

    >>> "%s.%s" % (zope.WSGI_SERVER_FIXTURE.__module__, zope.WSGI_SERVER_FIXTURE.__name__,)
    'plone.testing.zope.WSGIServer'

    >>> zope.WSGI_SERVER_FIXTURE.__bases__
    (<Layer 'plone.testing.zope.Startup'>,)


    >>> "%s.%s" % (zope.WSGI_SERVER.__module__, zope.WSGI_SERVER.__name__,)
    'plone.testing.zope.WSGIServer:Functional'

    >>> zope.WSGI_SERVER.__bases__
    (<Layer 'plone.testing.zope.WSGIServer'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zope.WSGI_SERVER, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.testing.zope.WSGIServer in ... seconds.
    Set up plone.testing.zope.WSGIServer:Functional in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and indicate where Zope is running.::

    >>> host = zope.WSGI_SERVER['host']
    >>> host
    'localhost'

    >>> port = zope.WSGI_SERVER['port']

Let's now simulate a test.
Test setup does nothing beyond what the base layers do.::

    >>> zope.STARTUP.testSetUp()
    >>> zope.FUNCTIONAL_TESTING.testSetUp()
    >>> zope.WSGI_SERVER.testSetUp()

It is common in a test to use the Python API to change the state of the server (e.g.
create some content or change a setting) and then use the HTTP protocol to look at the results.
Bear in mind that the server is running in a separate thread, with a separate security manager, so calls to ``zope.login()`` and ``zope.logout()``, for instance, do not affect the server thread.::

    >>> app = zope.WSGI_SERVER['app'] # would normally be self.layer['app']
    >>> _ = app.manage_addDTMLDocument('dtml-doc-3')

Note that we need to commit the transaction before it will show up in the other thread.::

    >>> import transaction; transaction.commit()

We can now look for this new object through the server.::

    >>> app_url = app.absolute_url()
    >>> app_url.split(':')[:-1]
    ['http', '//localhost']

    >>> from urllib.request import urlopen
    >>> conn = urlopen(app_url + '/dtml-doc-3', timeout=5)
    >>> b'This is the dtml-doc-3 Document.' in conn.read()
    True
    >>> conn.close()

Test tear-down does nothing beyond what the base layers do.::

    >>> zope.WSGI_SERVER.testTearDown()
    >>> zope.FUNCTIONAL_TESTING.testTearDown()
    >>> zope.STARTUP.testTearDown()

    >>> 'app' in zope.WSGI_SERVER
    False

    >>> 'request' in zope.WSGI_SERVER
    False

    >>> with zope.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True

When the server is torn down, the WSGIServer thread is stopped.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zope.WSGIServer:Functional in ... seconds.
    Tear down plone.testing.zope.WSGIServer in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

We can expect one of these exceptions:
- URLError: <urlopen error [Errno ...] Connection refused>
- error: [Errno 104] Connection reset by peer

    >>> try:
    ...     conn = urlopen(app_url + '/folder1', timeout=5)
    ... except Exception as exc:
    ...     if 'Connection refused' not in str(exc) and 'Connection reset' not in str(exc):
    ...         raise exc
    ... else:
    ...     print('urlopen should have raised exception')
