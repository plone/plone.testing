# -*- coding: utf-8 -*-
"""Zope2-specific helpers and layers using ZServer
"""
from __future__ import absolute_import
from plone.testing import Layer
from plone.testing.zope import addRequestContainer
from plone.testing.zope import login  # noqa
from plone.testing.zope import logout  # noqa
from plone.testing.zope import setRoles  # noqa
from plone.testing._z2_testbrowser import Browser  # noqa
from plone.testing import zope

import contextlib
import os
import transaction


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
    from ZServer import Zope2

    closeConn = True
    if connection is not None:
        closeConn = False

    if connection is None and db is not None:
        connection = db.open()

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

class Startup(zope.Startup):
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

    threads = 1

    # Layer lifecycle helper methods

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
        Zope2.startup()

        # At this point, Zope2.DB is set to the test database facade. This is
        # the database will be used by default when someone does Zope2.app().

    def tearDownApp(self):
        """Undo Zope 2 startup by unsetting the global state it creates.
        """

        import Zope2
        import ZServer.Zope2
        Zope2.app()._p_jar.close()

        ZServer.Zope2._began_startup = 0

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

        # Clear out the app reference cached in get_module_info's
        # 'modules' parameter default dict. (waaaaa)
        import ZPublisher.Publish
        defaults = ZPublisher.Publish.get_module_info.func_defaults

        if defaults:
            d = list(defaults)
            d[0] = {}
            ZPublisher.Publish.get_module_info.func_defaults = tuple(d)


STARTUP = Startup()


# Basic integration and functional test and layers. These are the simplest
# Zope 2 layers that are generally useful

class IntegrationTesting(zope.IntegrationTesting):
    """This layer extends ``STARTUP`` to add rollback of the transaction
    after each test. It does not manage a fixture and has no layer lifecyle,
    only a test lifecycle.

    The application root is available as the resource ``app`` and the request
    is available as the resource ``request``, set up and torn down for each
    test.

    Hint: If you want to create your own fixture on top of ``STARTUP``,
    create a new layer that has ``STARTUP`` as a base. Then instantiate
    this layer with your new "fixture" layer as a base, e.g.::

        from plone.testing import zserver
        from plone.testing import Layer

        class MyFixture(Layer):

            ...

        MY_FIXTURE = MyFixture(bases=(zserver.STARTUP,), name='MyFixture')
        MY_INTEGRATION_TESTING = zserver.IntegrationTesting(bases=(MY_FIXTURE,), name='MyFixture:Integration')  # noqa
    """

    defaultBases = (STARTUP,)


INTEGRATION_TESTING = IntegrationTesting()


class FunctionalTesting(zope.FunctionalTesting):
    """An alternative to ``INTEGRATION_TESTING`` suitable for functional testing.
    This one pushes and pops a ``DemoStorage`` layer for each test. The
    net result is that a test may commit safely.

    As with ``INTEGRATION_TESTING``, the application root is available as the
    resource ``app`` and the request is available as the resource ``request``,
    set up and torn down for each test.

    Hint: If you want to create your own fixture on top of ``STARTUP``,
    create a new layer that has ``STARTUP`` as a base. Then instantiate
    this layer with your new "fixture" layer as a base, e.g.::

        from plone.testing import zserver
        from plone.testing import Layer

        class MyFixture(Layer):

            ...

        MY_FIXTURE = MyFixture(bases=(zserver.STARTUP,), name='MyFixture')
        MY_FUNCTIONAL_TESTING = zserver.FunctionalTesting(bases=(MY_FIXTURE,), name='MyFixture:Functional')  # noqa
    """

    defaultBases = (STARTUP,)


FUNCTIONAL_TESTING = FunctionalTesting()


# More advanced functional testing - running ZServer and FTP server

class ZServer(Layer):
    """Start a ZServer that accesses the fixture managed by the
    ``STARTUP`` layer.

    The host and port are available as the resources ``host`` and ``port``,
    respectively.

    This should *not* be used in parallel with the ``FTP_SERVER`` layer, since
    it shares the same async loop.

    The ``ZSERVER_FIXTURE`` layer must be used as the base for a layer that
    uses the ``FunctionalTesting`` layer class. The ``ZSERVER`` layer is
    an example of such a layer.
    """

    defaultBases = (STARTUP,)

    host = os.environ.get('ZSERVER_HOST', 'localhost')
    port = int(os.environ.get('ZSERVER_PORT', 55001))
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
            name='{0} server'.format(self.__name__),
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

        server = zhttp_server(
            ip=self.host,
            port=self.port,
            resolver=None,
            logger_object=zopeLog)
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


# Fixture layer - use as a base layer, but don't use directly, as it has no
# test lifecycle
ZSERVER_FIXTURE = ZServer()

# Functional testing layer that uses the ZSERVER_FIXTURE
ZSERVER = FunctionalTesting(
    bases=(
        ZSERVER_FIXTURE,
    ),
    name='ZServer:Functional')


class FTPServer(ZServer):
    """FTP variant of the ZServer layer.

    This will not play well with the ZServer layer. If you need both
    ZServer and FTPServer running together, you can subclass the ZServer
    layer class (like this layer class does) and implement setUpServer()
    and tearDownServer() to set up and close down two servers on different
    ports. They will then share a main loop.

    The ``FTP_SERVER_FIXTURE`` layer must be used as the base for a layer that
    uses the ``FunctionalTesting`` layer class. The ``FTP_SERVER`` layer is
    an example of such a layer.
    """

    defaultBases = (STARTUP,)

    host = os.environ.get('FTPSERVER_HOST', 'localhost')
    port = int(os.environ.get('FTPSERVER_PORT', 55002))
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

        self.ftpServer = FTPServer(
            'Zope2',
            ip=self.host,
            port=self.port,
            logger_object=zopeLog)

    def tearDownServer(self):
        """Close the FTPServer socket
        """
        self.ftpServer.close()


# Fixture layer - use as a base layer, but don't use directly, as it has no
# test lifecycle
FTP_SERVER_FIXTURE = FTPServer()

# Functional testing layer that uses the FTP_SERVER_FIXTURE
FTP_SERVER = FunctionalTesting(
    bases=(
        FTP_SERVER_FIXTURE,
    ),
    name='FTPServer:Functional')
