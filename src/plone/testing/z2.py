"""Zope2-specific helpers and layers
"""

import contextlib

from plone.testing import Layer

_installedProducts = {}

# Constants for names used in layer setup
TEST_FOLDER_NAME = 'test_folder_1_'
TEST_USER_NAME = 'test_user_1_'
TEST_USER_PASSWORD = 'secret'
TEST_USER_ROLE = 'test_role_1_'
TEST_USER_PERMISSIONS = ['Access contents information', 'View']

def installProduct(app, productName, quiet=True):
    """Install the Zope 2 product with the given name, so that it will show
    up in the Zope 2 control panel and have its ``initialize()`` hook called.
    
    The ``STARTUP`` layer or an equivalent layer must have been loaded first.
    
    If ``quiet`` is False, an error will be logged if the product cannot be
    found. By default, the function is silent.
    
    Note that products' ZCML is *not* loaded automatically, even if the
    product is in the Products namespace.
    """
    
    import sys
    import Products
    
    from OFS.Folder import Folder
    from OFS.Application import get_folder_permissions, get_products
    from OFS.Application import install_product, install_package
    from App.class_init import InitializeClass
    
    global _installedProducts
    found = False
    
    if productName in _installedProducts:
        return
    
    if productName.startswith('Products.'):
        for priority, name, index, productDir in get_products():
            if ('Products.' + name) == productName:
                meta_types = []
                install_product(app, productDir, name, meta_types,
                                get_folder_permissions(), raise_exc=1)
                _installedProducts[productName] = 1
                Products.meta_types = Products.meta_types + tuple(meta_types)
                InitializeClass(Folder)
                
                found = True
                break
    
    else:
        for module, init_func in getattr(Products, '_packages_to_initialize', []):
            if module.__name__ == productName:
                install_package(app, module, init_func, raise_exc=1)
                _installedProducts[productName] = True
                Products._packages_to_initialize.remove((module, init_func))
                
                found = True
                break
    
    if not found and not quiet:
        sys.stderr.write("Could not install product %s" % productName)
        sys.stderr.flush()

def uninstallProduct(app, productName, quiet=True):
    """Uninstall the given Zope 2 product. This is the inverse of
    ``installProduct()`` above.
    """
    
    # TODO: Is this even possible? ;)
    pass

def login(userFolder, userName):
    """Log in as the given user in the given user folder.
    """
    
    from AccessControl.SecurityManagement import newSecurityManager
    
    user = userFolder.getUserById(userName)
    if not hasattr(user, 'aq_base'):
        user = user.__of__(userFolder)
    newSecurityManager(None, user)

def logout():
    """Log out, i.e. become anonymous
    """
    
    from AccessControl.SecurityManagement import noSecurityManager
    noSecurityManager()

def setRoles(userFolder, userName, roles):
    """Set the given user's roles to a tuple of roles.
    """
    
    userFolder.userFolderEditUser(userName, None, list(roles), [])

def addRequestContainer(app, environ=None):
    """Add the request container with a fake request to the app object's
    acquisition context and return the wrapped app object. Additional request
    environment values can be passed as a dict ``environ``.
    """
    
    from sys import stdin, stdout
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse
    from ZPublisher.BaseRequest import RequestContainer
    
    from zope.publisher.browser import setDefaultSkin
    
    if environ is None:
        environ = {}
    
    environ.setdefault('SERVER_NAME', 'nohost')
    environ.setdefault('SERVER_PORT', 'port')
    environ.setdefault('REQUEST_METHOD', 'GET')
    
    resp = HTTPResponse(stdout=stdout)
    req = HTTPRequest(stdin, environ, resp)
    req._steps = ['noobject']  # Fake a published object.
    
    setDefaultSkin(req)
    
    requestcontainer = RequestContainer(REQUEST=req)
    return app.__of__(requestcontainer)


@contextlib.contextmanager
def zopeApp(db=None, conn=None, environ=None):
    """Context manager for working with the Zope2 app::
    
        with zopeApp() as app:
            ...
    
    The ``app`` object has a request container and a simple ``REQUEST``.
    To set the request environment, pass a dict ``environ``. See
    ``addRequestContainer()`` for details.
    
    Pass a ZODB handle as ``db`` to use a specificdatabase. Alternatively,
    pass an open connection as ``conn`` (the connection will not be closed).
    """
    
    import Zope2
    import transaction
    
    closeConn = True
    if conn is not None:
        closeConn = False
    
    if conn is None and db is not None:
        conn = db.open()
    
    app = addRequestContainer(Zope2.app(conn), environ=environ)
    
    if conn is None:
        conn = app._p_jar
    
    try:
        yield app
        transaction.commit()
    except:
        transaction.abort()
        raise
    finally:
        app.REQUEST.close()
        
        if closeConn:
            conn.close()


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
    
    __bases__ = ()
    
    threads = 1
    
    # Layer lifecycle
    
    def setUp(self):
        
        self.setUpDebugMode()
        self.setUpClientCache()
        self.setUpPatches()
        self.setUpThreads()
        self.setUpDatabase()
        self.setUpHostPort()
        self.setUpApp()
        self.setUpBasicProducts()
        self.setUpZCML()
    
    def tearDown(self):
        
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
    
    def tearDownDebugMode(self):
        """Return the debug mode flag to its previous state
        """
        
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
        import App.ProductContext
        
        # Avoid expensive product import
        def null_import_products(): pass
        self._OFS_Application_import_products = OFS.Application.import_products
        OFS.Application.import_products = null_import_products
        
        # Avoid expensive product installation
        def null_initialize(app): pass
        self._OFS_Application_initialize = OFS.Application.initialize
        OFS.Application.initialize = null_initialize
        
        # Avoid expensive help registration
        def null_register_topic(self,id,topic): pass
        self._App_ProductContext_ProductContext_registerHelpTopic = App.ProductContext.ProductContext.registerHelpTopic
        App.ProductContext.ProductContext.registerHelpTopic = null_register_topic
        
        def null_register_title(self,title): pass
        self._App_ProductContext_ProductContext_registerHelpTitle = App.ProductContext.ProductContext.registerHelpTitle
        App.ProductContext.ProductContext.registerHelpTitle = null_register_title
        
        def null_register_help(self,directory='',clear=1,title_re=None): pass
        self._App_ProductContext_ProductContext_registerHelp = App.ProductContext.ProductContext.registerHelp
        App.ProductContext.ProductContext.registerHelp = null_register_help
    
    def tearDownPatches(self):
        """Revert the monkey patches from setUpPatches()
        """
        
        import OFS.Application
        import App.ProductContext
        
        OFS.Application.import_products = self._OFS_Application_import_products
        del self._OFS_Application_import_products
        
        OFS.Application.initialize = self._OFS_Application_initialize
        del self._OFS_Application_initialize
        
        App.ProductContext.ProductContext.registerHelpTopic = self._App_ProductContext_ProductContext_registerHelpTopic
        del self._App_ProductContext_ProductContext_registerHelpTopic
        
        App.ProductContext.ProductContext.registerHelpTitle = self._App_ProductContext_ProductContext_registerHelpTitle
        del self._App_ProductContext_ProductContext_registerHelpTitle
        
        App.ProductContext.ProductContext.registerHelp = self._App_ProductContext_ProductContext_registerHelp
        del self._App_ProductContext_ProductContext_registerHelp
    
    def setUpThreads(self):
        """Set the thread count for ZServer. This defaults to 1.
        """
        
        # We can't use setNumberOfThreads() because that function self-
        # destructs, literally, when called.
        
        import ZServer.PubCore
        self._zserverThreads = ZServer.PubCore._n
        ZServer.PubCore._n = self.threads
    
    def tearDownThreads(self):
        """Reset the ZServer thread count.
        """
        
        import ZServer.PubCore
        ZServer.PubCore._n = self._zserverThreads
        del self._zserverThreads
        
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
        
        import Zope2.Startup.datatypes
        import App.config
        
        from ZODB.DemoStorage import DemoStorage
        from ZODB.DB import DB
        
        # Layer a new storage for Zope 2 on top of the one from the base
        # layer, if there is one.
        
        db = self.get('zodbDB', None) # from base layer
        if db is not None:
            storage = DemoStorage(base=db.storage)
        else:
            storage = DemoStorage()
        
        self['zodbDB'] = db = DB(storage)
        
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
                self.db_factories = {'testing': None} # value is never used when we have an open db
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
        self['zodbDB'].close()
        del self['zodbDB']
    
    def setUpApp(self):
        """Trigger Zope startup and set up the application.
        """
        
        import Zope2
        
        # This uses the DB from the dbtab, as configured in setUpDatabase().
        # That DB then gets stored as Zope2.DB and becomes the default.
        
        Zope2.startup()
        
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
    
    def setUpZCML(self):
        """Load the basic ZCML configuration from Five. Exposes a resource
        ``configurationContext`` which can be used to load further ZCML.
        """
        
        from zope.configuration import xmlconfig
        import Products.Five
        
        self['configurationContext'] = xmlconfig.file('configure.zcml', Products.Five)
    
    def tearDownZCML(self):
        """Tear down the component registry and delete the
        ``configurationContext`` resource.
        """
        
        from zope.component.globalregistry import base
        base.__init__('base')
        
        del self['configurationContext']

STARTUP = Startup()

class BasicSite(Layer):
    """This layer extends ``STARTUP`` to add rollback of the transaction
    after each test. It also sets up some basic content:
    
    * A folder in the app root with the name ``z2.TEST_FOLDER_NAME``
    * A user named ``z2.TEST_USER_NAME`` with password
    ``z2.TEST_USER_PASSWORD`` in a local user folder inside the test folder.
    * A role granted to this user named ``z2.TEST_USER_ROLE``
    * ``View`` and ``Access contents information`` granted to this role
    
    The extra content is created in a stacked DemoStorage, shadowing the
    ``zodbDB`` resource.
    
    The folder is available as a resource ``folder``. The application root is
    available as the resource ``app``.
    
    The test user is "logged in" for each test. Use ``logout()`` to simulate
    an anonymous user.
    """
    
    __bases__ = (STARTUP,)
    
    # Layer lifecycle
    
    def setUp(self):
        from ZODB.DemoStorage import DemoStorage
        from ZODB.DB import DB
        
        # Stack a new DemoStorage on top of the one from STARTUP.
        storage = DemoStorage(base=self['zodbDB'].storage)
        self['zodbDB'] = DB(storage)
        
        self.setUpDefaultContent()
    
    def tearDown(self):
        # Zap the stacked ZODB
        
        self['zodbDB'].close()
        del self['zodbDB']
    
    def setUpDefaultContent(self):
        
        with zopeApp() as app:        
            app.manage_addFolder(TEST_FOLDER_NAME)
            folder = app[TEST_FOLDER_NAME]
            folder._addRole(TEST_USER_ROLE)
            folder.manage_addUserFolder()
        
            userFolder = folder['acl_users']
            userFolder.userFolderAddUser(TEST_USER_NAME, TEST_USER_PASSWORD, [TEST_USER_ROLE], [])
        
            folder.manage_role(TEST_USER_ROLE, TEST_USER_PERMISSIONS)
    
    # Test lifecycle
    
    def testSetUp(self):
        import Zope2
        import transaction
        
        # Open a new app and save it as the resource ``app``. Also fetch
        # the test folder and save that.
        
        environ = {
            'SERVER_NAME': self['host'],
            'SERVER_PORT': str(self['port']),
        }
        
        app = addRequestContainer(Zope2.app(), environ=environ)
        
        # Start a transaction
        transaction.begin()
        
        # Log in as the test user
        login(app[TEST_FOLDER_NAME]['acl_users'], TEST_USER_NAME)
        
        # Save resources for tests to access
        self['app'] = app
        self['folder'] = app[TEST_FOLDER_NAME]
    
    def testTearDown(self):
        import transaction
        
        # Abort the transaction
        transaction.abort()
        
        # Close the database connection and the request
        app = self['app']
        app._p_jar.close()
        app.REQUEST.close()
        
        # Delete the resources
        del self['app']
        del self['folder']

BASIC_SITE = BasicSite()

class Functional(BasicSite):
    """An alternative take on ``BasicSite`` suitable for functional testing.
    This one pushes and pops a ``DemoStorage`` layer for each test. The
    net result is that a test may commit safely.
    
    The same fixture is set up, but it's not actually shared with
    ``BASIC_SITE``, because that layer has different database management
    semantics.
    """
    
    __bases__ = (STARTUP,)
    
    # Test lifecycle
    
    def testSetUp(self):
        import Zope2
        
        from ZODB.DemoStorage import DemoStorage
        from ZODB.DB import DB
        
        import transaction
        
        # Stack yet another demo storage.
        
        # Override zodbDB from the layer setup. Since it was set up by
        # this layer, we can't just assign a new shadow. We therefore keep
        # track of the original so that we can restore it on tear-down.
        
        self._baseDB = self['zodbDB']
        storage = DemoStorage(base=self._baseDB.storage)
        self['zodbDB'] = DB(storage)
        
        # Save the app
        
        environ = {
            'SERVER_NAME': self['host'],
            'SERVER_PORT': str(self['port']),
        }
        
        app = addRequestContainer(Zope2.app(), environ=environ)
        
        # Start a transaction
        transaction.begin()
        
        # Log in as the test user
        
        login(app[TEST_FOLDER_NAME]['acl_users'], TEST_USER_NAME)
        
        # Save resources for the test
        self['app'] = app
        self['folder'] = app[TEST_FOLDER_NAME]
    
    def testTearDown(self):
        import transaction
        
        # Abort any open transactions
        transaction.abort()
        
        # Close the database connection and the request
        app = self['app']
        app._p_jar.close()
        app.REQUEST.close()
        
        del self['app']
        del self['folder']
        
        # Close and discard the database
        self['zodbDB'].close()
        self['zodbDB'] = self._baseDB
        del self._baseDB

FUNCTIONAL = Functional()

class ZServer(Layer):
    """Start a ZServer that accesses the fixture managed by the ``FUNCTIONAL``
    layer.
    
    The host and port are available as the resources ``host`` and ``port``,
    respectively.
    
    This should *not* be used in parallel with the ``FTP_SERVER`` layer, since
    it shares the same async loop.
    """
    
    __bases__ = (FUNCTIONAL,)
    
    host = 'localhost'
    port = 55001
    timeout = 5.0
    log = None
    
    def setUp(self):
        
        import time
        from threading import Thread
        
        self['host'] = self.host
        self['port'] = self.port
        
        self._shutdown = False
        
        self.setUpServer()
        
        self.thread = Thread(
                name="%s server" % self.__name__,
                target=self.runner,
            )
        
        self.thread.start()
        time.sleep(0.5)
        
    def tearDown(self):
        import time
        
        self._shutdown = True
        self.thread.join(self.timeout)
        time.sleep(0.5)
        
        self.tearDownServer()
        
        del self['host']
        del self['port']
    
    def setUpServer(self):
        """Create a ZServer server instance and save it in self.zserver
        """
        
        from ZServer import zhttp_server, zhttp_handler, logger
        from StringIO import StringIO
        
        log = self.log
        if log is None:
            log = StringIO()
        
        zopeLog = logger.file_logger(log)
        
        server = zhttp_server(ip=self.host, port=self.port, resolver=None, logger_object=zopeLog)
        zhttpHandler = zhttp_handler(module='Zope2', uri_base='')
        server.install_handler(zhttpHandler)
        
        self.zserver = server
    
    def tearDownServer(self):
        """Close the ZServer socket
        """
        self.zserver.close()
    
    # Thread runner
    
    def runner(self):
        """Thread runner for the main asyncore loop. This function runs in a
        separate thread.
        """
        
        import asyncore
        
        # Poll
        socket_map = asyncore.socket_map
        while socket_map and not self._shutdown:
            asyncore.poll(self.timeout, socket_map)

ZSERVER = ZServer()

class FTPServer(ZServer):
    """FTP variant of the ZServer layer.
    
    This will not play well with the ZServer layer. If you need both
    ZServer and FTPServer running together, you can subclass the ZServer
    layer class (like this layer class does) and implement setUpServer()
    and tearDownServer() to set up and close down two servers on different
    ports. They will then share a main loop.
    """
    
    __bases__ = (FUNCTIONAL,)
    
    host = 'localhost'
    port = 55002
    threads = 1
    timeout = 5.0
    log = None
    
    def setUpServer(self):
        """Create an FTP server instance and save it in self.ftpServer
        """
        
        from ZServer import logger
        from ZServer.FTPServer import FTPServer
        from StringIO import StringIO
        
        log = self.log
        if log is None:
            log = StringIO()
        
        zopeLog = logger.file_logger(log)
        
        self.ftpServer = FTPServer('Zope2', ip=self.host, port=self.port, logger_object=zopeLog)
    
    def tearDownServer(self):
        """Close the FTPServer socket
        """
        self.ftpServer.close()

FTP_SERVER = FTPServer()
