Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

9.0.2 (2024-06-26)
------------------

Bug fixes:


- makeTestRequest: use BytesIO to set up the test Response. @gotcha (fix_makeTestRequest)


9.0.1 (2023-11-30)
------------------

Bug fixes:


- Remove incorrect hard dependency on five.localsitemanager. @davisagli (#86)


9.0.0 (2023-10-25)
------------------

Breaking changes:


- Drop python 2.7 support.
  [gforcada] (#1)
- Drop ZServer support.
  [gforcada] (#2)


Internal:


- Update configuration files.
  [plone devs] (5cc689e5)


8.0.4 (2023-09-21)
------------------

Bug fixes:


- Fix tests when run with ZODB 5.8.1+.
  [maurits] (#581)


8.0.3 (2021-06-14)
------------------

Bug fixes:


- fix waitress deprecation warning (#77)
- Catch OSError in test teardown when removing a temporary directory.
  Fixes `issue 79 <https://github.com/plone/plone.testing/issues/79>`_.
  [maurits] (#79)


8.0.2 (2020-10-12)
------------------

Bug fixes:


- update `isort` configuration for version 5 of `isort` (#75)


8.0.1 (2020-06-16)
------------------

Bug fixes:


- fix broken Flake8 job (#74)


8.0.0 (2020-04-21)
------------------

Breaking changes:


- Drop support for Python 3.4 and 3.5.
  Remove "z2" extra.
  [jensens] (#72)


New features:


- Update links for further information about `testing`.
  [jugmac00] (#71)


Bug fixes:


- Fix tests when using zope.testrunner internals since its version 5.1.
  [jensens] (#72)


7.0.3 (2019-12-10)
------------------

Bug fixes:


- Fix issue with test-setup when using ZServer 4.0.2.
  [pbauer] (#69)


7.0.2 (2019-07-06)
------------------

Bug fixes:


- Remove the ``ZOPETESTCASEALERT`` as it imports from ZopeTestCase and has side effects.
  Fixes #64.
  [thet] (#67)


7.0.1 (2019-03-03)
------------------

Bug fixes:


- Fixed test for 'Connection refused' which could be 'Connection reset'.
  [maurits] (#59)


7.0.0 (2018-10-17)
------------------

Breaking changes:

- ``plone.testing.z2`` is now a BBB shim for ``plone.testing.zope``,
  thus it switches the tests to use WSGI.
  If you absolutely want to keep using ZServer please import from ``plone.testing.zserver``.

- ``plone.testing.z2`` now only contains a no-op FTPServer layer because FTP is not supported by WSGI.
  If you really need it, import it from ``plone.testing.zserver`` but this will not work on Python 3.
  
- Default to picking a dynamical port for ZServer layers instead of a static
  default port.
  [Rotonen]

New features:

- Make ``ZServer`` an optional dependency.

- Add support for Python 3.6.
  [rudaporto, icemac]

Bug fixes:

- Explicitly depend on ZServer on the z2 extra.
  [Rotonen]


6.1.0 (2018-10-05)
------------------

Breaking changes:

- Default to picking a dynamical port for ZServer layers instead of a static
  default port.
  [Rotonen]

Bug fixes:

- Pinned ZODB to < 5.4.0 for testing to avoid flaky doctest layer teardowns.
  [Rotonen]

- Loosened doctest assertions to keep up with Zope-side changes.
  [Rotonen]

- Fix most of the code smells Jenkins complains about.

- Fix the Zope exception hook when using the ZServer layer.

- Fix teardown of the ``plone.testing.security.Checkers`` layer.
  It was not properly restoring zope.security's ``_checkers`` dict.


6.0.0 (2018-02-05)
------------------

- Breaking changes:

  + Only support ``Zope >= 4``, no longer support ``Zope2``.
  + Drop support for Python 2.6.

- No longer use deprecated import for getSite/setSite.
  [jensens]

- Update code to follow Plone styleguide.
  [gforcada]


5.1.1 (2017-04-19)
------------------

- Do not break on import of ``plone.testing.z2`` when using `zope.testbrowser` >= 5.0 which no longer depends on `mechanize`.


5.1 (2017-04-13)
----------------

- Fix for ZODB 5: Abort transaction before DB close.
  [jensens, jimfulton]

- Remove BBB code and imports for Zope < 2.13.
  [thet]

- Fix issue, which prevented using layered-helper on Python 3.
  [datakurre]

- Fix ``.z2.Startup.setUpZCML()`` to be compatible with Zope >= 4.0a2.
  [icemac]

- Fix version pins on the package itself to be able to run the tests.
  [gforcada]

5.0.0 (2016-02-19)
------------------

Rerelease of 4.2.0 as 5.0.0.

The version 4.2.0 had changed error handling in the public api, causing exceptions where before everything continued to work.


4.2.0 (2016-02-18)
------------------

New:

- Refuse to work if user breaks test isolation.
  [do3cc]
- Check that tests don't run together with ZopeTestCase
  [do3cc]

Fixes:

- Fix tests for Zope 4, where the app root Control_Panel is not available anymore.
  [thet]


4.1.0 (2016-01-08)
------------------

Fixes:

- Rename all txt doctest files to rst. Reformat doctests.
  [thet]

- PEP 8.
  [thet]

- Depend on zope.testrunner, which was moved out from zope.testing.testrunner.
  [thet]

- Add support for Zope 4.
  [thet]


4.0.15 (2015-08-14)
-------------------

- Prevent exception masking in finally clause of zopeApp context.
  [do3cc]


4.0.14 (2015-07-29)
-------------------

- Rerelease for clarity due to double release of 4.0.13.
  [maurits]

- Added ``multiinit``-parameter to z2.installProduct to allow multiple initialize methods for a package
  [tomgross]


4.0.13 (2015-03-13)
-------------------

- Really fix not to depend on unittest2.
  [icemac]

- Add tox.ini
  [icemac]


4.0.12 (2014-09-07)
-------------------

- Fixed AttributeError when importing ``plone.testing.z2`` if ``zope.testbrowser`` 4.x is used but not ``zope.app.testing``.
  [icemac]

- Broke dependency on `unittest2` for Python 2.7+ as all features of `unittest2` are integrated in `unittest` there.
  [icemac]


4.0.11 (2014-02-22)
-------------------

- Fix z2.txt doctest for FTP_SERVER.
  [timo]


4.0.10 (2014-02-11)
-------------------

- Read 'FTPSERVER_HOST' and 'FTPSERVER_PORT' from the environment variables if possible.
  This allows us to run tests in parallel on CI servers.
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

- Fixed an issue where a query string would be unquoted twice;
  once while setting up the HTTP request and once in the handler (the publisher).
  [malthe]


4.0.4 (2012-08-04)
------------------

- Fixed the cache reset code.
  In some situations the function does not have any defaults,
  so we shouldn't try to clear out the app reference.
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
