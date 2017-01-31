from zope.testbrowser import browser
from ZPublisher.httpexceptions import HTTPExceptionHandler
from ZPublisher.WSGIPublisher import publish_module
import base64
import re
import urlparse


BASIC_RE = re.compile('Basic (.+)?:(.+)?$')


def authHeader(header):
    match = BASIC_RE.match(header)
    if match:
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        auth = base64.encodestring('%s:%s' % (u, p))
        return 'Basic %s' % auth[:-1]
    return header


def saveState(func):
    """Save threadlocal state (security manager, local component site) before
    exectuting a decorated function, and restore it after.
    """
    from AccessControl.SecurityManagement import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager
    from zope.site.hooks import getSite
    from zope.site.hooks import setSite

    def wrapped_func(*args, **kw):
        sm, site = getSecurityManager(), getSite()
        try:
            return func(*args, **kw)
        finally:
            setSecurityManager(sm)
            setSite(site)
    return wrapped_func


class Zope2Caller(object):
    """Functional testing caller that can execute HTTP requests via the
    Zope 2 WSGI publisher.
    """

    def __init__(self, browser, app):
        self.browser = browser
        self.app = app

    @saveState
    def __call__(self, environ, start_response):
        # Base64 encode auth header
        http_auth = 'HTTP_AUTHORIZATION'
        if http_auth in environ:
            environ[http_auth] = authHeader(environ[http_auth])

        publish = publish_module
        if self.browser.handleErrors:
            publish = HTTPExceptionHandler(publish)
        wsgi_result = publish(environ, start_response)

        # Sync transaction
        self.app._p_jar.sync()

        return wsgi_result


class Browser(browser.Browser):
    """A Zope ``testbrowser` Browser that uses the Zope Publisher."""

    handleErrors = True
    raiseHttpErrors = True

    def __init__(self, app, url=None):
        wsgi_app = Zope2Caller(self, app)
        super(Browser, self).__init__(url=url, wsgi_app=wsgi_app)

    def _absoluteUrl(self, url):
        url = super(Browser, self)._absoluteUrl(url)
        # use `localhost` as the internal host rather than `nohost`
        parsed = urlparse.urlparse(url)
        if parsed.netloc == 'nohost':
            parsed = parsed._replace(netloc='localhost')
        return parsed.geturl()
