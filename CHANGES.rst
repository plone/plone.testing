Changelog
=========

4.3.3 (2019-03-27)
------------------

Bug fixes:

- Set default ZPublisher encoding to utf-8 to avoid encoding errors in testbrowser
  [petschki]


4.3.2 (2018-10-05)
------------------

Breaking changes:

- Default to picking a dynamical port for ZServer layers instead of a static
  default port.
  [Rotonen]


4.3.1 (2017-05-29)
------------------

Bug fixes:

- Fix for ZODB 5: Abort transaction before DB close.
  [jensens, jimfulton, ale-rt]



4.3.0 (2017-03-05)
------------------

- No changes.

Notes
~~~~~

This is a rerelease of 4.1.2 (without any changes) meant to discourage the
use of the 4.2.x series which has turned into 5.0.x.


4.1.2 (2017-03-05)
------------------

Bugfixes:

- Replace `ZServer.PubCore` handler with a threadless version, which fixes
  `coverage` reporting.  See https://bitbucket.org/ned/coveragepy/issues/244.
  [witsch]


4.1.1 (2016-02-21)
------------------

Bugfixes:

- Fix tests for Zope 4, where the app root Control_Panel is not available anymore.
  [thet]


4.1.0 (2016-01-08)
------------------

Bugfixes:

- Rename all txt doctest files to rst. Reformat doctests.
  [thet]

- PEP 8.
  [thet]

- Depend on zope.testrunner, which was moved out from
  zope.testing.testrunner.
  [thet]

- Add support for Zope 4.
  [thet]


4.0.15 (2015-08-14)
-------------------

- Prevent exception masking in finally clause of zopeApp context
  [do3cc]


4.0.14 (2015-07-29)
-------------------

- Rerelease for clarity due to double release of 4.0.13.
  [maurits]

- Added ``multiinit``-parameter to z2.installProduct
  to allow multiple initialize methods for a package
  [tomgross]


4.0.13 (2015-03-13)
-------------------

- Really fix not to depend on unittest2.
  [icemac]

- Add tox.ini
  [icemac]


4.0.12 (2014-09-07)
-------------------

- Fixed AttributeError when importing ``plone.testing.z2`` if
  ``zope.testbrowser`` 4.x is used but not ``zope.app.testing``. [icemac]

- Broke dependency on `unittest2` for Python 2.7+ as all features of
  `unittest2` are integrated in `unittest` there. [icemac]


4.0.11 (2014-02-22)
-------------------

- Fix z2.txt doctest for FTP_SERVER.
  [timo]


4.0.10 (2014-02-11)
-------------------

- Read 'FTPSERVER_HOST' and 'FTPSERVER_PORT' from the environment variables if
  possible. This allows us to run tests in parallel on CI servers.
  [timo]


4.0.9 (2014-01-28)
------------------

- Replace deprecated Zope2VocabularyRegistry import.
  [timo]


4.0.8 (2013-03-05)
------------------

- Factor test request creation out of addRequestContainer into makeTestRequest.
  [davisagli]


4.0.7 (2012-12-09)
------------------

- Fix quoting of urls by the testbrowser.
  [do3cc]


4.0.6 (2012-10-15)
------------------

- Update manifest.in to include content in src directory.
  [esteele]


4.0.5 (2012-10-15)
------------------

- Fixed an issue where a query string would be unquoted twice; once
  while setting up the HTTP request and once in the handler (the
  publisher).
  [malthe]


4.0.4 (2012-08-04)
------------------

- Fixed the cache reset code. In some situations the function does not
  have any defaults, so we shouldn't try to clear out the app
  reference.
  [malthe]


4.0.3 (2011-11-24)
------------------

- Fixed class names in documentation to match code.
  [icemac]


4.0.2 (2011-08-31)
------------------

- The defaults of the ``ZPublisher.Publish.get_module_info`` function cache
  a reference to the app, so make sure that gets reset when tearing down the
  app. This fixes a problem where the testbrowser in the second functional
  layer to be set up accessed the database from the first functional layer.
  [davisagli]


4.0.1 - 2011-05-20
------------------

- Moved readme file containing tests into the package, so tests can be run from
  released source distributions. Closes http://dev.plone.org/plone/ticket/11821.
  [hannosch]

- Relicense under BSD license.
  See http://plone.org/foundation/materials/foundation-resolutions/plone-framework-components-relicensing-policy
  [davisagli]


4.0 - 2011-05-13
----------------

- Release 4.0 Final.
  [esteele]

- Add MANIFEST.in.
  [WouterVH]


4.0a6 - 2011-04-06
------------------

- Fixed Browser cookies retrieval with Zope 2.13.
  [vincentfretin]

- Add ``ZCMLSandbox`` layer to load a ZCML file; replaces ``setUpZcmlFiles`` and
  ``tearDownZcmlFiles`` helper functions.
  [gotcha]


4.0a5 - 2011-03-02
------------------

- Handle test failures due to userFolderAddUser returning the user object in
  newer versions of Zope.
  [esteele]

- Add ``setUpZcmlFiles`` and ``tearDownZcmlFiles`` helpers to enable loading
  of ZCML files without too much boilerplate.
  [gotcha]

- Add some logging.
  [gotcha]

- Add the ``[security]`` extra, to provide tear-down of security checkers.
  [optilude]

- Let the ``IntegrationTesting`` and ``FunctionalTesting`` lifecycle layers
  set up request ``PARENTS`` and, if present, wire up
  ``zope.globalrequest``.
  [optilude]

- Make the test browser support IStreamIterators
  [optilude]


4.0a4 - 2011-01-11
------------------

- Make sure ZCML doesn't load during App startup in Zope 2.13.
  [davisagli]


4.0a3 - 2010-12-14
------------------

- Ignore the `testinghome` configuration setting if present.
  [stefan]

- Use the new API for getting the packages_to_initialize list in Zope 2.13.
  [davisagli]

- De-duplicate _register_monkies and _meta_type_regs in the correct module on
  teardown of the Startup layer in Zope 2.13.
  [davisagli]

- Allow doctest suites from `zope.testing` to work with `plone.testing.layer.layered`.
  Previously, only doctest suites from the stdlib would see the `layer` global.
  [nouri]

- Changed documentation to advertise the `coverage` library for running
  coverage tests instead of the built-in `zope.testing` support. This also
  avoids using `z3c.coverage`. The coverage tests now run at the same speed
  as a normal test run, making it more likely to get executed frequently.
  [hannosch]

- Correct license to GPL version 2 only.
  [hannosch]

- Fix some user id vs name confusion.
  [rossp]

- Add the option to specify ZServer host and port through environment
  variables - ZSERVER_HOST and ZSERVER_PORT).
  [esteele]


1.0a2 - 2010-09-05
------------------

- Fix a problem that would cause ``<meta:redefinePermission />`` to break.
  In particular fixes the use of the ``zope2.Public`` permission.
  [optilude]

- Set the security implementation to "Python" for easier debugging during
  the z2.STARTUP layer.
  [optilude]

- Initialize Five in the z2.Startup layer, pushing a Zope2VocabularyRegistry on
  layer set-up and restoring the previous one upon tear-down.
  [dukebody]


1.0a1 - 2010-08-01
------------------

- Initial release
