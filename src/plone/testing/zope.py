# -*- coding: utf-8 -*-
"""Zope-specific helpers and layers using WSGI
"""
from __future__ import absolute_import
from OFS.metaconfigure import get_packages_to_initialize
from plone.testing import Layer
from plone.testing import zca
from plone.testing import zodb
from plone.testing._z2_testbrowser import Browser  # noqa
from Testing.ZopeTestCase.ZopeLite import _patched as ZOPETESTCASEALERT
from Zope2.App.schema import Zope2VocabularyRegistry
from zope.schema.vocabulary import getVocabularyRegistry
from zope.schema.vocabulary import setVocabularyRegistry

import contextlib
import os
import pkg_resources
import shutil
import tempfile
import threading
import transaction
import wsgiref.simple_server
import Zope2.Startup.run
import ZPublisher.WSGIPublisher


_INSTALLED_PRODUCTS = {}


class TestIsolationBroken(BaseException):
    pass


def installProduct(app, productName, quiet=False, multiinit=False):
    """Install the Zope 2 product with the given name, so that it will show
    up in the Zope 2 control panel and have its ``initialize()`` hook called.

    The ``STARTUP`` layer or an equivalent layer must have been loaded first.

    If ``quiet`` is False, an error will be logged if the product cannot be
    found. By default, the function is silent.

    Note that products' ZCML is *not* loaded automatically, even if the
    product is in the Products namespace.
    """
    from App.class_init import InitializeClass
    from OFS.Application import get_folder_permissions
    from OFS.Application import get_products
    from OFS.Application import install_package
    from OFS.Application import install_product
    from OFS.Folder import Folder
    import sys

    found = False

    if productName in _INSTALLED_PRODUCTS:
        return

    if productName.startswith('Products.'):
        for priority, name, index, productDir in get_products():
            if ('Products.' + name) == productName:

                install_product(
                    app,
                    productDir,
                    name,
                    [],
                    get_folder_permissions(),
                    raise_exc=1)
                InitializeClass(Folder)

                _INSTALLED_PRODUCTS[productName] = (
                    priority,
                    name,
                    index,
                    productDir,
                )

                found = True
                break

    else:
        packages = tuple(get_packages_to_initialize())
        for module, init_func in packages:
            if module.__name__ == productName:
                install_package(app, module, init_func, raise_exc=1)
                _INSTALLED_PRODUCTS[productName] = (module, init_func,)

                found = True
                if not multiinit:
                    break

    if not found and not quiet:
        sys.stderr.write(
            'Could not install product {0}\n'.format(productName))
        sys.stderr.flush()


def uninstallProduct(app, productName, quiet=False):
    """Uninstall the given Zope 2 product. This is the inverse of
    ``installProduct()`` above.
    """

    import sys

    # from OFS.Folder import Folder
    # from OFS.Application import get_folder_permissions
    # from App.class_init import InitializeClass

    from OFS.Application import Application, get_products

    global _INSTALLED_PRODUCTS
    found = False

    if productName not in _INSTALLED_PRODUCTS:
        return

    if productName.startswith('Products.'):
        for priority, name, index, productDir in get_products():
            if ('Products.' + name) == productName:

                if name in Application.misc_.__dict__:
                    delattr(Application.misc_, name)

                # TODO: Also remove permissions from get_folder_permissions?
                # Difficult to know if this would stomp on any other
                # permissions
                # InitializeClass(Folder)

                found = True
                break
    elif productName in _INSTALLED_PRODUCTS:  # must be a package

        module, init_func = _INSTALLED_PRODUCTS[productName]
        name = module.__name__

        packages = get_packages_to_initialize()
        packages.append((module, init_func))
        found = True

    if found:
        del _INSTALLED_PRODUCTS[productName]

    if not found and not quiet:
        sys.stderr.write(
            'Could not install product {0}\n'.format(productName))
        sys.stderr.flush()


def login(userFolder, userName):
    """Log in as the given user in the given user folder.
    """

    from AccessControl.SecurityManagement import newSecurityManager

    user = userFolder.getUser(userName)
    if user is None:
        raise ValueError('User could not be found')
    if getattr(user, 'aq_base', None) is None:
        user = user.__of__(userFolder)
    newSecurityManager(None, user)


def logout():
    """Log out, i.e. become anonymous
    """

    from AccessControl.SecurityManagement import noSecurityManager
    noSecurityManager()


def setRoles(userFolder, userId, roles):
    """Set the given user's roles to a tuple of roles.
    """

    userFolder.userFolderEditUser(userId, None, list(roles), [])

    from AccessControl import getSecurityManager
    userName = userFolder.getUserById(userId).getUserName()
    if userName == getSecurityManager().getUser().getUserName():
        login(userFolder, userName)


def makeTestRequest(environ=None):
    """Return an HTTPRequest object suitable for testing views."""
    from sys import stdin, stdout
    from zope.publisher.browser import setDefaultSkin
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse

    if environ is None:
        environ = {}
    environ.setdefault('SERVER_NAME', 'foo')
    environ.setdefault('SERVER_PORT', '80')
    environ.setdefault('REQUEST_METHOD', 'GET')

    resp = HTTPResponse(stdout=stdout)
    req = HTTPRequest(stdin, environ, resp)
    req._steps = ['noobject']  # Fake a published object.
    req['ACTUAL_URL'] = req.get('URL')
    setDefaultSkin(req)

    return req


def addRequestContainer(app, environ=None):
    """Add the request container with a fake request to the app object's
    acquisition context and return the wrapped app object. Additional request
    environment values can be passed as a dict ``environ``.
    """

    from ZPublisher.BaseRequest import RequestContainer
    req = makeTestRequest(environ)
    requestcontainer = RequestContainer(REQUEST=req)
    return app.__of__(requestcontainer)


@contextlib.contextmanager
def zopeApp(db=None, connection=None, environ=None):
    """Context manager for working with the Zope2 app::

        with zopeApp() as app:
            ...

    The ``app`` object has a request container and a simple ``REQUEST``.
    To set the request environment, pass a dict ``environ``. See
    ``addRequestContainer()`` for details.

    Pass a ZODB handle as ``db`` to use a specificdatabase. Alternatively,
    pass an open connection as ``connection`` (the connection will not be
    closed).
    """
    import Zope2

    closeConn = True
    if connection is not None:
        closeConn = False

    if connection is None and db is not None:
        connection = db.open()

    assert Zope2._began_startup, \
        "Zope2 WSGI is not started, maybe mixing Zope and ZServer layers."
    app = addRequestContainer(Zope2.app(connection), environ=environ)

    if connection is None:
        connection = app._p_jar

    # exceptions in finally clauses can mask exceptions
    # in the preceeding code block. So we catch
    # every exception and throw it instead of the exception
    # in the finally clause
    inner_exception = None
    try:
        yield app
    except Exception as e:
        inner_exception = e
        try:
            transaction.abort()
        except Exception as e:
            inner_exception = e
            raise
        raise
    else:
        try:
            transaction.commit()
        except Exception as e:
            inner_exception = e
    finally:
        try:
            app.REQUEST.close()
            if closeConn:
                transaction.abort()
                connection.close()
        except Exception:
            if inner_exception:
                raise inner_exception
            else:
                raise


# Startup layer - you probably don't want to use this one directly

class Startup(Layer):
    """This layer does what ZopeLite and ZopeTestCase's base.TestCase did:
    start up a minimal Zope instance and manages the application and
    request state.

    You probably don't want to use this layer directly. Instead, you should
    use one of the layers that has it as a base.

    The following resources are exposed:

    * ``zodbDB`` is the ZODB with the test fixture
    * ``configurationContext`` is the ``zope.configuration`` context for
      ZCML loading.
    * ``host`` and ``port`` are the fake hostname and port number,
      respectively.
    """

    defaultBases = (zca.LAYER_CLEANUP,)

    threads = 1

    # Layer lifecycle

    def setUp(self):
        self.setUpDebugMode()
        self.setUpClientCache()
        self.setUpPatches()
        self.setUpThreads()
        self.setUpHostPort()
        self.setUpDatabase()
        self.setUpApp()
        self.setUpBasicProducts()
        self.setUpZCML()
        self.setUpFive()

    def tearDown(self):
        self.tearDownFive()
        self.tearDownZCML()
        self.tearDownBasicProducts()
        self.tearDownApp()
        self.tearDownDatabase()
        self.tearDownHostPort()
        self.tearDownThreads()
        self.tearDownPatches()
        self.tearDownClientCache()
        self.tearDownDebugMode()

    # Layer lifecycle helper methods

    def setUpDebugMode(self):
        """Switch off debug mode in the global configuration
        """

        import App.config
        config = App.config.getConfiguration()
        self._debugMode = config.debug_mode
        config.debug_mode = False
        App.config.setConfiguration(config)

        # Set Python security mode
        from AccessControl.Implementation import setImplementation
        setImplementation('Python')

        # Set a flag so that other code can know that we are running tests.
        # Some of the speed-related patches in Plone use this, for instance.
        # The name is a BBB artefact from ZopeTestCase :
        import os
        os.environ['ZOPETESTCASE'] = '1'

    def tearDownDebugMode(self):
        """Return the debug mode flag to its previous state
        """

        from AccessControl.Implementation import setImplementation
        setImplementation('C')

        import App.config
        config = App.config.getConfiguration()
        config.debug_mode = self._debugMode
        App.config.setConfiguration(config)
        del self._debugMode

    def setUpClientCache(self):
        """Make sure we use a temporary client cache by altering the global
        configuration
        """

        # Make sure we use a temporary client cache
        import App.config
        config = App.config.getConfiguration()
        self._zeoClientName = getattr(config, 'zeo_client_name', None)
        config.zeo_client_name = None
        App.config.setConfiguration(config)

    def tearDownClientCache(self):
        """Restore the cache configuration to its previous state
        """

        # Make sure we use a temporary client cache
        import App.config
        config = App.config.getConfiguration()
        config.zeo_client_name = self._zeoClientName
        App.config.setConfiguration(config)
        del self._zeoClientName

    def setUpPatches(self):
        """Apply monkey patches that disable unnecessary parts of Zope.
        This speeds up the test runs.
        """

        import OFS.Application
        import Zope2.App.startup

        # Avoid expensive product import
        def null_import_products():
            pass
        self._OFS_Application_import_products = OFS.Application.import_products
        OFS.Application.import_products = null_import_products

        # Avoid expensive product installation
        def null_initialize(app):
            pass
        self._OFS_Application_initialize = OFS.Application.initialize
        OFS.Application.initialize = null_initialize

        # Prevent ZCML from loading during App startup:
        self._Zope2_App_startup_load_zcml = Zope2.App.startup.load_zcml

        def null_load_zcml():
            pass

        Zope2.App.startup.load_zcml = null_load_zcml

    def tearDownPatches(self):
        """Revert the monkey patches from setUpPatches()
        """

        import OFS.Application

        OFS.Application.import_products = self._OFS_Application_import_products
        del self._OFS_Application_import_products

        OFS.Application.initialize = self._OFS_Application_initialize
        del self._OFS_Application_initialize

        Zope2.App.startup.load_zcml = self._Zope2_App_startup_load_zcml

    def setUpThreads(self):
        """Set the thread count. Only needed in ZServer.
        """
        pass

    def tearDownThreads(self):
        """Reset the thread count. Only needed in ZServer.
        """
        pass

    def setUpHostPort(self):
        """Set up the 'host' and 'port' resources
        """

        self['host'] = 'nohost'
        self['port'] = 80

    def tearDownHostPort(self):
        """Pop the 'host' and 'port' resources
        """

        del self['host']
        del self['port']

    def setUpDatabase(self):
        """Create a database and stash it in the resource ``zodbDB``. If
        that resource exists, create a layered DemoStorage on top of the
        base database. Otherwise, create a new resource.

        The database is registered in the global configuration so that
        Zope 2 app startup will find it. We use a facade object to ensure
        that the database that is opened by Zope 2 is in fact the top of
        the resource stack.
        """
        if ZOPETESTCASEALERT:
            raise Exception('You try to run plone.testing tests together with '
                            'ZopeTestCase tests. This will result in random '
                            'failures. Convert the ZopeTestCase Tests or '
                            'do not run them together')

        import Zope2.Startup.datatypes
        import App.config

        # Layer a new storage for Zope 2 on top of the one from the base
        # layer, if there is one.

        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'),
            name='Startup')

        # Create a facade for the database object that will delegate to the
        # correct underlying database. This allows resource shadowing to work
        # with regular traversal, which relies on a module-level ``DB``
        # variable.

        class DBFacade(object):

            def __init__(self, layer):
                self.__layer = layer

            @property
            def __db(self):
                return self.__layer['zodbDB']

            def __getattr__(self, name):
                return getattr(self.__db, name)

        # Create a fake dbtab value in the config so that app startup will
        # use this one.

        class DBTab(Zope2.Startup.datatypes.DBTab):
            """A fake DBTab that causes App.startup() to use our own database.
            """

            def __init__(self, db):
                # value is never used when we have an open db
                self.db_factories = {'testing': None}
                self.mount_paths = {'/': 'testing'}
                self.databases = {'testing': db}

        config = App.config.getConfiguration()
        self._dbtab = getattr(config, 'dbtab', None)
        config.dbtab = DBTab(DBFacade(self))
        App.config.setConfiguration(config)

    def tearDownDatabase(self):
        """Close the database and pop the ``zodbDB`` resource. Restore the
        global database configuration to its previous state.
        """

        import App.config
        config = App.config.getConfiguration()
        config.dbtab = self._dbtab
        App.config.setConfiguration(config)
        del self._dbtab

        # Close and pop the zodbDB resource
        transaction.abort()
        self['zodbDB'].close()
        del self['zodbDB']

    def setUpApp(self):
        """Trigger Zope startup and set up the application.
        """

        # If the Testing module has been imported, the testinghome
        # variable is set and changes the way Zope2.startup() works.
        # We want the standard behavior so we remove it.

        import App.config
        config = App.config.getConfiguration()
        try:
            self._testingHome = config.testinghome
        except AttributeError:
            pass
        else:
            del config.testinghome
            App.config.setConfiguration(config)

        # This uses the DB from the dbtab, as configured in setUpDatabase().
        # That DB then gets stored as Zope2.DB and becomes the default.

        import Zope2
        Zope2.startup_wsgi()

        # At this point, Zope2.DB is set to the test database facade. This is
        # the database will be used by default when someone does Zope2.app().

    def tearDownApp(self):
        """Undo Zope 2 startup by unsetting the global state it creates.
        """

        import Zope2
        Zope2.app()._p_jar.close()

        Zope2._began_startup = 0

        Zope2.DB = None
        Zope2.bobo_application = None
        Zope2.zpublisher_transactions_manager = None
        Zope2.zpublisher_validated_hook = None
        Zope2.zpublisher_exception_hook = None
        Zope2.__bobo_before__ = None

        import App.config
        try:
            self._testingHome
        except AttributeError:
            pass
        else:
            config = App.config.getConfiguration()
            config.testinghome = self._testingHome
            App.config.setConfiguration(config)
            del self._testingHome

        import ZPublisher.WSGIPublisher
        ZPublisher.WSGIPublisher._MODULES.clear()

    def setUpBasicProducts(self):
        """Install a minimal set of products required for Zope 2.
        """

        with zopeApp() as app:
            installProduct(app, 'Products.PluginIndexes')
            installProduct(app, 'Products.OFSP')

    def tearDownBasicProducts(self):
        """Tear down the minimal set of products
        """

        with zopeApp() as app:
            uninstallProduct(app, 'Products.PluginIndexes')
            uninstallProduct(app, 'Products.OFSP')

        # It's possible for Five's _register_monkies and _meta_type_regs
        # global variables to contain duplicates. This causes an unecessary
        # error in the LayerCleanup layer's tear-down. Guard against that
        # here

        try:
            from OFS import metaconfigure
        except ImportError:
            # Zope <= 2.12
            from Products.Five import fiveconfigure as metaconfigure
        metaconfigure._register_monkies = list(
            set(metaconfigure._register_monkies))
        metaconfigure._meta_type_regs = list(
            set(metaconfigure._meta_type_regs))

    def setUpZCML(self):
        """Load the basic ZCML configuration from Five. Exposes a resource
        ``configurationContext`` which can be used to load further ZCML.
        """

        # Push a new global registry so that we can cleanly tear down all ZCML
        from plone.testing import zca
        zca.pushGlobalRegistry()

        # Load something akin to the default site.zcml without actually auto-
        # loading products

        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext'))

        from zope.configuration import xmlconfig
        xmlconfig.string("""\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:meta="http://namespaces.zope.org/meta">

    <include package="Products.Five" />
    <meta:redefinePermission from="zope2.Public" to="zope.Public" />

    <securityPolicy component="AccessControl.security.SecurityPolicy" />

</configure>
""", context=context)

    def tearDownZCML(self):
        """Tear down the component registry and delete the
        ``configurationContext`` resource.
        """
        # Delete the (possibly stacked) configuration context
        del self['configurationContext']

        # Zap all globally loaded ZCML
        from plone.testing import zca
        zca.popGlobalRegistry()

    def setUpFive(self):
        """Initialize Five without loading the site.zcml file to avoid
        loading all Products.* .

        This basically pushes a special vocabulary registry that
        supports global and local utilities.
        """

        self._oldVocabularyRegistry = getVocabularyRegistry()
        setVocabularyRegistry(Zope2VocabularyRegistry())

    def tearDownFive(self):
        """Tear down the Five initialization restoring the previous
        vocabulary registry.
        """

        setVocabularyRegistry(self._oldVocabularyRegistry)


STARTUP = Startup()


# Basic integration and functional test and layers. These are the simplest
# Zope layers that are generally useful

class IntegrationTesting(Layer):
    """This layer extends ``STARTUP`` to add rollback of the transaction
    after each test. It does not manage a fixture and has no layer lifecyle,
    only a test lifecycle.

    The application root is available as the resource ``app`` and the request
    is available as the resource ``request``, set up and torn down for each
    test.

    Hint: If you want to create your own fixture on top of ``STARTUP``,
    create a new layer that has ``STARTUP`` as a base. Then instantiate
    this layer with your new "fixture" layer as a base, e.g.::

        from plone.testing import wsgi
        from plone.testing import Layer

        class MyFixture(Layer):

            ...

        MY_FIXTURE = MyFixture(bases=(wsgi.STARTUP,), name='MyFixture')
        MY_INTEGRATION_TESTING = wsgi.IntegrationTesting(bases=(MY_FIXTURE,), name='MyFixture:Integration')  # noqa
    """

    defaultBases = (STARTUP,)

    # Test lifecycle

    def testSetUp(self):
        import Zope2

        # Open a new app and save it as the resource ``app``.

        environ = {
            'SERVER_NAME': self['host'],
            'SERVER_PORT': str(self['port']),
        }

        app = addRequestContainer(Zope2.app(), environ=environ)
        request = app.REQUEST
        request['PARENTS'] = [app]

        # Make sure we have a zope.globalrequest request
        try:
            from zope.globalrequest import setRequest
            setRequest(request)
        except ImportError:
            pass

        # Start a transaction
        transaction.begin()

        self._original_commit = transaction.commit

        def you_broke_it():
            raise TestIsolationBroken("""You are in a Test Layer
(IntegrationTesting) that is fast by just aborting transactions between each
test.  You just committed something. That breaks the test isolation.  So I stop
here and let you fix it.""")

        # Prevent commits in integration tests which breaks test isolation.
        transaction.commit = you_broke_it

        # Save resources for tests to access
        self['app'] = app
        self['request'] = request

    def testTearDown(self):

        # Abort the transaction
        transaction.abort()

        transaction.commit = self._original_commit

        # Make sure we have a zope.globalrequest request
        try:
            from zope.globalrequest import setRequest
            setRequest(None)
        except ImportError:
            pass

        # Close the database connection and the request
        app = self['app']
        app.REQUEST.close()
        app._p_jar.close()

        # Delete the resources
        del self['request']
        del self['app']


INTEGRATION_TESTING = IntegrationTesting()


class FunctionalTesting(Layer):
    """An alternative to ``INTEGRATION_TESTING`` suitable for functional testing.
    This one pushes and pops a ``DemoStorage`` layer for each test. The
    net result is that a test may commit safely.

    As with ``INTEGRATION_TESTING``, the application root is available as the
    resource ``app`` and the request is available as the resource ``request``,
    set up and torn down for each test.

    Hint: If you want to create your own fixture on top of ``STARTUP``,
    create a new layer that has ``STARTUP`` as a base. Then instantiate
    this layer with your new "fixture" layer as a base, e.g.::

        from plone.testing import wsgi
        from plone.testing import Layer

        class MyFixture(Layer):

            ...

        MY_FIXTURE = MyFixture(bases=(wsgi.STARTUP,), name='MyFixture')
        MY_FUNCTIONAL_TESTING = wsgi.FunctionalTesting(bases=(MY_FIXTURE,), name='MyFixture:Functional')  # noqa
    """

    defaultBases = (STARTUP,)

    # Test lifecycle

    def testSetUp(self):
        import Zope2

        # Override zodbDB from the layer setup. Since it was set up by
        # this layer, we can't just assign a new shadow. We therefore keep
        # track of the original so that we can restore it on tear-down.

        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'),
            name='FunctionalTest')

        # Save the app

        environ = {
            'SERVER_NAME': self['host'],
            'SERVER_PORT': str(self['port']),
        }

        app = addRequestContainer(Zope2.app(), environ=environ)
        request = app.REQUEST
        request['PARENTS'] = [app]

        # Make sure we have a zope.globalrequest request
        try:
            from zope.globalrequest import setRequest
            setRequest(request)
        except ImportError:
            pass

        # Start a transaction
        transaction.begin()

        # Save resources for the test
        self['app'] = app
        self['request'] = request

    def testTearDown(self):
        # Abort any open transactions
        transaction.abort()

        # Make sure we have a zope.globalrequest request
        try:
            from zope.globalrequest import setRequest
            setRequest(None)
        except ImportError:
            pass

        # Close the database connection and the request
        app = self['app']
        app.REQUEST.close()
        app._p_jar.close()

        del self['app']
        del self['request']

        # Close and discard the database
        self['zodbDB'].close()
        del self['zodbDB']


FUNCTIONAL_TESTING = FunctionalTesting()

WSGI_LOG_REQUEST = 'WSGI_REQUEST_LOGGING' in os.environ


class NoLogWSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    """Less chatty WSGIRequestHandler."""

    def log_request(self, *args):
        """Print the request only on the console if requested."""
        if WSGI_LOG_REQUEST:
            wsgiref.simple_server.WSGIRequestHandler.log_request(
                self, *args)  # old-style class :-/


class WSGIServer(Layer):
    """Start a WSGI server that accesses the fixture managed by the
    ``STARTUP`` layer.

    The host and port are available as the resources ``host`` and ``port``,
    respectively.

    The ``WSGI_SERVER_FIXTURE`` layer must be used as the base for a layer that
    uses the ``FunctionalTesting`` layer class. The ``WSGI_SERVER`` layer is
    an example of such a layer.
    """

    defaultBases = (STARTUP,)

    timeout = 5
    host = os.environ.get('WSGI_SERVER_HOST',
                          os.environ.get('ZSERVER_HOST', 'localhost'))
    port = int(os.environ.get('WSGI_SERVER_PORT',
                              os.environ.get('ZSERVER_PORT', 55001)))
    pipeline = [
        ('Zope', 'paste.filter_app_factory', 'httpexceptions', {}),
    ]

    def setUp(self):
        self['host'] = self.host
        self.setUpServer()
        self['port'] = self.port

    def tearDown(self):
        self.tearDownServer()
        del self['host']
        del self['port']

    def setUpServer(self):
        """Create a WSGI server instance and save it in self.server.
        """
        app = self.make_wsgi_app()
        self.server = wsgiref.simple_server.make_server(
            self.host, self.port, app, handler_class=NoLogWSGIRequestHandler)
        # allow to choose a random port using 0 as port number:
        self.port = self.server.server_port

        self.thread = threading.Thread(target=self.serve)
        self.thread.daemon = True
        self.thread.start()

    def tearDownServer(self):
        """Close the server socket and clean up.
        """
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(self.timeout)
        if self.thread.isAlive():
            raise RuntimeError('WSGI server could not be shut down')

        shutil.rmtree(self._wsgi_conf_dir)

    def make_wsgi_app(self):
        self._wsgi_conf_dir = tempfile.mkdtemp()
        global_config = {'here': self._wsgi_conf_dir}
        zope_conf = self._get_zope_conf(self._wsgi_conf_dir)
        Zope2.Startup.run.make_wsgi_app(global_config, zope_conf)
        app = ZPublisher.WSGIPublisher.publish_module

        for spec, protocol, name, extra in reversed(self.pipeline):
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_config, **extra)
        return app

    def serve(self):
        self.server.serve_forever()

    def _get_zope_conf(self, dir):
        fd, path = tempfile.mkstemp(dir=dir)
        with os.fdopen(fd, 'w') as zope_conf:
            zope_conf.write('instancehome {0}\n'.format(os.path.dirname(dir)))
        return path


# Fixture layer - use as a base layer, but don't use directly, as it has no
# test lifecycle
WSGI_SERVER_FIXTURE = WSGIServer()

# Functional testing layer that uses the WSGI_SERVER_FIXTURE
WSGI_SERVER = FunctionalTesting(
    bases=(
        WSGI_SERVER_FIXTURE,
    ),
    name='WSGIServer:Functional')
