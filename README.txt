Introduction
============

``plone.testing`` provides tools for writing unit and integration tests in a
Zope and Plone environment. It is not tied to Plone, and it does not depend on
Zope 2 (although it will provide some additional tools if you are using Zope 2).

``plone.testing`` builds on `zope.testing`_, in particular its layers concept.
This package also aims to promote some "good practice" for writing tests of
various types.

    Note: If you are working with Plone, there is also `plone.app.testing`_,
    which builds on ``plone.testing`` to provide additional layers useful for
    testing Plone add-on products.

If you are new to automated testing and test driven development, you should
spend some time learning about the core concepts. Some useful references
include:

* `The Wikipedia article on unit testing <http://en.wikipedia.org/wiki/Unit_testing>`_
* `The Dive Into Python chapter on testing <http://diveintopython.org/unit_testing/index.html>`_

Bear in mind that different Python frameworks have slightly different takes on
how to approach testing. Therefore, you may find examples that are slightly
different to those shown below. The basic concepts should be consistent,
however.

Definitions
-----------

In this documentation, we will use a number of testing-related terms. The
following definitions apply:

Unit test
    An automated test (i.e. one written in code) that tests a single unit
    (normally a function) in isolation. A unit test attempts to prove that the
    given function works as expected and gives the correct output given a
    particular input. It is common to have a number of unit tests for a single
    function, testing different inputs, including boundary cases and errors.
    Unit tests are typically quick to write and run.
Integration test
    An automated test that tests how a number of units interact. In a Zope
    context, this often pertains to how a particular object or view interacts
    with the Zope framework, the ZODB persistence engine, and so on. Integration
    tests usually require some setup and can be slower to run than unit tests.
    It is common to have fewer integration tests than unit test.
Functional test
    An automated test that tests a feature in an "end-to-end" fashion. In a Zope
    context, that normally means that it invokes an action in the same way
    that a user would, i.e. through a web request.Functional tests are normally
    slower to run than either unit or integration tests, and can be
    significantly slower to run. It is therefore common to have only a few
    functional tests for each major feature, relying on unit and integration
    tests for the bulk of testing.
Black box testing
    Testing which only considers the system's defined inputs and outputs. For
    example, a functional test is normally a black box test that provides inputs
    only through the defined interface (e.g. URLs published in a web
    application), and makes assertions only on end outputs (e.g. the
    response returned by those requests).
White box testing
    Testing which examines the internal state of a system to make assertions.
    Authors of unit and integration tests normally have significant knowledge of
    the implementation of the code under test, and can examine such things as
    data in a database or changes to the system's environment to determine
    if the test succeeded or failed.
Assertion
    A check that determines whether a test succeeds or fails. For example, if
    a unit test for the function ``foo()`` expects it to return the value 1,
    an assertion could be written to verify this fact. A test is said to *fail*
    if any of its assertions fail. A test always contains one or more
    assertions.
Test case
    A single unit, integration or functional test. Often shortened to just
    *test*. A test case sets up, executes and makes assertions against a single
    scenario that bears testing.
Test fixture
    The state used as a baseline for one or more tests. The test fixture is
    *set up* before each test is executed, and *torn down* afterwards. This
    is a pre-requisite in *test isolation* - the principle that tests should
    be independent of one another.
Test layer
    The configuration of a test fixture shared by a number of tests. All test
    cases that belong to a particular layer will be executed together. The
    layer is *set up* once before the tests are executed, and *torn down* once
    after. Layers may depend on one another. Any *base layers* are set up before
    and torn down after a particular layer is used. The test runner will order
    test execution to minimise layer setup and tear-down. For example, if some
    tests use layer A, some other tests use layer B, and both of these layers
    share layer C as a base layer, the test runner will set up C, set up A,
    execute the tests in A, tear down A, set up B, execute the tests in B, 
    tear down B, and finally tear down C.
Test suite
    A collection of test cases (and layers) that are executed together.
Test runner
    The program which executes tests. This is responsible for layer and test
    fixture set-up and tear-down. It also reports on the test run, usually by
    printing output to the console.
Coverage
    To have confidence in your code, you should ensure it iscovered by tests.
    That is, each line of code, and each possible branching point (loops, ``if``
    statements) should be executed by a test. This is known as *coverage*,
    and is normally measured as a percentage of lines of non-test code covered
    by tests. Coverage can be measured by the test runner, which keeps track
    of which lines of code were executed in a given test run.
Doctest
    A style of testing where tests are written as examples that could be typed
    into the interactive Python interpreter. The test runner executes each
    example and checks the actual output against the expected output. Doctests
    can either be placed in the docstring of a method, or in a separate file.
    The use of doctests is largely a personal preference. Some developers like
    to write documentation as doctests, which has the advantage that code
    samples can be automatically tested for correctness. You can read more
    about doctests on `Wikipedia <http://en.wikipedia.org/wiki/Doctest>`_.

Installation and usage
======================

To use ``plone.testing`` in your own package, you need to add it as a
dependency. Most people prefer to keep test-only dependencies separate, so that
they do not need to be installed in scenarios (such as on a production server)
where the tests will not be run. This can be achieved using a ``tests`` extra.

In ``setup.py``, add or modify the ``extras_require`` option, like so::

    extras_require = {
        'tests': [
                'plone.testing',
            ]
    },

You can add other test-only dependencies to that list as well, of course.

To run tests, you need a test runner. If you are using ``zc.buildout``, you can
install a test runner using the `zc.recipe.testrunner`_ recipe. For example, you
could add the following to your ``buildout.cfg``::

    [test]
    recipe = zc.recipe.testrunner
    eggs =
        my.package [tests]
    defaults = ['--exit-with-status', '--auto-color', '--auto-progress']

You'll also need to add this part to the ``parts`` list, of course::

    [buildout]
    parts =
        ...
        test

In this example, have listed a single package to test, called ``my.package``,
and asked for it to be installed with the ``[tests]`` extra. This will install
any regular dependencies (listed in the ``install_requires`` option in
``setup.py``), as well as those in the list associated with the ``tests`` key in
the ``extras_require`` option.

Note that it becomes important to properly list your dependencies here, because
the test runner will only be aware of the package explicitly listed, and their
dependencies. For example, if your package depends on Zope 2, you need to list
``Zope2`` in the ``install_requires`` list in ``setup.py``; ditto for ``Plone``,
or indeed any other package you import from.

Once you have re-run buildout, the test runner will be installed as ``bin/test`` 
(the executable name is taken from the name of the buildout part). You can run
it without arguments to run all tests of each egg listed in the ``eggs`` list::

    $ bin/test

If you have listed several eggs, and you want to run only one, you can do::

    $ bin/test -s my.package

There are other command line options, which you can find by running::

    $ bin/test --help

Also note the ``defaults`` option in the buildout configuration. This can be
used to set default command line options. Some commonly useful options are
shown above.

Coverage reporting
------------------

When writing tests, it is useful to know how well your tests cover your code.
`zope.testing`_ can report on coverage via the ``--coverage`` option::

    $ bin/test --coverage ../../coverage

This will place coverage reporting information in the ``coverage`` directory
inside your buildout. The ``../../`` prefix is necessary because the test runner
is actually executed in relation to the installation path for the ``test`` part,
which is usually ``parts/test``.

If you always want test coverage, you can add the coverage options to the
``defaults`` line in ``buildout.cfg``::

    defaults = ['--exit-with-status', '--auto-color', '--auto-progress', '--coverage', '../../coverage']

The coverage reporter will print a summary to the console, indicating percentage
coverage for each module, and write detailed information to the ``coverage``
directory as specified. For a more user-friendly report, you can use the
`z3c.coverage`_ tool to turn the coverage report into HTML.

To install `z3c.coverage`_, you can use a buildout part like the following::

    [buildout]
    parts =
        ...
        test
        coverage-report

    [coverage-report]
    recipe = zc.recipe.egg
    eggs = z3c.coverage
    arguments = ('coverage', 'report')

After re-running buildout, you can convert the contents of an existing
``coverage`` directory into an HTML by running::

    $ bin/coveragereport

As you might have guessed, the ``arguments`` option specifies the "raw" coverage
report directory, and the output directory for the HTML report.

Layers
======




Writing tests
=============

Tests in Python
---------------

Doctests
--------

Layer reference
===============

.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _plone.app.testing: http://pypi.python.org/pypi/plone.app.testing
.. _zc.recipe.testrunner: http://pypi.python.org/pypi/zc.recipe.testrunner
.. _z3c.coverage: http://pypi.python.org/pypi/z3c.coverage