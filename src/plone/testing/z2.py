from zope.deferredimport import deprecated
import plone.testing
import plone.testing.wsgi
import warnings

deprecated(
    'Please import from plone.testing.wsgi.',
    Browser='plone.testing.wsgi:Browser',
    TestIsolationBroken='plone.testing.wsgi:TestIsolationBroken',
    installProduct='plone.testing.wsgi:installProduct',
    uninstallProduct='plone.testing.wsgi:uninstallProduct',
    login='plone.testing.wsgi:login',
    logout='plone.testing.wsgi:logout',
    setRoles='plone.testing.wsgi:setRoles',
    makeTestRequest='plone.testing.wsgi:makeTestRequest',
    addRequestContainer='plone.testing.wsgi:addRequestContainer',
    zopeApp='plone.testing.wsgi:zopeApp',
    Startup='plone.testing.wsgi:Startup',
    STARTUP='plone.testing.wsgi:STARTUP',
    IntegrationTesting='plone.testing.wsgi:IntegrationTesting',
    INTEGRATION_TESTING='plone.testing.wsgi:INTEGRATION_TESTING',
    FunctionalTesting='plone.testing.wsgi:FunctionalTesting',
    FUNCTIONAL_TESTING='plone.testing.wsgi:FUNCTIONAL_TESTING',
    ZServer='plone.testing.wsgi:WSGIServer',
    ZSERVER_FIXTURE='plone.testing.wsgi:WSGI_SERVER_FIXTURE',
    ZSERVER='plone.testing.wsgi:WSGI_SERVER',
)


deprecated(
    'Please import from plone.testing.',
    Layer='plone.testing:Layer',
)


class FTPServer(plone.testing.Layer):
    """No-op so imports do not break."""

    def setUp(self):
        warnings.warn(
            'The FTPServer layer is now only a no-op as FTP is not supported'
            ' by WSGI. If you really need the fixture import it from'
            ' plone.testing.zserver.')

FTP_SERVER_FIXTURE = FTPServer()

FTP_SERVER = plone.testing.wsgi.FunctionalTesting(
    bases=(
        FTP_SERVER_FIXTURE,
    ),
    name='No-OpFTPServer:Functional')
