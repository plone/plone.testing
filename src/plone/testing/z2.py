from zope.deferredimport import deprecated

import plone.testing
import plone.testing.zope
import warnings


deprecated(
    "Please import from plone.testing.zope.",
    Browser="plone.testing.zope:Browser",
    TestIsolationBroken="plone.testing.zope:TestIsolationBroken",
    installProduct="plone.testing.zope:installProduct",
    uninstallProduct="plone.testing.zope:uninstallProduct",
    login="plone.testing.zope:login",
    logout="plone.testing.zope:logout",
    setRoles="plone.testing.zope:setRoles",
    makeTestRequest="plone.testing.zope:makeTestRequest",
    addRequestContainer="plone.testing.zope:addRequestContainer",
    zopeApp="plone.testing.zope:zopeApp",
    Startup="plone.testing.zope:Startup",
    STARTUP="plone.testing.zope:STARTUP",
    IntegrationTesting="plone.testing.zope:IntegrationTesting",
    INTEGRATION_TESTING="plone.testing.zope:INTEGRATION_TESTING",
    FunctionalTesting="plone.testing.zope:FunctionalTesting",
    FUNCTIONAL_TESTING="plone.testing.zope:FUNCTIONAL_TESTING",
    ZServer="plone.testing.zope:WSGIServer",
    ZSERVER_FIXTURE="plone.testing.zope:WSGI_SERVER_FIXTURE",
    ZSERVER="plone.testing.zope:WSGI_SERVER",
)


deprecated(
    "Please import from plone.testing.",
    Layer="plone.testing:Layer",
)


class FTPServer(plone.testing.Layer):
    """No-op so imports do not break."""

    def setUp(self):
        warnings.warn(
            "The FTPServer layer is now only a no-op as FTP is not supported"
            " by WSGI. If you really need the fixture import it from"
            " plone.testing.zserver."
        )


FTP_SERVER_FIXTURE = FTPServer()

FTP_SERVER = plone.testing.zope.FunctionalTesting(
    bases=(FTP_SERVER_FIXTURE,), name="No-OpFTPServer:Functional"
)
