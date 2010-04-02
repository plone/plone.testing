Introduction
============

.. contents:: Table of contents

``plone.testing`` provides tools for writing unit and integration tests in a
Zope and Plone environment. It is not tied to Plone, and it does not depend on
Zope 2 (although it will provide some additional tools if you are using Zope 2).

``plone.testing`` builds on `zope.testing`_, in particular its layers concept.
This package also aims to promote some "good practice" for writing tests of
various types.

    **Note:** If you are working with Plone, there is also `plone.app.testing`_,
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
Layer
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

In large part, ``plone.testing`` is about layers. It provides:

* A set of layers (outlined below), which you can use or extend.
* A set of tools for working with layers
* A mini-framework to make it easy to write layers

We'll discuss the last two items here.

Layer basics
------------

Layers are used to create test fixtures that are shared by multiple test cases.
For example, if you are writing a set of integration tests, you may need to set
up a database and configure various components to access that database. This
type of test fixture setup can be resource-intensive and time-consuming. If it
is possible to only perform the setup and tear-down once for a set of tests
without losing isolation between those tests, test runs can often be sped up
significantly.

At the most basic, a layer is an object with the following methods and
attributes:

``setUp()``
    Called by the test runner when the layer is to be set up. This is normally
    called exactly once during the test run.
``tearDown()``
    Called by the test runner when the layer is to be down down. As with
    ``setUp()``, this is normally called exactly once during the test run.
``testSetUp()``
    Called immediately before each test case that uses the layer is executed.
``testTearDown()``
    Called immediately after each test case that uses the layer is executed.
    This is a chance to perform any post-test cleanup to ensure the fixture
    is ready for the next test.
``__bases__``
    A tuple of base layers.

Each test case is associated with zero or one layer. (The syntax for specifying
the layer is shown in the section "Writing tests" below.) All the tests
associated with a given layer will be executed together.

Layers can depend on one another (as indicated in the ``__bases__`` tuple). Base
layers are set up before and torn down after their dependants. For example, if
the test runner is executing some tests that belong to layer A, and some other
tests that belong to layer B, both of which depend on layer C, the order of
execution might be::

    1. C.setUp()
    1.1. A.setUp()

    1.1.1. C.testSetUp()
    1.1.2. A.testSetUp()
    1.1.3. [A test using layer A]
    1.1.4. A.testTearDown()
    1.1.5. C.testTearDown()

    1.1.6. C.testSetUp()
    1.1.7. A.testSetUp()
    1.1.8. [Another test using layer A]
    1.1.9. A.testTearDown()
    1.1.10. C.testTearDown()

    1.2. A.tearDown()
    1.3. B.setUp()

    1.3.1. C.testSetUp()
    1.3.2. B.testSetUp()
    1.3.3. [A test using layer B]
    1.3.4. B.testTearDown()
    1.3.5. C.testTearDown()

    1.3.6. C.testSetUp()
    1.3.7. B.testSetUp()
    1.3.8. [Another test using layer B]
    1.3.9. B.testTearDown()
    1.3.10. C.testTearDown()

    1.4. B.tearDown()
    2. C.tearDown()

A bayer layer may of course depend on another base layer. In the case of nested
dependencies like this, the order of set up and tear-down as calculated by the
test runner is similar to the way in which Python searches for the method to
invoke in the case of multiple inheritance.

Writing layer
-------------

The easiest way to create a new layer is to use the ``Layer`` base class and
implement the ``setUp()``, ``tearDown()``, ``testSetUp()`` and
``testTearDown()`` methods as needed. All four are optional. The default
implementation of each does nothing.

By convention, layers are created in a module called ``testing.py`` at the top
level of your package. The idea is that other packages that extend your package
can re-use your layers for their own testing.

A simple layer may look like this:

    >>> from plone.testing import Layer
    >>> class SpaceShip(Layer):
    ...
    ...     def setUp(self):
    ...         print "Assembling space ship"
    ...     
    ...     def tearDown(self):
    ...         print "Disasembling space ship"
    ...     
    ...     def setUpTest(self):
    ...         print "Fuelling space ship in preparation for test"
    ...     
    ...     def tearDownTest(self)
    ...         print "Emptying the fuel tank"

    **Note:** You may find it useful to create other layer base or mix-in
    classes that extend ``plone.testing.Layer`` and provide helper methods for
    use in your own layers. This is perfectly acceptable, but please do not
    confuse a layer base class used in this manner with the concept of a *base
    layer* as documented above.
    
    Also note that the `zope.testing`_ documentation contains examples of layers
    that are "old-style" classes where the ``setUp()`` and ``tearDown()``
    methods are ``classmethod``s. Whilst this pattern works, we discourage its
    use, because the classes created using this pattern are not really used as
    classes. The concept of layer inheritance is slightly different from class
    inheritance, and using the ``class`` keyword to create layers with base
    layers leads to a number of "gotchas" that are best avoided.

Before this layer can be used, it must be instantiated. Layers are normally
instantiated exactly once, since by nature they are shared between tests. This
becomes important when you start to manage state (such as persistent data,
database connections, or other shared resources) in layers.

The layer instance is conventionally also found in ``testing.py``, just after
the layer class definition.

    >>> SPACE_SHIP = SpaceShip()

    **Note:** Since the layer is created in module scope, it will be
    constructed as soon as the ``testing`` module where it lives is imported.
    It is therefore very important that the layer class is inexpensive to
    create. In general, you should avoid doing anything non-trivial in the
    ``__init__()`` method of your layer class. All setup should happen in the
    ``setUp()`` class. If you *do* implement ``__init__()``, be sure to call
    the ``super`` version as well.

The layer shown above did not have any base layers (dependencies). Here is an
example of another layer that depends on the example layer above:

    >>> class ZIGSpaceShip(Layer):
    ...     __bases__ = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         print "Installing main canon"

    >>> ZIG = ZIGSpaceShip()

Here, we have explicitly listed the base layers on which ``MyOtherLayer``
depends, by setting the ``__bases__`` tuple. Note that we used the layer
*instance* in the ``__bases__`` tuple, not the class.

    **Note:** In this example, we have only implemented one method. Presumably,
    the ZIG layer does not require any tear-down to leave a clean state for the
    next layer.

Advanced usage - overriding bases
---------------------------------

In some cases, it may be useful to create a copy of a layer, but change its
bases. One reason to do this may if you are re-using a layer from another
module, but need to change the order in which layers are set up and torn down.

Normally, you would just re-use the layer instance, either directly
in a test, or in the ``__bases__`` tuple of another layer. However, if you
need to change the bases, you can pass a new list of bases to the layer
constructor:

    >>> class CATSMessage(Layer)
    ...     
    ...     def setUp(self):
    ...         print "Somebody set up us the bomb"
    ...     
    ...     def tearDown(self):
    ...         print "All your base are belong to us"

    >>> CATS_MESSAGE = CATSMessage()

    >>> ZERO_WING = ZIGSpaceship((SPACE_SHIP, CATS_MESSAGE))

Please take great care when changing layer bases like this. The layer
implementation may make assumptions about the test fixture that was set up
by its bases. If you change the order in which the bases are listed, or remove
a base altogether, the layer may fail to set up correctly.

Also, the new layer instance is independent of the original layer instance, so
any resources defined in the layer are likely to be duplicated.

Layer resources
---------------

Many layers will manage one or more resources that are used either by other
layers, or by tests themselves. Examples may include database connections,
global objects (such as the Zope application root), or configuration data.

``plone.testing`` contains a simple resource storage that makes it easy to
access resources from dependant layers or tests. The resource storage uses
dictionary notation:

    >>> class WarpDrive(object):
    ...     """A shared resource"""
    ...     
    ...     def __init__(self, maxSpeed)
    ...         self.maxSpeed = maxSpeed
    ...     
    ...     def start(self, speed):
    ...         if speed > self.maxSpeed:
    ...             print "We need more power!"
    ...         else:
    ...             print "Going to warp at speed", speed
    ...     
    ...     def stop(self):
    ...         pass
    
    >>> class ConstitutionClassSpaceShip(Layer):
    ...     __bases__ = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         self['warpDrive'] = WarpDrive(8)
    ...
    ...     def tearDown(self):
    ...         del self['warpDrive']
    
    >>> CONSTITUTION_CLASS_SPACE_SHIP = ConstitutionClassSpaceShip()

    >>> class GalaxyClassSpaceShip(Layer):
    ...     __bases__ = (CONSTITUTION_CLASS_SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         # Upgrade the warp drive
    ...         self.previousMaxSpeed = self['warpDrive'].maxSpeed
    ...         self['warpDrive'].maxSpeed = 9.5
        
    >>> GALAXY_CLASS_SPACE_SHIP = GalaxyClassSpaceShip()

As shown, layers (that derive from ``plone.testing.Layer``) support item
(dict-like) assignment, access and deletion of arbitrary resources under string
keys.

A resource defined in a base layer is accessible through a child layer. If a
resource is set on a child using a key that also exists in a base layer, the
child version will shadow the base version when that key is used on the child
layer, but the base layer version is intact. Conversely, if (as shown above)
the child layer accesses and modifies the object, it will modify the original.

    **Note:** It is sometimes necessary (or desirable) to modify a shared
    resource in a child layer, as shown in the example above. In this case,
    however, it is very important to restore the original state when the layer
    is torn down. Otherwise, other layers or tests using the base layer directly
    may be affected in difficult-to-debug ways.

If the same key is used in multiple base layers, the rules for choosing which
version to use are similar to those that apply when choosing an attribute or
method to use in the case of multiple inheritance.

In the example above, we used the resource manager for the ``warpDrive`` object,
but we assigned the ``previousMaxSpeed`` variable to ``self``.  This is because
``previousMaxSpeed`` is internal to the layer and should not be shared with
any other layers that happen to use this layer as a base. Nor should it be used
by any test cases. Conversely, ``warpDrive`` is a shared resource that is
exposed to other layers and test cases.

The distinction becomes even more important when you consider how a test case
may access the shared resource. We'll discuss how to write test cases that use
layers shortly, but consider the following test:

    >>> import unittest
    >>> class TestFasterThanLightTravel(unittest.TestCase):
    ...     layer = GALAXY_CLASS_SPACE_SHIP
    ...     
    ...     def test_hyperdrive(self):
    ...         warpDrive = self.layer['warpDrive']
    ...         warpDrive.start(8)

This test needs access to the shared resource. It knows that its layer defines
one called ``warpDrive``. It does not know or care that the warp drive was
actually initiated by the ``ConstitutionClassSpaceShip`` base layer.

If, however, the base layer had assigned the resource as an instance variable,
it would not inherit to child layers (remember: layer bases are not base
classes!). The syntax to access it would be
``self.layer.__bases__[0].warpDrive``, which is not only ugly, but brittle:
if the list of bases is changed, the expression above may lead to an attribute
error.

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