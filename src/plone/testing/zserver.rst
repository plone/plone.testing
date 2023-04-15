Zope 2 layers
-------------

The Zope 2 layers are found in the module ``plone.testing.zserver``:::

    >>> from plone.testing import zserver

For testing, we need a testrunner:::

    >>> from zope.testrunner import runner

Startup
~~~~~~~

``STARTUP`` is the base layer for all Zope 2 testing.
It sets up a Zope 2 sandbox environment that is suitable for testing.
It extends the ``zca.LAYER_CLEANUP`` layer to maximise the chances of having and leaving a pristine environment.

**Note**: You should probably use at least ``INTEGRATION_TESTING`` for any real test, although ``STARTUP`` is a useful base layer if you are setting up your own fixture.
See the description of ``INTEGRATION_TESTING`` below.::

    >>> "%s.%s" % (zserver.STARTUP.__module__, zserver.STARTUP.__name__,)
    'plone.testing.zserver.Startup'

    >>> zserver.STARTUP.__bases__
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
    >>> runner.setup_layer(options, zserver.STARTUP, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.

After layer setup, the ``zodbDB`` resource is available, pointing to the default ZODB.::

    >>> zserver.STARTUP['zodbDB']
    <ZODB.DB.DB object at ...>

    >>> zserver.STARTUP['zodbDB'].storage
    Startup

In addition, the resources ``host`` and ``port`` are set to the default hostname and port that are used for URLs generated from Zope.
These are hardcoded, but shadowed by layers that provide actual running Zope instances.::

    >>> zserver.STARTUP['host']
    'nohost'
    >>> zserver.STARTUP['port']
    80

At this point, it is also possible to get hold of a Zope application root.
If you are setting up a layer fixture, you can obtain an application root with the correct database that is properly closed by using the ``zopeApp()`` context manager.::

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds()
    True

If you want to use a specific database, you can pass that to ``zopeApp()`` as the ``db`` parameter.
A new connection will be opened and closed.::

    >>> with zserver.zopeApp(db=zserver.STARTUP['zodbDB']) as app:
    ...     'acl_users' in app.objectIds()
    True

If you want to reuse an existing connection, you can pass one to ``zopeApp()`` as the ``connection`` argument.
In this case, you will need to close the connection yourself.::

    >>> conn = zserver.STARTUP['zodbDB'].open()
    >>> with zserver.zopeApp(connection=conn) as app:
    ...     'acl_users' in app.objectIds()
    True

    >>> conn.opened is not None
    True

    >>> conn.close()

If an exception is raised within the ``with`` block, the transaction is aborted, but the connection is still closed (if it was opened by the context manager):::

    >>> with zserver.zopeApp() as app:
    ...     raise Exception("Test error")
    Traceback (most recent call last):
    ...
    Exception: Test error

It is common to combine the ``zopeApp()`` context manager with a stacked ``DemoStorage`` to set up a layer-specific fixture.
As a sketch:::

    from plone.testing import Layer, zserver, zodb

    class MyLayer(Layer):
        defaultBases = (zserver.STARTUP,)

        def setUp(self):
            self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name='MyLayer')
            with zserver.zopeApp() as app:

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

Note that you would normally *not* use the ``zserver.zopeApp()`` in a test or in a ``testSetUp()`` or ``testTearDown()`` method.
The ``IntegrationTesting`` and ``FunctionalTesting`` layer classes manage the application object for you, exposing them as the resource ``app`` (see below).

After layer setup, the global component registry contains a number of components needed by Zope.::

    >>> len(list(getSiteManager().registeredAdapters())) > 1 # in fact, > a lot
    True

And Five has set a ``Zope2VocabularyRegistry`` vocabulary registry:::

    >>> getVocabularyRegistry()
    <....Zope2VocabularyRegistry object at ...>

To load additional ZCML, you can use the ``configurationContext`` resource:::

    >>> zserver.STARTUP['configurationContext']
    <zope.configuration.config.ConfigurationMachine object ...>

See ``zca.rst`` for details about how to use ``zope.configuration`` for this purpose.

The ``STARTUP`` layer does not perform any specific test setup or tear-down.
That is left up to the ``INTEGRATION_TESTING`` and ``FUNCTIONAL_TESTING`` layers, or other layers using their layer classes - ``IntegrationTesting`` and ``FunctionalTesting``.::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.STARTUP.testTearDown()

Layer tear-down resets the environment.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> import ZServer.Zope2
    >>> ZServer.Zope2._began_startup
    0
    >>> import Zope2
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

``INTEGRATION_TESTING`` is intended for simple Zope 2 integration testing.
It extends ``STARTUP`` to ensure that a transaction is begun before and rolled back after each test.
Two resources, ``app`` and ``request``, are available during testing as well.
It does not manage any layer state - it implements the test lifecycle methods only.

**Note:** You would normally *not* use ``INTEGRATION_TESTING`` as a base layer.
Instead, you'd use the ``IntegrationTesting`` class to create your own layer with the testing lifecycle semantics of ``INTEGRATION_TESTING``.
See the ``plone.testing`` ``README`` file for an example.

``app`` is the application root.
In a test, you should use this instead of the ``zopeApp`` context manager (which remains the weapon of choice for setting up persistent fixtures), because the ``app`` resource is part of the transaction managed by the layer.

``request`` is a test request. It is the same as ``app.REQUEST``.::

    >>> "%s.%s" % (zserver.INTEGRATION_TESTING.__module__, zserver.INTEGRATION_TESTING.__name__,)
    'plone.testing.zserver.IntegrationTesting'

    >>> zserver.INTEGRATION_TESTING.__bases__
    (<Layer 'plone.testing.zserver.Startup'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zserver.INTEGRATION_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.testing.zserver.IntegrationTesting in ... seconds.

Let's now simulate a test.
On test setup, the ``app`` resource is made available.
In a test, you should always use this to access the application root.::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.INTEGRATION_TESTING.testSetUp()

The test may now inspect and modify the environment.::

    >>> app = zserver.INTEGRATION_TESTING['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')
    >>> 'acl_users' in app.objectIds() and 'folder1' in app.objectIds()
    True

The request is also available:::

    >>> zserver.INTEGRATION_TESTING['request'] # would normally be self.layer['request']
    <HTTPRequest, URL=http://nohost>

We can create a user and simulate logging in as that user, using the ``zserver.login()`` helper:::

    >>> app._addRole('role1')
    >>> ignore = app['acl_users'].userFolderAddUser('user1', 'secret', ['role1'], [])
    >>> zserver.login(app['acl_users'], 'user1')

The first argument to ``zserver.login()`` is the user folder that contains the relevant user.
The second argument is the user's name.
There is no need to give the password.::

    >>> from AccessControl import getSecurityManager
    >>> getSecurityManager().getUser()
    <User 'user1'>

You can change the roles of a user using the ``zserver.setRoles()`` helper:::

    >>> sorted(getSecurityManager().getUser().getRolesInContext(app))
    ['Authenticated', 'role1']

    >>> zserver.setRoles(app['acl_users'], 'user1', [])
    >>> getSecurityManager().getUser().getRolesInContext(app)
    ['Authenticated']

To become the anonymous user again, use ``zserver.logout()``:::

    >>> zserver.logout()
    >>> getSecurityManager().getUser()
    <SpecialUser 'Anonymous User'>

On tear-down, the transaction is rolled back:::

    >>> zserver.INTEGRATION_TESTING.testTearDown()
    >>> zserver.STARTUP.testTearDown()

    >>> 'app' in zserver.INTEGRATION_TESTING
    False

    >>> 'request' in zserver.INTEGRATION_TESTING
    False

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True


Let's tear down the layers:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.IntegrationTesting in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
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

    >>> "%s.%s" % (zserver.FUNCTIONAL_TESTING.__module__, zserver.FUNCTIONAL_TESTING.__name__,)
    'plone.testing.zserver.FunctionalTesting'

    >>> zserver.FUNCTIONAL_TESTING.__bases__
    (<Layer 'plone.testing.zserver.Startup'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zserver.FUNCTIONAL_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.testing.zserver.FunctionalTesting in ... seconds.

Let's now simulate a test.
On test setup, the ``app`` resource is made available.
In a test, you should always use this to access the application root.
The ``request`` resource can be used to access the test request.::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.FUNCTIONAL_TESTING.testSetUp()

The test may now inspect and modify the environment.
It may also commit things.::

    >>> app = zserver.FUNCTIONAL_TESTING['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')
    >>> 'acl_users' in app.objectIds() and 'folder1' in app.objectIds()
    True

    >>> import transaction
    >>> transaction.commit()

On tear-down, the database is torn down.::

    >>> zserver.FUNCTIONAL_TESTING.testTearDown()
    >>> zserver.STARTUP.testTearDown()

    >>> 'app' in zserver.FUNCTIONAL_TESTING
    False

    >>> 'request' in zserver.FUNCTIONAL_TESTING
    False

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True

Let's tear down the layer:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.FunctionalTesting in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

The test browser
~~~~~~~~~~~~~~~~

The ``FUNCTIONAL_TESTING`` layer and ``FunctionalTesting`` layer class are the basis for functional testing using ``zope.testbrowser``.
This simulates a web browser, allowing an application to be tested "end-to-end" via its user-facing interface.

To use the test browser with a ``FunctionalTesting`` layer (such as the default ``FUNCTIONAL_TESTING`` layer instance), we need to use a custom browser client, which ensures that the test browser uses the correct ZODB and is appropriately isolated from the test code.::

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zserver.FUNCTIONAL_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.testing.zserver.FunctionalTesting in ... seconds.

Let's simulate a test:::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.FUNCTIONAL_TESTING.testSetUp()

In the test, we can create a test browser client like so:::

    >>> app = zserver.FUNCTIONAL_TESTING['app'] # would normally be self.layer['app']
    >>> browser = zserver.Browser(app)

It is usually best to let Zope errors be shown with full tracebacks:::

    >>> browser.handleErrors = False

We can add to the test fixture in the test.
For those changes to be visible to the test browser, however, we need to commit the transaction.::

    >>> app.manage_addFolder('folder1')
    >>> import transaction; transaction.commit()

We can now view this via the test browser:::

    >>> browser.open(app.absolute_url() + '/folder1')

    >>> browser.contents.replace('"', '').replace("'", "")
    '<Folder ...'

The __repr__ of Zope objects is not stable anymore.

The test browser integration converts the URL into a request and passes control to Zope's publisher.
Let's check that query strings are available for input processing:::

    >>> import urllib
    >>> qs = urllib.urlencode({'foo': 'boo, bar & baz'})  # sic: the ampersand.
    >>> _ = app['folder1'].addDTMLMethod('index_html', file='<dtml-var foo>')
    >>> import transaction; transaction.commit()
    >>> browser.open(app.absolute_url() + '/folder1?' + qs)
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

    >>> zserver.FUNCTIONAL_TESTING.testTearDown()
    >>> zserver.STARTUP.testTearDown()

    >>> 'app' in zserver.FUNCTIONAL_TESTING
    False

    >>> 'request' in zserver.FUNCTIONAL_TESTING
    False

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds()\
    ...         and 'folder1' not in app.objectIds()\
    ...         and 'file1' not in app.objectIds()
    True

Let's tear down the layer:::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.FunctionalTesting in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

HTTP server
~~~~~~~~~~~

The ``ZSERVER_FIXTURE`` layer extends ``STARTUP`` to start a single-threaded Zope server in a separate thread.
This makes it possible to connect to the test instance using a web browser or a testing tool like Selenium or Windmill.

The ``ZSERVER`` layer provides a ``FunctionalTesting`` layer that has ``ZSERVER_FIXTURE`` as its base.::

    >>> "%s.%s" % (zserver.ZSERVER_FIXTURE.__module__, zserver.ZSERVER_FIXTURE.__name__,)
    'plone.testing.zserver.ZServer'

    >>> zserver.ZSERVER_FIXTURE.__bases__
    (<Layer 'plone.testing.zserver.Startup'>,)


    >>> "%s.%s" % (zserver.ZSERVER.__module__, zserver.ZSERVER.__name__,)
    'plone.testing.zserver.ZServer:Functional'

    >>> zserver.ZSERVER.__bases__
    (<Layer 'plone.testing.zserver.ZServer'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zserver.ZSERVER, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.testing.zserver.ZServer in ... seconds.
    Set up plone.testing.zserver.ZServer:Functional in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and indicate where Zope is running.::

    >>> host = zserver.ZSERVER['host']
    >>> port = zserver.ZSERVER['port']

Let's now simulate a test.
Test setup does nothing beyond what the base layers do.::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.FUNCTIONAL_TESTING.testSetUp()
    >>> zserver.ZSERVER.testSetUp()

It is common in a test to use the Python API to change the state of the server (e.g.
create some content or change a setting) and then use the HTTP protocol to look at the results.
Bear in mind that the server is running in a separate thread, with a separate security manager, so calls to ``zserver.login()`` and ``zserver.logout()``, for instance, do not affect the server thread.::

    >>> app = zserver.ZSERVER['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')

Note that we need to commit the transaction before it will show up in the other thread.::

    >>> import transaction; transaction.commit()

We can now look for this new object through the server.::

    >>> app_url = app.absolute_url()
    >>> app_url.split(':')[:-1]
    ['http', '//localhost']

    >>> import urllib2
    >>> conn = urllib2.urlopen(app_url + '/folder1', timeout=5)
    >>> conn.read().replace('"', '').replace("'", "")
    '<Folder ...'
    >>> conn.close()

The __repr__ of Zope objects is not stable anymore.

Test tear-down does nothing beyond what the base layers do.::

    >>> zserver.ZSERVER.testTearDown()
    >>> zserver.FUNCTIONAL_TESTING.testTearDown()
    >>> zserver.STARTUP.testTearDown()

    >>> 'app' in zserver.ZSERVER
    False

    >>> 'request' in zserver.ZSERVER
    False

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True

When the server is torn down, the ZServer thread is stopped.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.ZServer:Functional in ... seconds.
    Tear down plone.testing.zserver.ZServer in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

We can expect one of these exceptions:
- URLError: <urlopen error [Errno ...] Connection refused>
- error: [Errno 104] Connection reset by peer

    >>> try:
    ...     conn = urllib2.urlopen(app_url + '/folder1', timeout=5)
    ... except Exception as exc:
    ...     if 'Connection refused' not in str(exc) and 'Connection reset' not in str(exc):
    ...         raise exc
    ... else:
    ...     print('urllib2.urlopen should have raised exception')


FTP server
~~~~~~~~~~

The ``FTP_SERVER`` layer is identical similar to ``ZSERVER``, except that it starts an FTP server instead of an HTTP server.
The fixture is contained in the ``FTP_SERVER_FIXTURE`` layer.

    **Warning:** It is generally not safe to run the ``ZSERVER`` and ``FTP_SERVER`` layers concurrently, because they both start up the same ``asyncore`` loop.
    If you need concurrent HTTP and FTP servers in a test, you can create your own layer by subclassing the ``ZServer`` layer class, and overriding the ``setUpServer()`` and ``tearDownServer()`` hooks to set up and close both servers.
    See the code for an example.

The ``FTP_SERVER_FIXTURE`` layer is based on the ``STARTUP`` layer.::

    >>> "%s.%s" % (zserver.FTP_SERVER_FIXTURE.__module__, zserver.FTP_SERVER_FIXTURE.__name__,)
    'plone.testing.zserver.FTPServer'

    >>> zserver.FTP_SERVER_FIXTURE.__bases__
    (<Layer 'plone.testing.zserver.Startup'>,)

The ``FTP_SERVER`` layer is based on ``FTP_SERVER_FIXTURE``, using the ``FunctionalTesting`` layer class.::

    >>> "%s.%s" % (zserver.FTP_SERVER.__module__, zserver.FTP_SERVER.__name__,)
    'plone.testing.zserver.FTPServer:Functional'

    >>> zserver.FTP_SERVER.__bases__
    (<Layer 'plone.testing.zserver.FTPServer'>,)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zserver.FTP_SERVER, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.testing.zserver.FTPServer in ... seconds.
    Set up plone.testing.zserver.FTPServer:Functional in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and indicate where Zope is running.::

    >>> host = zserver.FTP_SERVER['host']
    >>> port = zserver.FTP_SERVER['port']

Let's now simulate a test.
Test setup does nothing beyond what the base layers do.::

    >>> zserver.STARTUP.testSetUp()
    >>> zserver.FUNCTIONAL_TESTING.testSetUp()
    >>> zserver.FTP_SERVER.testSetUp()

As with ``ZSERVER``, we will set up some content for the test and then access it over the FTP port.::

    >>> app = zserver.FTP_SERVER['app'] # would normally be self.layer['app']
    >>> app.manage_addFolder('folder1')

We'll also create a user in the root user folder to make FTP access easier.::

    >>> ignore = app['acl_users'].userFolderAddUser('admin', 'secret', ['Manager'], ())

Note that we need to commit the transaction before it will show up in the other thread.::

    >>> import transaction; transaction.commit()

We can now look for this new object through the server.::

    >>> app_path = app.absolute_url_path()

    >>> import ftplib
    >>> ftpClient = ftplib.FTP()
    >>> ftpClient.connect(host, port, timeout=5)
    '220 ... FTP server (...) ready.'

    >>> ftpClient.login('admin', 'secret')
    '230 Login successful.'

    >>> ftpClient.cwd(app_path)
    '250 CWD command successful.'

    >>> ftpClient.retrlines('LIST')
    drwxrwx---   1 Zope     Zope            0 ... .
    ...--w--w----   1 Zope     Zope            0 ... acl_users
    drwxrwx---   1 Zope     Zope            0 ... folder1
    '226 Transfer complete'

    >>> ftpClient.quit()
    '221 Goodbye.'

Test tear-down does nothing beyond what the base layers do.::

    >>> zserver.FTP_SERVER.testTearDown()
    >>> zserver.FUNCTIONAL_TESTING.testTearDown()
    >>> zserver.STARTUP.testTearDown()

    >>> 'app' in zserver.ZSERVER
    False

    >>> 'request' in zserver.ZSERVER
    False

    >>> with zserver.zopeApp() as app:
    ...     'acl_users' in app.objectIds() and 'folder1' not in app.objectIds()
    True

When the server is torn down, the FTP thread is stopped.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zserver.FTPServer:Functional in ... seconds.
    Tear down plone.testing.zserver.FTPServer in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> ftpClient.connect(host, port, timeout=5)
    Traceback (most recent call last):
    ...
    error: [Errno ...] Connection refused
