Introduction
============

.. contents:: Table of contents

``plone.testing`` provides tools for writing unit and integration tests in a
Zope and Plone environment. It is not tied to Plone, and it does not depend on
Zope 2 (although it will provide some additional tools if you are using Zope
2).

``plone.testing`` builds on `zope.testing`_, in particular its layers concept.
This package also aims to promote some "good practice" for writing tests of
various types.

    **Note:** If you are working with Plone, there is also
    `plone.app.testing`_, which builds on ``plone.testing`` to provide
    additional layers useful for testing Plone add-on products.

If you are new to automated testing and test driven development, you should
spend some time learning about those concepts. Some useful references include:

* `The Wikipedia article on unit testing <http://en.wikipedia.org/wiki/Unit_testing>`_
* `The Dive Into Python chapter on testing <http://diveintopython.org/unit_testing/index.html>`_

Bear in mind that different Python frameworks have slightly different takes on
how to approach testing. Therefore, you may find examples that are different
to those shown below. The core concepts should be consistent, however.

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
    with the Zope framework, the ZODB persistence engine, and so on.
    Integration tests usually require some setup and can be slower to run than
    unit tests. It is common to have fewer integration tests than unit test.
Functional test
    An automated test that tests a feature in an "end-to-end" fashion. In a
    Zope context, that normally means that it invokes an action in the same
    way that a user would, i.e. through a web request.Functional tests are
    normally slower to run than either unit or integration tests, and can be
    significantly slower to run. It is therefore common to have only a few
    functional tests for each major feature, relying on unit and integration
    tests for the bulk of testing.
Black box testing
    Testing which only considers the system's defined inputs and outputs. For
    example, a functional test is normally a black box test that provides
    inputs only through the defined interface (e.g. URLs published in a web
    application), and makes assertions only on end outputs (e.g. the response
    returned for requests to those URLs).
White box testing
    Testing which examines the internal state of a system to make assertions.
    Authors of unit and integration tests normally have significant knowledge
    of the implementation of the code under test, and can examine such things
    as data in a database or changes to the system's environment to determine
    if the test succeeded or failed.
Assertion
    A check that determines whether a test succeeds or fails. For example, if
    a unit test for the function ``foo()`` expects it to return the value 1,
    an assertion could be written to verify this fact. A test is said to
    *fail* if any of its assertions fail. A test always contains one or more
    assertions.
Test case
    A single unit, integration or functional test. Often shortened to just
    *test*. A test case sets up, executes and makes assertions against a
    single scenario that bears testing.
Test fixture
    The state used as a baseline for one or more tests. The test fixture is
    *set up* before each test is executed, and *torn down* afterwards. This is
    a pre-requisite for *test isolation* - the principle that tests should be
    independent of one another.
Layer
    The configuration of a test fixture shared by a number of tests. All test
    cases that belong to a particular layer will be executed together. The
    layer is *set up* once before the tests are executed, and *torn down* once
    after. Layers may depend on one another. Any *base layers* are set up
    before and torn down after a particular *child layer* is used. The test
    runner will order test execution to minimise layer setup and tear-down.
Test suite
    A collection of test cases (and layers) that are executed together.
Test runner
    The program which executes tests. This is responsible for calling layer
    and test fixture set-up and tear-down methods. It also reports on the test
    run, usually by printing output to the console.
Coverage
    To have confidence in your code, you should ensure it is adequately
    covered by tests. That is, each line of code, and each possible branching
    point (loops, ``if`` statements) should be executed by a test. This is
    known as *coverage*, and is normally measured as a percentage of lines of
    non-test code covered by tests. Coverage can be measured by the test
    runner, which keeps track of which lines of code were executed in a given
    test run.
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
dependency. Most people prefer to keep test-only dependencies separate, so
that they do not need to be installed in scenarios (such as on a production
server) where the tests will not be run. This can be achieved using a
``tests`` extra.

In ``setup.py``, add or modify the ``extras_require`` option, like so::

    extras_require = {
        'tests': [
                'plone.testing',
            ]
    },

You can add other test-only dependencies to that list as well, of course.

To run tests, you need a test runner. If you are using ``zc.buildout``, you
can install a test runner using the `zc.recipe.testrunner`_ recipe. For
example, you could add the following to your ``buildout.cfg``::

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
``setup.py``), as well as those in the list associated with the ``tests`` key
in the ``extras_require`` option.

Note that it becomes important to properly list your dependencies here,
because the test runner will only be aware of the packages explicitly listed,
and their dependencies. For example, if your package depends on Zope 2, you
need to list ``Zope2`` in the ``install_requires`` list in ``setup.py``; ditto
for ``Plone``, or indeed any other package you import from.

Once you have re-run buildout, the test runner will be installed as
``bin/test`` (the executable name is taken from the name of the buildout
part). You can run it without arguments to run all tests of each egg listed in
the ``eggs`` list::

    $ bin/test

If you have listed several eggs, and you want to run the tests for a
particular one, you can do::

    $ bin/test -s my.package

If you want to run only a particular test within this package, use the ``-t``
option. This can be passed a regular expression matching either a doctest file
name or a test method name.

    $ bin/test -s my.package -t test_spaceship

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
inside your buildout root. The ``../../`` prefix is necessary because the test
runner is actually executed in relation to the installation path for the
``test`` part, which is usually ``parts/test``.

If you always want test coverage, you can add the coverage options to the
``defaults`` line in ``buildout.cfg``::

    defaults = ['--exit-with-status', '--auto-color', '--auto-progress', '--coverage', '../../coverage']

The coverage reporter will print a summary to the console, indicating
percentage coverage for each module, and write detailed information to the
``coverage`` directory as specified. For a more user-friendly report, you can
use the `z3c.coverage`_ tool to turn the coverage report into HTML.

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

As you might have guessed, the ``arguments`` option specifies the "raw"
coverage report directory, and the output directory for the HTML report.

Layers
======

In large part, ``plone.testing`` is about layers. It provides:

* A set of layers (outlined below), which you can use or extend.
* A set of tools for working with layers
* A mini-framework to make it easy to write layers

We'll discuss the last two items here.

Layer basics
------------

Layers are used to create test fixtures that are shared by multiple test
cases. For example, if you are writing a set of integration tests, you may
need to set up a database and configure various components to access that
database. This type of test fixture setup can be resource-intensive and
time-consuming. If it is possible to only perform the setup and tear-down once
for a set of tests without losing isolation between those tests, test runs can
often be sped up significantly.

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

Each test case is associated with zero or one layer. (The syntax for
specifying the layer is shown in the section "Writing tests" below.) All the
tests associated with a given layer will be executed together.

Layers can depend on one another (as indicated in the ``__bases__`` tuple).
Base layers are set up before and torn down after their dependants. For
example, if the test runner is executing some tests that belong to layer A,
and some other tests that belong to layer B, both of which depend on layer C,
the order of execution might be::

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

A base layer may of course depend on other base layers. In the case of nested
dependencies like this, the order of set up and tear-down as calculated by the
test runner is similar to the way in which Python searches for the method to
invoke in the case of multiple inheritance.

Writing layers
--------------

The easiest way to create a new layer is to use the ``Layer`` base class and
implement the ``setUp()``, ``tearDown()``, ``testSetUp()`` and
``testTearDown()`` methods as needed. All four are optional. The default
implementation of each does nothing.

By convention, layers are created in a module called ``testing.py`` at the top
level of your package. The idea is that other packages that extend your
package can re-use your layers for their own testing.

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
    ...     def tearDownTest(self):
    ...         print "Emptying the fuel tank"

    **Note:** You may find it useful to create other layer base/mix-in classes
    that extend ``plone.testing.Layer`` and provide helper methods for use in
    your own layers. This is perfectly acceptable, but please do not confuse a
    layer base class used in this manner with the concept of a *base layer* as
    documented above.
    
    Also note that the `zope.testing`_ documentation contains examples of
    layers that are "old-style" classes where the ``setUp()`` and
    ``tearDown()`` methods are ``classmethod``s and class inheritance syntax
    is used to specify base layers. Whilst this pattern works, we discourage
    its use, because the classes created using this pattern are not really
    used as classes. The concept of layer inheritance is slightly different
    from class inheritance, and using the ``class`` keyword to create layers
    with base layers leads to a number of "gotchas" that are best avoided.

Before this layer can be used, it must be instantiated. Layers are normally
instantiated exactly once, since by nature they are shared between tests. This
becomes important when you start to manage resources (such as persistent data,
database connections, or other shared resources) in layers.

The layer instance is conventionally also found in ``testing.py``, just after
the layer class definition.

    >>> SPACE_SHIP = SpaceShip()

    **Note:** Since the layer is instantiated in module scope, it will be
    created as soon as the ``testing`` module where it lives is imported. It
    is therefore very important that the layer class is inexpensive and safe
    to create. In general, you should avoid doing anything non-trivial in the
    ``__init__()`` method of your layer class. All setup should happen in the
    ``setUp()`` method. If you *do* implement ``__init__()``, be sure to call
    the ``super`` version as well.

The layer shown above did not have any base layers (dependencies). Here is an
example of another layer that depends on it:

    >>> class ZIGSpaceShip(Layer):
    ...     __bases__ = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         print "Installing main canon"

    >>> ZIG = ZIGSpaceShip()

Here, we have explicitly listed the base layers on which ``ZIGSpaceShip``
depends, by setting the ``__bases__`` tuple.

Note that we use the layer *instance* in the ``__bases__`` tuple, not the
class. Layer dependencies always pertain to specific layer instances. Above,
we are really saying that *instances* of ``ZIGSpaceShip`` will, by default,
require the ``SPACE_SHIP`` layer to be set up first.

Advanced - overriding bases
---------------------------

In some cases, it may be useful to create a copy of a layer, but change its
bases. One reason to do this may if you are re-using a layer from another
module, and you need to change the order in which layers are set up and torn
down.

Normally, of course, you would just re-use the layer instance, either directly
in a test, or in the ``__bases__`` tuple of another layer, but if you need to
change the bases, you can pass a new list of bases to the layer instance
constructor:

    >>> class CATSMessage(Layer):
    ...
    ...     def setUp(self):
    ...         print "All your base are belong to us"
    ...     
    ...     def tearDown(self):
    ...         print "For great justice"

    >>> CATS_MESSAGE = CATSMessage()

    >>> ZERO_WING = ZIGSpaceShip((SPACE_SHIP, CATS_MESSAGE,))

Please take great care when changing layer bases like this. The layer
implementation may make assumptions about the test fixture that was set up
by its bases. If you change the order in which the bases are listed, or remove
a base altogether, the layer may fail to set up correctly.

Also, bear in mind that the new layer instance is independent of the original
layer instance, so any resources defined in the layer are likely to be
duplicated.

Layer combinations
------------------

Sometimes, it is useful to be able to combine several layers into one, without
adding any new fixture. One way to do this is to use the ``Layer`` class
directly and instantiate it with new bases:

    >>> COMBI_LAYER = Layer((CATS_MESSAGE, SPACE_SHIP,), name="Combi")

Here, we have created a "no-op" layer with two bases: ``CATS_MESSAGE`` and
``SPACE_SHIP``, named ``Combi``.

Please note that when using ``Layer`` directly like this, the ``name``
argument is required. This is to allow the test runner to identify the layer
correctly.

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
    ...     def __init__(self, maxSpeed):
    ...         self.maxSpeed = maxSpeed
    ...         self.running = False
    ...     
    ...     def start(self, speed):
    ...         if speed > self.maxSpeed:
    ...             print "We need more power!"
    ...         else:
    ...             print "Going to warp at speed", speed
    ...             self.running = True
    ...     
    ...     def stop(self):
    ...         self.running = False
    
    >>> class ConstitutionClassSpaceShip(Layer):
    ...     __bases__ = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         self['warpDrive'] = WarpDrive(8.0)
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
(dict-like) assignment, access and deletion of arbitrary resources under
string keys.

A resource defined in a base layer is accessible through a child layer. If a
resource is set on a child using a key that also exists in a base layer, the
child version will shadow the base version when that key is used on the child
layer, but the base layer version is intact. Conversely, if (as shown above)
the child layer accesses and modifies the object, it will modify the original.

    **Note:** It is sometimes necessary (or desirable) to modify a shared
    resource in a child layer, as shown in the example above. In this case,
    however, it is very important to restore the original state when the layer
    is torn down. Otherwise, other layers or tests using the base layer
    directly may be affected in difficult-to-debug ways.

If the same key is used in multiple base layers, the rules for choosing which
version to use are similar to those that apply when choosing an attribute or
method to use in the case of multiple inheritance.

In the example above, we used the resource manager for the ``warpDrive``
object, but we assigned the ``previousMaxSpeed`` variable to ``self``. This is
because ``previousMaxSpeed`` is internal to the layer and should not be shared
with any other layers that happen to use this layer as a base. Nor should it
be used by any test cases. Conversely, ``warpDrive`` is a shared resource that
is exposed to other layers and test cases.

The distinction becomes even more important when you consider how a test case
may access the shared resource. We'll discuss how to write test cases that use
layers shortly, but consider the following test:

    >>> import unittest2 as unittest
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
classes!). The syntax to access it would be::

    self.layer.__bases__[0].warpDrive
    
which is not only ugly, but brittle: if the list of bases is changed, the
expression above may lead to an attribute error.

Writing tests
=============

Tests are usually written in one of two ways: As methods on a class, sometimes
known as "Python tests" or "JUnit-style tests"; or using doctest syntax.

You should realise that although the relevant frameworks (``unittest``,
``unittest2`` and ``doctest``) often talk about unit testing, these tools are
also used to write integration and functional tests. The distinction between
unit, integration and functional tests is largely practical: you use the same
techniques to set up a fixture or write assertions for an integration test as
you would for a unit test. The difference lies in what that fixture contains, 
and how you invoke the code under test. In general, a true unit test will have
a minimal or no test fixture, whereas an integration test will have a fixture
that contains the components your code is integrating with. A functional test
will have a fixture that contains enough of the full system to execute an
"end-to-end" test.

Python tests
------------

Python tests use the Python `unittest`_ module, or its cousin `unittest2`_
(see below). They should be placed in a module or package called ``tests``.
For small packages, a single module called ``tests.py`` will normally contain
all tests. For larger packages, it is common to have a ``tests`` module that
contains a number of modules with tests. These need to start with the word
``test``, e.g. ``test_foo.py`` or ``test_bar.py``. Don't forget the
``__init__.py`` either.

unittest2
~~~~~~~~~

In Python 2.7+, the ``unittest`` module has grown several new and useful
features. To make use of these in Python 2.4, 2.5 and 2.6, an add-on module
called `unittest2`_ can be installed. Simply replace all uses of the
``unittest`` module with ``unittest2``. ``plone.testing`` depends on
``unittest2`` (and uses it for its own tests), so you will have access to it
if you depend on ``plone.testing``.

We will use ``unittest2`` for the examples in this document, but import it
with an alias of ``unittest``. This makes the code forward compatible with
Python 2.7, where the built-in ``unittest`` module will have all the features
of the ``unittest2`` module.

Please note that the `zope.testing`_ test runner at the time of writing
(version 3.9.3) does not (yet) support the new ``setUpClass()``,
``tearDownClass()``, ``setUpModule()`` and ``tearDownModule()`` hooks from
``unittest2``. This is not normally a problem, since we tend to use layers to
manage complex fixtures.

Test modules, classes and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python tests are written in classes that derive from the base class
``TestCase``. Each test is written as a method that takes no arguments and
has a name starting with ``test``. Other methods can be added and called from
test methods as appropriate, e.g. to share some test logic.

Two special methods, ``setUp()`` and ``tearDown()``, can also be added. These
will be called before or after each test, respectively, and provide a useful
place to construct and clean up test fixtures without writing a custom layer.
They are obviously not as re-usable as layers, though.

A layer can be specified by setting the ``layer`` class attribute to a layer
instance. If layers are used in conjunction with ``setUp()`` and
``tearDown()`` methods in the test class itself, the class' ``setUp()`` method
will be called after the layer's ``setUpTest()`` method, and the class'
``tearDown()`` method will be called before the layer's ``tearDownTest()``
method.

The ``TestCase`` base class contains a number of methods which can be used to
write assertions. They all take the form ``self.assertSomething()``, e.g.
``self.assertEqual(result, expectedValue)``. See the `unittest`_ and/or
`unittest2`_ documentation for details.

Putting this together, let's expand on our previous example unit test:

    >>> import unittest2 as unittest

    >>> class TestFasterThanLightTravel(unittest.TestCase):
    ...     layer = GALAXY_CLASS_SPACE_SHIP
    ...     
    ...     def setUp(self):
    ...         self.warpDrive = self.layer['warpDrive']
    ...         self.warpDrive.stop()
    ...     
    ...     def tearDown(self):
    ...         self.warpDrive.stop()
    ...     
    ...     def test_warp8(self):
    ...         self.warpDrive.start(8)
    ...         self.assertEqual(self.warpDrive.running, True)
    ...     
    ...     def test_max_speed(self):
    ...         tooFast = self.warpDrive.maxSpeed + 0.1
    ...         self.warpDrive.start(tooFast)
    ...         self.assertEqual(self.warpDrive.running, False)
    
A few things to note:

* The class derives from ``unittest.TestCase``.
* The ``layer`` class attribute is set to a layer instance (not a layer
  class!) defined previously. This would typically be imported from a
  ``testing`` module.
* We have used the ``setUp()`` method to fetch the ``warpDrive`` resource and
  ensure that it is stopped before each test is executed. Assigning a variable
  to ``self`` is a useful way to provide some state to each test method,
  though be careful about data leaking between tests: in general, you cannot
  predict the order in which tests will run, and tests should always be
  independent.
* We have used the ``tearDown()`` method to make sure the warp
  drive is really stopped after each test.
* There are two tests here: ``test_warp8()`` and ``test_max_speed()``.
* We have used the ``self.assertEqual()`` assertion in both tests to check the
  result of executing the ``start()`` method on the warp drive.

Test suite
~~~~~~~~~~

If you are using version 3.8.0 or later of `zope.testing`_, a class like the
one above is all you need: any class deriving from ``TestCase`` in a module
with a name starting with ``test`` will be examined for test methods. Those
tests are then collected into a test suite and executed.

With older versions of `zope.testing`_, you need to add a ``test_suite()`` in
each module that returns the tests in the test suite. The `unittest`_ module
contains several tools to construct suites, but one of the simplest is to use
the default test loader and load all tests in the current module:

    >>> def test_suite():
    ...     return unittest.defaultTestLoader.loadTestsFromName(__name__)

If you need to load tests explicitly, you can use the ``TestSuite`` API from
the `unittest`_ module. For example:

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.makeSuite(TestFasterThanLightTravel)
    ...     ])
    ...     return suite

The ``makeSuite()`` function creates a test suite from the test methods in
the given class (which must derive from ``TestCase``). This suite is then
appended to an overall suite, which is returned from the ``test_suite()``
method. Note that ``addTests()`` takes a list of suites. We'll add additional
suites later.

See the `unittest`_ documentation for other options.

    **Note:** Adding a ``test_suite()`` method to a module disables automatic
    test discovery, even when using a recent version of ``zope.testing``.

Doctests
--------

Doctests can be written in two ways: as the contents of a docstring (usually,
but not always, as a means of illustrating and testing the functionality of
the method or class where the docstring appears), or as a separate text file.
In both cases, the standard `doctest`_ module is used. See its documentation
for details about doctest syntax and conventions.

Docstring doctests
~~~~~~~~~~~~~~~~~~

Doctests can be added to any module, class or function docstring::

    def canOutrunKlingons(warpDrive):
        """Find out of the given warp drive can outrun Klingons.
        
        Klingons travel at warp 8
        
        >>> drive = WarpDrive(5)
        >>> canOutrunKlingons(drive)
        False
        
        We have to be faster than that to outrun them.
        
        >>> drive = WarpDrive(8.1)
        >>> canOutrunKlingons(drive)
        True
        
        We can't outrun them if we're travelling exactly the same speed
        
        >>> drive = WarpDrive(8.0)
        >>> canOutrunKlingons(drive)
        False

        """
        return warpDrive.maxSpeed > 8.0

To add the doctests from a particular module to a test suite, you need to
use the ``test_suite()`` function hook:
    
    >>> import doctest
    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.makeSuite(TestFasterThanLightTravel),
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...     ])
    ...     return suite

Here, we have given the name of the module to check as a string dotted name.
It is also possible to import a module and pass it as an object. The code
above passes a list to ``addTests()``, making it easy to add several sets of
tests to the suite: the list can contain be constructed from calls to
``DocTestSuite()``, ``DocFileSuite()`` (shown below) and ``makeSuite()``
(shown above).

    Remember that if you add a ``test_suite()`` function to a module that
    also has ``TestCase``-derived python tests, those tests will no longer
    be automatically picked up, so you need to add them to the test suite
    explicitly.

File doctests
~~~~~~~~~~~~~

Doctests contained in a file are similar. For example, if we had a file called
``spaceship.txt`` with doctests, we could add it to the test suite above 
with:

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.makeSuite(TestFasterThanLightTravel),
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...         doctest.DocFileSuite('spaceship.txt'),
    ...     ])
    ...     return suite

By default, the file is located relative to the module where the the test
suite is defined. You can use ``../`` to reference the parent directory,
which is sometimes useful if the doctest is inside a module in a ``tests``
package.

It is possible to pass several tests to the suite, e.g.::

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.makeSuite(TestFasterThanLightTravel),
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...         doctest.DocFileSuite('spaceship.txt', 'warpdrive.txt',),
    ...     ])
    ...     return suite

Doctest fixtures and layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A docstring doctest will by default have access to any global symbol available
in the module (e.g. anything defined or imported in the module). The global
namespace can be overridden by passing a ``globs`` keyword argument to the
``DocTestSuite()`` constructor, or augmented by passing an ``extraglobs``
argument. Both should be given dictionaries.

A file doctest has an empty globals namespace by default. Globals may be
provided via the ``globs`` argument to ``DocFileSuite()``.

To manage a simple test fixture for a doctest, you can define set-up and
tear-down functions and pass them as the ``setUp`` and ``tearDown``
arguments respectively. These both take a single arugment, a ``DocTest``
object. The most useful attribute of this object is ``globs``, which is a
mutable dictionary of globals available in the test.

For example:

    >>> def setUpKlingons(doctest):
    ...     doctest.globs['oldStyleKlings'] = True
    
    >>> def tearDownKlingons(doctest):
    ...     doctest.globs['oldStyleKlings'] = False

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         doctest.DocTestSuite('spaceship.utils', setUp=setUpKlingons, tearDown=tearDownKlingons),
    ...     ])
    ...     return suite

The same arguments are available on the ``DocFileSuite()`` constructor. The
set up method is called before each docstring in the given module for a
``DocTestSuite``, and before each file given in a ``DocFileSuite``.

Of course, we often want to use layers with doctests too. Unfortunately,
the ``unittest`` API is not aware of layers, so you can't just pass a layer
to the ``DocTestSuite()`` and ``DocFileSuite()`` constructors. Instead,
you have to set a ``layer`` attribute on the suite after it has been
constructed.

To make it easier to do this, ``plone.testing`` comes with a helper function
called ``layered()``. Its first argument is a test suite. The second argument
is the layer.

For example:

    >>> from plone.testing import layered
    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         layered(doctest.DocTestSuite('spaceship.utils'), layer=CONSTITUTION_CLASS_SPACE_SHIP),
    ...     ])
    ...     return suite

This is equivalent to:

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     
    ...     spaceshipUtilTests = doctest.DocTestSuite('spaceship.utils')
    ...     spaceshipUtilTests.layer = CONSTITUTION_CLASS_SPACE_SHIP
    ...     suite.addTest(spaceshipUtilTests)
    ...     
    ...     return suite

In this example, we've opted to use ``addTest()`` to add a single suite,
instead of using ``addTests()`` to add multiple suites in one go.

Zope testing tools
==================

Everything described so far in this document relies only on the standard
`unittest`_/`unittest2`_ and `doctest`_ modules and `zope.testing`_, and you
can use this package without any other dependencies.

However, there are also some tools (and layers) available in this package, as
well as in other packages, that are specifically useful for testing
applications that use the Zope application framework.

Test cleanup
------------

If a test uses a global registry, it may be necessary to clean that registry
on set up and tear down of each test fixture. ``zope.testing`` provides a
mechanism to register cleanup handlers - methods that are called to clean
up global state. This can then be invoked in the ``setUp()`` and 
`tearDown()`` fixture lifecycle methods of a test case.

    >>> from zope.testing import cleanup

Let's say we had a global registry, implemented as a dictionary

    >>> SOME_GLOBAL_REGISTRY = {}

If we wanted to clean this up on each test run, we could call ``clear()``
on the dict. Since that's a no-argument method, it is perfect as a cleanup
handler.

    >>> cleanup.addCleanUp(SOME_GLOBAL_REGISTRY.clear)

We can now use the ``cleanUp()`` method to execute all registered 
cleanups:

    >>> cleanup.cleanUp()

This call could be placed in a ``setUp()`` and/or ``tearDow()`` method in a
test class, for example.

Event testing
-------------

You may wish to test some code that uses ``zope.event`` to fire specific
events. `zope.component`_ provides some helpers to capture and analyse
events.

    >>> from zope.component import eventtesting

To use this, you first need to set up event testing. Some of the layers
shown below will do this for you, but you can do it yourself by calling
the ``eventtesting.setUp()`` method, e.g. from your own ``setUp()`` method:

    >>> eventtesting.setUp()

This simply registers a few catch-all event handlers. Once you have
executed the code that is expected to fire events, you can use the
``getEvents()`` helper function to obtain a list of the event instances
caught:

    >>> events = eventtesting.getEvents()

You can now examine ``events`` to see what events have been caught since the
last cleanup.

``getEvents()`` takes two optional arguments that can be used to filter the
returned list of events. The first (``event_type``) is an interface. If given,
only events providing this interface are returned. The second (``filter``) is
a callable taking one argument. If given, it will be called with each captured
event. Only those events where the filter function returns ``True`` will be
included.

The ``eventtesting`` module registers a cleanup action as outlined above. When
you call ``cleanup.cleanUp()`` (or ``eventtesting.clearEvents()``, which is
the handler it registers), the events list will be cleared, ready for the
next test.

Mock requests
-------------

Many tests require a request object, often with particular request/form
variables set. `zope.publisher`_ contains a useful class for this purpose.

    >>> from zope.publisher.browser import TestRequest

A simple test request can be constructed with no arguments:

    >>> request = TestRequest()

To add a body input stream, pass a ``StringIO`` or file as the first
parameter. To set the environment (request headers), use the ``environ``
keyword argument. To simulate a submitted and marshalled form, use the
``form`` keyword argument:

    >>> request = TestRequest(form=dict(field1='foo', field2=1))

Note that the ``form`` dict contains marshalled form fields, so modifiers like
``:int`` or ``:boolean`` should not be included in the field names, and
values should be converted to the appropriate type.

Registering components
----------------------

Many test fixtures will depend on having a minimum of Zope Component
Architecture (ZCA) components registered. In normal operation, these would
probably be registered via ZCML, but in a unit test, you should avoid loading
the full ZCML configuration of your package (and its dependencies).

Instead, you can use the Python API in `zope.component`_ to register
global components instantly. The three most commonly used functions are:

    >>> from zope.component import provideAdapter
    >>> from zope.component import provideUtility
    >>> from zope.component import provideHandler

See the `zope.component`_ documentation for details about how to use these.

When registering global components like this, it is important to avoid
test leakage. The ``cleanup`` mechanism outlined above can be used to tear
down the component registry between each test.

Loading ZCML
------------

Integration tests often need to load ZCML configuration. This can be achieved
using the ``zope.configuration`` API.

    >>> from zope.configuration import xmlconfig

The ``xmlconfig`` module contains two useful methods. ``xmlconfig.string()``
can be used to load a literal string of ZCML:

    >>> xmlconfig.string("""\
    ... <configure xmlns="http://namespaces.zope.org/zope" package="plone.testing">
    ...     <include package="zope.component" file="meta.zcml" />
    ... </configure>
    ... """) # doctest: +ELLIPSIS
    <zope.configuration.config.ConfigurationMachine object at ...>

Note that we need to set a package (used for relative imports and file
locations) explicitly here.

Also note that unless the optional second argument (``context``) is passed,
a new configuration machine will be created every time ``string()`` is called.
It therefore becomes necessary to explicitly ``<include />`` the files that
contains the directives you want to use (the one in ``zope.component`` is a
common example). Layers that set up ZCML configuration may expose a resource
which can be passed as the ``context`` parameter.

To load the configuration for a particular package, use ``xmlconfig.file()``:

    >>> import zope.component
    >>> context = xmlconfig.file('meta.zcml', zope.component)
    >>> xmlconfig.file('configure.zcml', zope.component, context=context) # doctest: +ELLIPSIS
    <zope.configuration.config.ConfigurationMachine object at ...>

This takes two required arguments: the file name and the module relative to
which it is to be found. Here, we have loaded two files: ``meta.zcml`` and
``configure.zcml``. The first call to ``xmlconfig.file()`` creates and
returns a configuration context. We re-use that for the subsequent invocation,
so that the directives configured are available.

Installing a Zope 2 product
---------------------------

Some packages (including all those in the ``Products.*`` namespace) have the
special status of being Zope 2 "products". These are recorded in a special
registry viewable through the Zope Management Interface, and may have an
``initialize()`` hook in their top-level ``__init__.py`` that needs to be
called for the package to be fully configured.

Zope 2 will find and execute any products during startup. For testing, we
need to explicitly list the products to install. Provided you are using
``plone.testing`` with Zope 2, you can use the following:

    >>> from plone.testing.z2 import installProduct
    >>> installProduct('Products.ZCatalog')

Note:

* Unlike the similarly-named function from ``ZopeTestCase``, this helper
  will work with any type of product. There is no distinction between a
  "product" and a "package" (and no ``installPackage()``).
* Installing a product in this manner is independent of ZCML configuration.
  However, it is almost always necessary to install the package's ZCML
  configuration first.

Layer reference
===============

``plone.testing`` comes with several layers that are available to use directly
or extend. These are outlined below.

Zope Component Architecture: sandbox
------------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.SANDBOX``                    |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.Sandbox``                    |
+------------+--------------------------------------------------+
| Bases:     | None                                             |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer does not set up a fixture per se, but performs a cleanup
before and after each test, using ``zope.testing.cleanup`` as described
above.

The net result is that each test has a clean global component registry. Thus,
it is safe to use the `zope.component`_ Python API (``provideAdapter()``,
``provideUtility()``, ``provideHandler()`` and so on) to register components.

Be careful about using this layer in combination with other layers. Because
it tears down the component registry between each test, it will clobber any
layer that sets up more permanent test fixture in the component registry.

Zope Component Architecture: Placeless setup
--------------------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.PLACELESS``                  |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.Placeless``                  |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.SANDBOX``                    |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

TODO - describe

Zope Component Architecture: Basic ZCML directives
--------------------------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.ZCML_DIRECTIVES``            |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.ZCMLDirectives``             |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.PLACELESS``                  |
+------------+--------------------------------------------------+
| Resources: | ``configurationContext``                         |
+------------+--------------------------------------------------+

TODO - describe

Zope Component Architecture: ZCML browser directives
----------------------------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.ZCML_BROWSER_DIRECTIVES``    |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.ZCMLBrowserDirectives``      |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.ZCML_DIRECTIVES``            |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

TODO - describe

ZODB: Basic persistent sandbox
------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zodb.EMPTY_ZODB``                |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zodb.EmptyZODB``                 |
+------------+--------------------------------------------------+
| Bases:     |  None                                            |
+------------+--------------------------------------------------+
| Resources: | ``zodbRoot``                                     |
+------------+--------------------------------------------------+

TODO - describe

Zope 2: Basic site
------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.z2.BASIC_SITE``                  |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.z2.BasicSite``                   |
+------------+--------------------------------------------------+
| Bases:     | None                                             |
+------------+--------------------------------------------------+
| Resources: | ``applicationRoot``                              |
|            +--------------------------------------------------+
|            | ``rootUser``                                     |
+------------+--------------------------------------------------+

TODO - describe

NOTE: We have to avoid using Five's load_site() anywhere - it is too brittle
because it loads things in the environment not related to the package under
test.

Zope 2: HTTP ZServer thread
---------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.z2.ZSERVER``                     |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.z2.ZServer``                     |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.z2.BASIC_SITE``                  |
+------------+--------------------------------------------------+
| Resources: | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

TODO - describe

.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _plone.app.testing: http://pypi.python.org/pypi/plone.app.testing
.. _zc.recipe.testrunner: http://pypi.python.org/pypi/zc.recipe.testrunner
.. _z3c.coverage: http://pypi.python.org/pypi/z3c.coverage
.. _unittest: http://doc.python.org/library/unittest.html
.. _unittest2: http://pypi.python.org/pypi/unittest2
.. _doctest: http://docs.python.org/dev/library/doctest.html
