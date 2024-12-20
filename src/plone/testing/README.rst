Introduction
============

.. contents:: Table of contents

``plone.testing`` provides tools for writing unit and integration tests in a Zope and Plone environment.
It is not tied to Plone, and it does not depend on Zope (although it has some optional Zope-only features).

``plone.testing`` builds on `zope.testing`_, in particular its layers concept.
This package also aims to promote some "good practice" for writing tests of various types.

.. note::

   If you are working with Plone, there is a complementary package `plone.app.testing`_, which builds on ``plone.testing`` to provide additional layers useful for testing Plone add-ons.

If you are new to automated testing and test driven development, you should spend some time learning about those concepts.
Some useful references include:

* `The Wikipedia article on unit testing <https://en.wikipedia.org/wiki/Unit_testing>`_
* `The Dive Into Python chapter on testing <https://diveintopython3.problemsolving.io/unit-testing.html>`_

Bear in mind that different Python frameworks have slightly different takes on how to approach testing.
Therefore, you may find examples that are different to those shown below.
The core concepts should be consistent, however.

Compatibility
-------------

``plone.testing`` 7.x has been tested with Python 2.7 and 3.6.
If you're using the optional Zope layers, you must use Zope version 4 or later.
Look at older ``plone.testing`` versions for supporting older Zope versions.

Definitions
-----------

In this documentation, we will use a number of testing-related terms.
The following definitions apply:

Unit test
    An automated test (i.e. one written in code) that tests a single unit (normally a function) in isolation.
    A unit test attempts to prove that the given function works as expected and gives the correct output given a particular input.
    It is common to have a number of unit tests for a single function, testing different inputs, including boundary cases and errors.
    Unit tests are typically quick to write and run.

Integration test
    An automated test that tests how a number of units interact.
    In a Zope context, this often pertains to how a particular object or view interacts with the Zope framework, the ZODB persistence engine, and so on.
    Integration tests usually require some setup and can be slower to run than unit tests.
    It is common to have fewer integration tests than unit test.

Functional test
    An automated test that tests a feature in an "end-to-end" fashion.
    In a Zope context, that normally means that it invokes an action in the same way that a user would, i.e. through a web request.
    Functional tests are normally slower to run than either unit or integration tests, and can be significantly slower to run.
    It is therefore common to have only a few functional tests for each major feature, relying on unit and integration tests for the bulk of testing.

Black box testing
    Testing which only considers the system's defined inputs and outputs.
    For example, a functional test is normally a black box test that provides inputs only through the defined interface (e.g. URLs published in a web application), and makes assertions only on end outputs (e.g. the response returned for requests to those URLs).

White box testing
    Testing which examines the internal state of a system to make assertions.
    Authors of unit and integration tests normally have significant knowledge of the implementation of the code under test, and can examine such things as data in a database or changes to the system's environment to determine if the test succeeded or failed.

Assertion
    A check that determines whether a test succeeds or fails.
    For example, if a unit test for the function ``foo()`` expects it to return the value 1, an assertion could be written to verify this fact.
    A test is said to *fail* if any of its assertions fail.
    A test always contains one or more assertions.

Test case
    A single unit, integration or functional test.
    Often shortened to just *test*.
    A test case sets up, executes and makes assertions against a single scenario that bears testing.

Test fixture
    The state used as a baseline for one or more tests.
    The test fixture is *set up* before each test is executed, and *torn down* afterwards.
    This is a pre-requisite for *test isolation* - the principle that tests should be independent of one another.

Layer
    The configuration of a test fixture shared by a number of tests.
    All test cases that belong to a particular layer will be executed together.
    The layer is *set up* once before the tests are executed, and *torn down* once after.
    Layers may depend on one another.
    Any *base layers* are set up before and torn down after a particular *child layer* is used.
    The test runner will order test execution to minimise layer setup and tear-down.

Test suite
    A collection of test cases (and layers) that are executed together.

Test runner
    The program which executes tests.
    This is responsible for calling layer and test fixture set-up and tear-down methods.
    It also reports on the test run, usually by printing output to the console.

Coverage
    To have confidence in your code, you should ensure it is adequately covered by tests.
    That is, each line of code, and each possible branching point (loops, ``if`` statements) should be executed by a test.
    This is known as *coverage*, and is normally measured as a percentage of lines of non-test code covered by tests.
    Coverage can be measured by the test runner, which keeps track of which lines of code were executed in a given test run.

Doctest
    A style of testing where tests are written as examples that could be typed into the interactive Python interpreter.
    The test runner executes each example and checks the actual output against the expected output.
    Doctests can either be placed in the docstring of a method, or in a separate file.
    The use of doctests is largely a personal preference.
    Some developers like to write documentation as doctests, which has the advantage that code samples can be automatically tested for correctness.
    You can read more about doctests on `Wikipedia <http://en.wikipedia.org/wiki/Doctest>`_.

Installation and usage
======================

To use ``plone.testing`` in your own package, you need to add it as a dependency.
Most people prefer to keep test-only dependencies separate, so that they do not need to be installed in scenarios (such as on a production server) where the tests will not be run.
This can be achieved using a ``test`` extra.

In ``setup.py``, add or modify the ``extras_require`` option, like so:::

    extras_require = {
        'test': [
                'plone.testing',
            ]
    },

You can add other test-only dependencies to that list as well, of course.

To run tests, you need a test runner.
If you are using ``zc.buildout``, you can install a test runner using the `zc.recipe.testrunner`_ recipe.
For example, you could add the following to your ``buildout.cfg``:::

    [test]
    recipe = zc.recipe.testrunner
    eggs =
        my.package [test]
    defaults = ['--auto-color', '--auto-progress']

You'll also need to add this part to the ``parts`` list, of course:::

    [buildout]
    parts =
        ...
        test

In this example, have listed a single package to test, called ``my.package``, and asked for it to be installed with the ``[test]`` extra.
This will install any regular dependencies (listed in the ``install_requires`` option in ``setup.py``), as well as those in the list associated with the ``test`` key in the ``extras_require`` option.

Note that it becomes important to properly list your dependencies here, because the test runner will only be aware of the packages explicitly listed, and their dependencies.
For example, if your package depends on Zope, you need to list ``Zope`` in the ``install_requires`` list in ``setup.py``;
ditto for ``Plone``, or indeed any other package you import from.

Once you have re-run buildout, the test runner will be installed as ``bin/test`` (the executable name is taken from the name of the buildout part).
You can execute it without arguments to run all tests of each egg listed in the ``eggs`` list::

    $ bin/test

If you have listed several eggs, and you want to run the tests for a particular one, you can do::

    $ bin/test -s my.package

If you want to run only a particular test within this package, use the ``-t`` option.
This can be passed a regular expression matching either a doctest file name or a test method name.::

    $ bin/test -s my.package -t test_spaceship

There are other command line options, which you can find by running::

    $ bin/test --help

Also note the ``defaults`` option in the buildout configuration.
This can be used to set default command line options.
Some commonly useful options are shown above.

Coverage reporting
------------------

When writing tests, it is useful to know how well your tests cover your code.
You can create coverage reports via the excellent `coverage`_ library.
In order to use it, we need to install it and a reporting script::

    [buildout]
    parts =
        ...
        test
        coverage
        report

    [coverage]
    recipe = zc.recipe.egg
    eggs = coverage
    initialization =
        include = '--source=${buildout:directory}/src'
        sys.argv = sys.argv[:] + ['run', include, 'bin/test', '--all']

    [report]
    recipe = zc.recipe.egg
    eggs = coverage
    scripts = coverage=report
    initialization =
        sys.argv = sys.argv[:] + ['html', '-i']

This will run the ``bin/test`` script with arguments like `--all` to run all layers.
You can also specify no or some other arguments.
It will place coverage reporting information in a ``.coverage`` file inside your buildout root.
Via the ``--source`` argument you specify the directories containing code you want to cover.
The coverage script would otherwise generate coverage information for all executed code, including other packages and even the standard library.

Running the ``bin/report`` script will generate a human readable HTML representation of the run in the `htmlcov` directory.
Open the contained `index.html` in a browser to see the result.

If you want to generate an XML representation suitable for the `Cobertura`_ plugin of `Jenkins`_, you can add another part::

    [buildout]
    parts =
        ...
        report-xml

    [report-xml]
    recipe = zc.recipe.egg
    eggs = coverage
    scripts = coverage=report-xml
    initialization =
        sys.argv = sys.argv[:] + ['xml', '-i']

This will generate a ``coverage.xml`` file in the buildout root.

Optional dependencies
---------------------

``plone.testing`` comes with a core set of tools for managing layers, which depends only on `zope.testing`_.
In addition, there are several layers and helper functions which can be used in your own tests (or as bases for your own layers).
Some of these have deeper dependencies.
However, these dependencies are optional and not installed by default.
If you don't use the relevant layers, you can safely ignore them.

``plone.testing`` does specify these dependencies, however, using the ``setuptools`` "extras" feature.
You can depend on one or more extras in your own ``setup.py`` ``install_requires`` or ``extras_require`` option using the same square bracket notation shown for the ``[test]`` buildout part above.
For example, if you need both the ``zca`` and ``publisher`` extras, you can have the following in your ``setup.py``::

    extras_require = {
        'test': [
                'plone.testing [zca, publisher]',
            ]
    },

The available extras are:

``zodb``
    ZODB testing.
    Depends on ``ZODB``.
    The relevant layers and helpers are in the module ``plone.testing.zodb``.

``zca``
    Zope Component Architecture testing.
    Depends on core Zope Component Architecture packages such as ``zope.component`` and ``zope.event``.
    The relevant layers and helpers are in the module ``plone.testing.zca``.

``security``
    Security testing.
    Depends on ``zope.security``.
    The relevant layers and helpers are in the module ``plone.testing.security``.

``publisher``
    Zope Publisher testing.
    Depends on ``zope.publisher``, ``zope.browsermenu``, ``zope.browserpage``, ``zope.browserresource`` and ``zope.security`` and sets up ZCML directives.
    The relevant layers and helpers are in the module ``plone.testing.publisher``.

``zope`` (For backwards compatibility there is also ``z2``.)

    Zope testing.
    Depends on the ``Zope`` egg, which includes all the dependencies of the Zope application server.
    The relevant layers and helpers are in the module ``plone.testing.zope``.

``zserver``

    Tests against the ``ZServer``. (Python 2 only!) Requires additionally to use the ``zope`` extra.
    The relevant layers and helpers are in the module ``plone.testing.zserver``


Adding a test buildout to your package
--------------------------------------

When creating reusable, mostly stand-alone packages, it is often useful to be able to include a buildout with the package sources itself that can be used to create a test runner.
This is a popular approach for many Zope packages, for example.
In fact, ``plone.testing`` itself uses this kind of layout.

To have a self-contained buildout in your package, the following is required:

* You need a ``buildout.cfg`` at the root of the package.

* In most cases, you always want a ``bootstrap.py`` file to make it easier for people to set up a fresh buildout.

* Your package sources need to be inside a ``src`` directory.
  If you're using namespace packages, that means the top level package should be in the ``src`` directory.

* The ``src`` directory must be referenced in ``setup.py``.

For example, ``plone.testing`` has the following layout::

    plone.testing/
    plone.testing/setup.py
    plone.testing/bootstrap.py
    plone.testing/buildout.cfg
    plone.testing/README.rst
    plone.testing/src/
    plone.testing/src/plone
    plone.testing/src/plone/__init__.py
    plone.testing/src/plone/testing/
    plone.testing/src/plone/testing/*

In ``setup.py``, the following arguments are required::

        packages=find_packages('src'),
        package_dir={'': 'src'},

This tells ``setuptools`` where to find the source code.

The ``buildout.cfg`` for ``plone.testing`` looks like this::

    [buildout]
    extends =
        http://download.zope.org/Zope2/index/2.12.12/versions.cfg
    parts = coverage test report report-xml
    develop = .

    [test]
    recipe = collective.xmltestreport
    eggs =
        plone.testing [test]
    defaults = ['--auto-color', '--auto-progress']

    [coverage]
    recipe = zc.recipe.egg
    eggs = coverage
    initialization =
        include = '--source=${buildout:directory}/src'
        sys.argv = sys.argv[:] + ['run', include, 'bin/test', '--all', '--xml']

    [report]
    recipe = zc.recipe.egg
    eggs = coverage
    scripts = coverage=report
    initialization =
        sys.argv = sys.argv[:] + ['html', '-i']

    [report-xml]
    recipe = zc.recipe.egg
    eggs = coverage
    scripts = coverage=report-xml
    initialization =
        sys.argv = sys.argv[:] + ['xml', '-i']

Obviously, you should adjust the package name in the ``eggs`` list and the version set in the ``extends`` line as appropriate.

You can of course also add additional buildout parts, for example to include some development/debugging tools, or even a running application server for testing purposes.

    *Hint:* If you use this package layout, you should avoid checking any files or directories generated by buildout into your version control repository.
    You want to ignore:

    * ``.coverage``
    * ``.installed.cfg``
    * ``bin``
    * ``coverage.xml``
    * ``develop-eggs``
    * ``htmlcov``
    * ``parts``
    * ``src/*.egg-info``

Layers
======

In large part, ``plone.testing`` is about layers.
It provides:

* A set of layers (outlined below), which you can use or extend.

* A set of tools for working with layers

* A mini-framework to make it easy to write layers and manage shared resources associated with layers.

We'll discuss the last two items here, before showing how to write tests that use layers.

Layer basics
------------

Layers are used to create test fixtures that are shared by multiple test cases.
For example, if you are writing a set of integration tests, you may need to set up a database and configure various components to access that database.
This type of test fixture setup can be resource-intensive and time-consuming.
If it is possible to only perform the setup and tear-down once for a set of tests without losing isolation between those tests, test runs can often be sped up significantly.

Layers also allow reuse of test fixtures and set-up/tear-down code.
``plone.testing`` provides a number of useful (but optional) layers that manage test fixtures for common Zope testing scenarios, letting you focus on the actual test authoring.

At the most basic, a layer is an object with the following methods and attributes:

``setUp()``
    Called by the test runner when the layer is to be set up.
    This is called exactly once for each layer used during a test run.

``tearDown()``
    Called by the test runner when the layer is to be torn down.
    As with ``setUp()``, this is called exactly once for each layer.

``testSetUp()``
    Called immediately before each test case that uses the layer is executed.
    This is useful for setting up aspects of the fixture that are managed on a per-test basis, as opposed to fixture shared among all tests.

``testTearDown()``
    Called immediately after each test case that uses the layer is executed.
    This is a chance to perform any post-test cleanup to ensure the fixture is ready for the next test.

``__bases__``
    A tuple of base layers.

Each test case is associated with zero or one layer.
(The syntax for specifying the layer is shown in the section "Writing tests" below.) All the tests associated with a given layer will be executed together.

Layers can depend on one another (as indicated in the ``__bases__`` tuple), allowing one layer to build on the fixture created by another.
Base layers are set up before and torn down after their dependants.

For example, if the test runner is executing some tests that belong to layer A, and some other tests that belong to layer B, both of which depend on layer C, the order of execution might be::

    1. C.setUp()
    1.1. A.setUp()

    1.1.1. C.testSetUp()
    1.1.2. A.testSetUp()
    1.1.3. [One test using layer A]
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
    1.3.3. [One test using layer B]
    1.3.4. B.testTearDown()
    1.3.5. C.testTearDown()

    1.3.6. C.testSetUp()
    1.3.7. B.testSetUp()
    1.3.8. [Another test using layer B]
    1.3.9. B.testTearDown()
    1.3.10. C.testTearDown()

    1.4. B.tearDown()
    2. C.tearDown()

A base layer may of course depend on other base layers.
In the case of nested dependencies like this, the order of set up and tear-down as calculated by the test runner is similar to the way in which Python searches for the method to invoke in the case of multiple inheritance.

Writing layers
--------------

The easiest way to create a new layer is to use the ``Layer`` base class and implement the ``setUp()``, ``tearDown()``, ``testSetUp()`` and ``testTearDown()`` methods as needed.
All four are optional.
The default implementation of each does nothing.

By convention, layers are created in a module called ``testing.py`` at the top level of your package.
The idea is that other packages that extend your package can reuse your layers for their own testing.

A simple layer may look like this::

    >>> from plone.testing import Layer
    >>> class SpaceShip(Layer):
    ...
    ...     def setUp(self):
    ...         print("Assembling space ship")
    ...
    ...     def tearDown(self):
    ...         print("Disasembling space ship")
    ...
    ...     def testSetUp(self):
    ...         print("Fuelling space ship in preparation for test")
    ...
    ...     def testTearDown(self):
    ...         print("Emptying the fuel tank")

Before this layer can be used, it must be instantiated.
Layers are normally instantiated exactly once, since by nature they are shared between tests.
This becomes important when you start to manage resources (such as persistent data, database connections, or other shared resources) in layers.

The layer instance is conventionally also found in ``testing.py``, just after the layer class definition.::

    >>> SPACE_SHIP = SpaceShip()

.. note::

    Since the layer is instantiated in module scope, it will be created as soon as the ``testing`` module is imported.
    It is therefore very important that the layer class is inexpensive and safe to create.
    In general, you should avoid doing anything non-trivial in the ``__init__()`` method of your layer class.
    All setup should happen in the ``setUp()`` method.
    If you *do* implement ``__init__()``, be sure to call the ``super`` version as well.

The layer shown above did not have any base layers (dependencies).
Here is an example of another layer that depends on it:::

    >>> class ZIGSpaceShip(Layer):
    ...     defaultBases = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         print("Installing main canon")

    >>> ZIG = ZIGSpaceShip()

Here, we have explicitly listed the base layers on which ``ZIGSpaceShip`` depends, in the ``defaultBases`` attribute.
This is used by the ``Layer`` base class to set the layer bases in a way that can also be overridden: see below.

Note that we use the layer *instance* in the ``defaultBases`` tuple, not the class.
Layer dependencies always pertain to specific layer instances.
Above, we are really saying that *instances* of ``ZIGSpaceShip`` will, by default, require the ``SPACE_SHIP`` layer to be set up first.

.. note::

    You may find it useful to create other layer base/mix-in classes that extend ``plone.testing.Layer`` and provide helper methods for use in your own layers.
    This is perfectly acceptable, but please do not confuse a layer base class used in this manner with the concept of a *base layer* as described above:

    * A class deriving from ``plone.testing.Layer`` is known as a *layer class*.
      It defines the behaviour of the layer by implementing the lifecycle methods ``setUp()``, ``tearDown()``, ``testSetUp()`` and/or ``testTearDown()``.

    * A layer class can be instantiated into an actual layer.
      When a layer is associated with a test, it is the layer *instance* that is used.

    * The instance is usually a shared, module-global object, although in some cases it is useful to create copies of layers by instantiating the class more than once.

    * Subclassing an existing layer class is just straightforward OOP reuse: the test runner is not aware of the subclassing relationship.

    * A layer *instance* can be associated with any number of layer *bases*, via its ``__bases__`` property (which is usually via the ``defaultBases`` variable in the class body and/or overridden using the ``bases`` argument to the ``Layer`` constructor).
      These bases are layer *instances*, not classes.
      The test runner will inspect the ``__bases__`` attribute of each layer instance it sets up to calculate layer pre-requisites and dependencies.

    Also note that the `zope.testing`_ documentation contains examples of layers that are "old-style" classes where the ``setUp()`` and ``tearDown()`` methods are ``classmethod`` methods and class inheritance syntax is used to specify base layers.
    Whilst this pattern works, we discourage its use, because the classes created using this pattern are not really used as classes.
    The concept of layer bases is slightly different from class inheritance, and using the ``class`` keyword to create layers with base layers leads to a number of "gotchas" that are best avoided.

Advanced - overriding bases
---------------------------

In some cases, it may be useful to create a copy of a layer, but change its bases.
One reason to do this may if you are reusing a layer from another module, and you need to change the order in which layers are set up and torn down.

Normally, of course, you would just reuse the layer instance, either directly in a test, or in the ``defaultBases`` tuple of another layer, but if you need to change the bases, you can pass a new list of bases to the layer instance constructor:::

    >>> class CATSMessage(Layer):
    ...
    ...     def setUp(self):
    ...         print("All your base are belong to us")
    ...
    ...     def tearDown(self):
    ...         print("For great justice")

    >>> CATS_MESSAGE = CATSMessage()

    >>> ZERO_WING = ZIGSpaceShip(bases=(SPACE_SHIP, CATS_MESSAGE,), name="ZIGSpaceShip:CATSMessage")

Please note that when overriding bases like this, the ``name`` argument is required.
This is because each layer (using in a given test run) must have a unique name.
The default is to use the layer class name, but this obviously only works for one instantiation.
Therefore, ``plone.testing`` requires a name when setting ``bases`` explicitly.

Please take great care when changing layer bases like this.
The layer implementation may make assumptions about the test fixture that was set up by its bases.
If you change the order in which the bases are listed, or remove a base altogether, the layer may fail to set up correctly.

Also, bear in mind that the new layer instance is independent of the original layer instance, so any resources defined in the layer are likely to be duplicated.

Layer combinations
------------------

Sometimes, it is useful to be able to combine several layers into one, without adding any new fixture.
One way to do this is to use the ``Layer`` class directly and instantiate it with new bases:::

    >>> COMBI_LAYER = Layer(bases=(CATS_MESSAGE, SPACE_SHIP,), name="Combi")

Here, we have created a "no-op" layer with two bases: ``CATS_MESSAGE`` and ``SPACE_SHIP``, named ``Combi``.

Please note that when using ``Layer`` directly like this, the ``name`` argument is required.
This is to allow the test runner to identify the layer correctly.
Normally, the class name of the layer is used as a basis for the name, but when using the ``Layer`` base class directly, this is unlikely to be unique or descriptive.

Layer resources
---------------

Many layers will manage one or more resources that are used either by other layers, or by tests themselves.
Examples may include database connections, thread-local objects, or configuration data.

``plone.testing`` contains a simple resource storage abstraction that makes it easy to access resources from dependent layers or tests.
The resource storage uses dictionary notation:::

    >>> class WarpDrive(object):
    ...     """A shared resource"""
    ...
    ...     def __init__(self, maxSpeed):
    ...         self.maxSpeed = maxSpeed
    ...         self.running = False
    ...
    ...     def start(self, speed):
    ...         if speed > self.maxSpeed:
    ...             print("We need more power!")
    ...         else:
    ...             print("Going to warp at speed", speed)
    ...             self.running = True
    ...
    ...     def stop(self):
    ...         self.running = False

    >>> class ConstitutionClassSpaceShip(Layer):
    ...     defaultBases = (SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         self['warpDrive'] = WarpDrive(8.0)
    ...
    ...     def tearDown(self):
    ...         del self['warpDrive']

    >>> CONSTITUTION_CLASS_SPACE_SHIP = ConstitutionClassSpaceShip()

    >>> class GalaxyClassSpaceShip(Layer):
    ...     defaultBases = (CONSTITUTION_CLASS_SPACE_SHIP,)
    ...
    ...     def setUp(self):
    ...         # Upgrade the warp drive
    ...         self.previousMaxSpeed = self['warpDrive'].maxSpeed
    ...         self['warpDrive'].maxSpeed = 9.5
    ...
    ...     def tearDown(self):
    ...         # Restore warp drive to its previous speed
    ...         self['warpDrive'].maxSpeed = self.previousMaxSpeed

    >>> GALAXY_CLASS_SPACE_SHIP = GalaxyClassSpaceShip()

As shown, layers (that derive from ``plone.testing.Layer``) support item (dict-like) assignment, access and deletion of arbitrary resources under string keys.

    **Important:** If a layer creates a resource (by assigning an object to a key on ``self`` as shown above) during fixture setup-up, it must also delete the resource on tear-down.
    Set-up and deletion should be symmetric: if the resource is assigned during ``setUp()`` it should be deleted in ``tearDown()``;
    if it's created in ``testSetUp()`` it should be deleted in ``testTearDown()``.

A resource defined in a base layer is accessible from and through a child layer.
If a resource is set on a child using a key that also exists in a base layer, the child version will shadow the base version until the child layer is torn down (presuming it deletes the resource, which it should), but the base layer version remains intact.

.. note::

    Accessing a resource is analogous to accessing an instance variable.
    For example, if a base layer assigns a resource to a given key in its ``setUp()`` method, a child layer shadows that resource with another object under the same key, the shadowed resource will by used during the ``testSetUp()`` and ``testTearDown()`` lifecycle methods if implemented by the *base* layer as well.
    This will be the case until the child layer "pops" the resource by deleting it, normally in its ``tearDown()``.

Conversely, if (as shown above) the child layer accesses and modifies the object, it will modify the original.

.. note::

   It is sometimes necessary (or desirable) to modify a shared resource in a child layer, as shown in the example above.  In this case, however, it is very important to restore the original state when the layer is torn down.  Otherwise, other layers or tests using the base layer directly may be affected in difficult-to-debug ways.

If the same key is used in multiple base layers, the rules for choosing which version to use are similar to those that apply when choosing an attribute or method to use in the case of multiple inheritance.

In the example above, we used the resource manager for the ``warpDrive`` object, but we assigned the ``previousMaxSpeed`` variable to ``self``.
This is because ``previousMaxSpeed`` is internal to the layer and should not be shared with any other layers that happen to use this layer as a base.
Nor should it be used by any test cases.
Conversely, ``warpDrive`` is a shared resource that is exposed to other layers and test cases.

The distinction becomes even more important when you consider how a test case may access the shared resource.
We'll discuss how to write test cases that use layers shortly, but consider the following test:::

    >>> import unittest
    >>> class TestFasterThanLightTravel(unittest.TestCase):
    ...     layer = GALAXY_CLASS_SPACE_SHIP
    ...
    ...     def test_hyperdrive(self):
    ...         warpDrive = self.layer['warpDrive']
    ...         warpDrive.start(8)

This test needs access to the shared resource.
It knows that its layer defines one called ``warpDrive``.
It does not know or care that the warp drive was actually initiated by the ``ConstitutionClassSpaceShip`` base layer.

If, however, the base layer had assigned the resource as an instance variable, it would not inherit to child layers (remember: layer bases are not base classes!).
The syntax to access it would be:::

    self.layer.__bases__[0].warpDrive

which is not only ugly, but brittle: if the list of bases is changed, the expression above may lead to an attribute error.

Writing tests
=============

Tests are usually written in one of two ways: As methods on a class that derives from ``unittest.TestCase`` (this is sometimes known as "Python tests" or "JUnit-style tests"), or using doctest syntax.

You should realise that although the relevant frameworks (``unittest`` and ``doctest``) often talk about unit testing, these tools are also used to write integration and functional tests.
The distinction between unit, integration and functional tests is largely practical: you use the same techniques to set up a fixture or write assertions for an integration test as you would for a unit test.
The difference lies in what that fixture contains, and how you invoke the code under test.
In general, a true unit test will have a minimal or no test fixture, whereas an integration test will have a fixture that contains the components your code is integrating with.
A functional test will have a fixture that contains enough of the full system to execute and test an "end-to-end" scenario.

Python tests
------------

Python tests use the Python `unittest`_ module.
They should be placed in a module or package called ``tests`` for the test runner to pick them up.

For small packages, a single module called ``tests.py`` will normally contain all tests.
For larger packages, it is common to have a ``tests`` package that contains a number of modules with tests.
These need to start with the word ``test``, e.g.
``tests/test_foo.py`` or ``tests/test_bar.py``.
Don't forget the ``__init__.py`` in the ``tests`` package, too!

unittest
~~~~~~~~

Please note that the `zope.testing`_ test runner at the time of writing (version 4.6.2) does not (yet) support the new ``setUpClass()``, ``tearDownClass()``, ``setUpModule()`` and ``tearDownModule()`` hooks from ``unittest``.
This is not normally a problem, since we tend to use layers to manage complex fixtures, but it is important to be aware of nonetheless.

Test modules, classes and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python tests are written with classes that derive from the base class ``TestCase``.
Each test is written as a method that takes no arguments and has a name starting with ``test``.
Other methods can be added and called from test methods as appropriate, e.g.
to share some test logic.

Two special methods, ``setUp()`` and ``tearDown()``, can also be added.
These will be called before or after each test, respectively, and provide a useful place to construct and clean up test fixtures without writing a custom layer.
They are obviously not as reusable as layers, though.

   *Hint:* Somewhat confusingly, the ``setUp()`` and ``tearDown()`` methods in a test case class are the equivalent of the ``testSetUp()`` and ``testTearDown()`` methods of a layer class.

A layer can be specified by setting the ``layer`` class attribute to a layer instance.
If layers are used in conjunction with ``setUp()`` and ``tearDown()`` methods in the test class itself, the class' ``setUp()`` method will be called after the layer's ``testSetUp()`` method, and the class' ``tearDown()`` method will be called before the layer's ``testTearDown()`` method.

The ``TestCase`` base class contains a number of methods which can be used to write assertions.
They all take the form ``self.assertSomething()``, e.g.
``self.assertEqual(result, expectedValue)``.
See the `unittest`_ documentation for details.

Putting this together, let's expand on our previous example unit test:::

    >>> import unittest

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

* The ``layer`` class attribute is set to a layer instance (not a layer class!) defined previously.
  This would typically be imported from a ``testing`` module.

* There are two tests here: ``test_warp8()`` and ``test_max_speed()``.

* We have used the ``self.assertEqual()`` assertion in both tests to check the result of executing the ``start()`` method on the warp drive.

* We have used the ``setUp()`` method to fetch the ``warpDrive`` resource and ensure that it is stopped before each test is executed.
  Assigning a variable to ``self`` is a useful way to provide some state to each test method, though be careful about data leaking between tests: in general, you cannot predict the order in which tests will run, and tests should always be independent.

* We have used the ``tearDown()`` method to make sure the warp drive is really stopped after each test.

Test suites
~~~~~~~~~~~

A class like the one above is all you need: any class deriving from ``TestCase`` in a module with a name starting with ``test`` will be examined for test methods.
Those tests are then collected into a test suite and executed.

See the `unittest`_ documentation for other options.

Doctests
--------

Doctests can be written in two ways: as the contents of a docstring (usually, but not always, as a means of illustrating and testing the functionality of the method or class where the docstring appears), or as a separate text file.
In both cases, the standard `doctest`_ module is used.
See its documentation for details about doctest syntax and conventions.

Doctests are used in two different ways:

* To test documentation.
  That is, to ensure that code examples contained in documentation are valid and continue to work as the software is updated.

* As a convenient syntax for writing tests.

These two approaches use the same testing APIs and techniques.
The difference is mostly about mindset.
However, it is important to avoid falling into the trap that tests can substitute for good documentation or vice-a-versa.
Tests usually need to systematically go through inputs and outputs and cover off a number of corner cases.
Documentation should tell a compelling narrative and usually focus on the main usage scenarios.
Trying to kill these two birds with one stone normally leaves you with an unappealing pile of stones and feathers.

Docstring doctests
~~~~~~~~~~~~~~~~~~

Doctests can be added to any module, class or function docstring:::

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

To add the doctests from a particular module to a test suite, you need to use the ``test_suite()`` function hook:::

    >>> import doctest
    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.defaultTestLoader.loadTestsFromTestCase(TestFasterThanLightTravel), # our previous test
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...     ])
    ...     return suite

Here, we have given the name of the module to check as a string dotted name.
It is also possible to import a module and pass it as an object.
The code above passes a list to ``addTests()``, making it easy to add several sets of tests to the suite: the list can be constructed from calls to ``DocTestSuite()``, ``DocFileSuite()`` (shown below) and ``unittest.defaultTestLoader.loadTestsFromTestCase()`` (shown above).

    Remember that if you add a ``test_suite()`` function to a module that also has ``TestCase``-derived python tests, those tests will no longer be automatically picked up by ``zope.testing``, so you need to add them to the test suite explicitly.

The example above illustrates a documentation-oriented doctest, where the doctest forms part of the docstring of a public module.
The same syntax can be used for more systematic unit tests.
For example, we could have a module ``spaceship.tests.test_spaceship`` with a set of methods like::

    # It's often better to put the import into each method, but here we've
    # imported the code under test at module level
    from spaceship.utils import WarpDrive, canOutrunKlingons

    def test_canOutrunKlingons_too_small():
        """Klingons travel at warp 8.0

        >>> drive = WarpDrive(7.9)
        >>> canOutrunKlingons(drive)
        False

        """

    def test_canOutrunKlingons_big():
        """Klingons travel at warp 8.0

        >>> drive = WarpDrive(8.1)
        >>> canOutrunKlingons(drive)
        True

        """

    def test_canOutrunKlingons_must_be_greater():
        """Klingons travel at warp 8.0

        >>> drive = WarpDrive(8.0)
        >>> canOutrunKlingons(drive)
        False

        """

Here, we have created a number of small methods that have no body.
They merely serve as a container for docstrings with doctests.
Since the module has no globals, each test must import the code under test, which helps make import errors more explicit.

File doctests
~~~~~~~~~~~~~

Doctests contained in a file are similar to those contained in docstrings.
File doctests are better suited to narrative documentation covering the usage of an entire module or package.

For example, if we had a file called ``spaceship.txt`` with doctests, we could add it to the test suite above with:::

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.defaultTestLoader.loadTestsFromTestCase(TestFasterThanLightTravel),
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...         doctest.DocFileSuite('spaceship.txt'),
    ...     ])
    ...     return suite

By default, the file is located relative to the module where the test suite is defined.
You can use ``../`` (even on Windows) to reference the parent directory, which is sometimes useful if the doctest is inside a module in a ``tests`` package.

.. note::

    If you put the doctest ``test_suite()`` method in a module inside a ``tests`` package, that module must have a name starting with ``test``.
    It is common to have ``tests/test_doctests.py`` that contains a single ``test_suite()`` method that returns a suite of multiple doctests.

It is possible to pass several tests to the suite, e.g.::

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         unittest.defaultTestLoader.loadTestsFromTestCase(TestFasterThanLightTravel),
    ...         doctest.DocTestSuite('spaceship.utils'),
    ...         doctest.DocFileSuite('spaceship.txt', 'warpdrive.txt',),
    ...     ])
    ...     return suite

The test runner will report each file as a separate test, i.e.
the ``DocFileSuite()`` above would add two tests to the overall suite.
Conversely, a ``DocTestSuite()`` using a module with more than one docstring containing doctests will report one test for each eligible docstring.

Doctest fixtures and layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A docstring doctest will by default have access to any global symbol available in the module where the docstring is found (e.g.
anything defined or imported in the module).
The global namespace can be overridden by passing a ``globs`` keyword argument to the ``DocTestSuite()`` constructor, or augmented by passing an ``extraglobs`` argument.
Both should be given dictionaries.

A file doctest has an empty globals namespace by default.
Globals may be provided via the ``globs`` argument to ``DocFileSuite()``.

To manage a simple test fixture for a doctest, you can define set-up and tear-down functions and pass them as the ``setUp`` and ``tearDown`` arguments respectively.
These are both passed a single argument, a ``DocTest`` object.
The most useful attribute of this object is ``globs``, which is a mutable dictionary of globals available in the test.

For example:::

    >>> def setUpKlingons(doctest):
    ...     doctest.globs['oldStyleKlingons'] = True

    >>> def tearDownKlingons(doctest):
    ...     doctest.globs['oldStyleKlingons'] = False

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         doctest.DocTestSuite('spaceship.utils', setUp=setUpKlingons, tearDown=tearDownKlingons),
    ...     ])
    ...     return suite

The same arguments are available on the ``DocFileSuite()`` constructor.
The set up method is called before each docstring in the given module for a ``DocTestSuite``, and before each file given in a ``DocFileSuite``.

Of course, we often want to use layers with doctests too.
Unfortunately, the ``unittest`` API is not aware of layers, so you can't just pass a layer to the ``DocTestSuite()`` and ``DocFileSuite()`` constructors.
Instead, you have to set a ``layer`` attribute on the suite after it has been constructed.

Furthermore, to use layer resources in a doctest, we need access to the layer instance.
The easiest way to do this is to pass it as a glob, conventionally called 'layer'.
This makes a global name 'layer' available in the doctest itself, giving access to the test's layer instance.

To make it easier to do this, ``plone.testing`` comes with a helper function called ``layered()``.
Its first argument is a test suite.
The second argument is the layer.

For example:::

    >>> from plone.testing import layered
    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         layered(doctest.DocTestSuite('spaceship.utils'), layer=CONSTITUTION_CLASS_SPACE_SHIP),
    ...     ])
    ...     return suite

This is equivalent to:::

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...
    ...     spaceshipUtilTests = doctest.DocTestSuite('spaceship.utils', globs={'layer': CONSTITUTION_CLASS_SPACE_SHIP})
    ...     spaceshipUtilTests.layer = CONSTITUTION_CLASS_SPACE_SHIP
    ...     suite.addTest(spaceshipUtilTests)
    ...
    ...     return suite

(In this example, we've opted to use ``addTest()`` to add a single suite, instead of using ``addTests()`` to add multiple suites in one go).

Zope testing tools
==================

Everything described so far in this document relies only on the standard `unittest`_ and `doctest`_ modules and `zope.testing`_, and you can use this package without any other dependencies.

However, there are also some tools (and layers) available in this package, as well as in other packages, that are specifically useful for testing applications that use various Zope-related frameworks.

Test cleanup
------------

If a test uses a global registry, it may be necessary to clean that registry on set up and tear down of each test fixture.
``zope.testing`` provides a mechanism to register cleanup handlers - methods that are called to clean up global state.
This can then be invoked in the ``setUp()`` and ``tearDown()`` fixture lifecycle methods of a test case.::

    >>> from zope.testing import cleanup

Let's say we had a global registry, implemented as a dictionary:::

    >>> SOME_GLOBAL_REGISTRY = {}

If we wanted to clean this up on each test run, we could call ``clear()`` on the dict.
Since that's a no-argument method, it is perfect as a cleanup handler.::

    >>> cleanup.addCleanUp(SOME_GLOBAL_REGISTRY.clear)

We can now use the ``cleanUp()`` method to execute all registered cleanups:::

    >>> cleanup.cleanUp()

This call could be placed in a ``setUp()`` and/or ``tearDown()`` method in a test class, for example.

Event testing
-------------

You may wish to test some code that uses ``zope.event`` to fire specific events.
`zope.component`_ provides some helpers to capture and analyse events.::

    >>> from zope.component import eventtesting

To use this, you first need to set up event testing.
Some of the layers shown below will do this for you, but you can do it yourself by calling the ``eventtesting.setUp()`` method, e.g.
from your own ``setUp()`` method:::

    >>> eventtesting.setUp()

This simply registers a few catch-all event handlers.
Once you have executed the code that is expected to fire events, you can use the ``getEvents()`` helper function to obtain a list of the event instances caught:::

    >>> events = eventtesting.getEvents()

You can now examine ``events`` to see what events have been caught since the last cleanup.

``getEvents()`` takes two optional arguments that can be used to filter the returned list of events.
The first (``event_type``) is an interface.
If given, only events providing this interface are returned.
The second (``filter``) is a callable taking one argument.
If given, it will be called with each captured event.
Only those events where the filter function returns ``True`` will be included.

The ``eventtesting`` module registers a cleanup action as outlined above.
When you call ``cleanup.cleanUp()`` (or ``eventtesting.clearEvents()``, which is the handler it registers), the events list will be cleared, ready for the next test.
Here, we'll do it manually:::

    >>> eventtesting.clearEvents()

Mock requests
-------------

Many tests require a request object, often with particular request/form variables set.
`zope.publisher`_ contains a useful class for this purpose.::

    >>> from zope.publisher.browser import TestRequest

A simple test request can be constructed with no arguments:::

    >>> request = TestRequest()

To add a body input stream, pass a ``StringIO`` or file as the first parameter.
To set the environment (request headers), use the ``environ`` keyword argument.
To simulate a submitted form, use the ``form`` keyword argument:::

    >>> request = TestRequest(form=dict(field1='foo', field2=1))

Note that the ``form`` dict contains marshalled form fields, so modifiers like ``:int`` or ``:boolean`` should not be included in the field names, and values should be converted to the appropriate type.

Registering components
----------------------

Many test fixtures will depend on having a minimum of Zope Component Architecture (ZCA) components registered.
In normal operation, these would probably be registered via ZCML, but in a unit test, you should avoid loading the full ZCML configuration of your package (and its dependencies).

Instead, you can use the Python API in `zope.component`_ to register global components instantly.
The three most commonly used functions are:::

    >>> from zope.component import provideAdapter
    >>> from zope.component import provideUtility
    >>> from zope.component import provideHandler

See the `zope.component`_ documentation for details about how to use these.

When registering global components like this, it is important to avoid test leakage.
The ``cleanup`` mechanism outlined above can be used to tear down the component registry between each test.
See also the ``plone.testing.zca.UNIT_TESTING`` layer, described below, which performs this cleanup automatically via the ``testSetUp()``/``testTearDown()`` mechanism.

Alternatively, you can "stack" a new global component registry using the ``plone.testing.zca.pushGlobalRegistry()`` and ``plone.testing.zca.popGlobalRegistry()`` helpers.
This makes it possible to set up and tear down components that are specific to a given layer, and even allow tests to safely call the global component API (or load ZCML - see below) with proper tear-down.
See the layer reference below for details.

Loading ZCML
------------

Integration tests often need to load ZCML configuration.
This can be achieved using the ``zope.configuration`` API.::

    >>> from zope.configuration import xmlconfig

The ``xmlconfig`` module contains two methods for loading ZCML.

``xmlconfig.string()`` can be used to load a literal string of ZCML:::

    >>> xmlconfig.string("""\
    ... <configure xmlns="http://namespaces.zope.org/zope" package="plone.testing">
    ...     <include package="zope.component" file="meta.zcml" />
    ... </configure>
    ... """)
    <zope.configuration.config.ConfigurationMachine object at ...>

Note that we need to set a package (used for relative imports and file locations) explicitly here, using the ``package`` attribute of the ``<configure />`` element.

Also note that unless the optional second argument (``context``) is passed, a new configuration machine will be created every time ``string()`` is called.
It therefore becomes necessary to explicitly ``<include />`` the files that contain the directives you want to use (the one in ``zope.component`` is a common example).
Layers that set up ZCML configuration may expose a resource which can be passed as the ``context`` parameter, usually called ``configurationContext`` - see below.

To load the configuration for a particular package, use ``xmlconfig.file()``:::

    >>> import zope.component
    >>> context = xmlconfig.file('meta.zcml', zope.component)
    >>> xmlconfig.file('configure.zcml', zope.component, context=context)
    <zope.configuration.config.ConfigurationMachine object at ...>

This takes two required arguments: the file name and the module relative to which it is to be found.
Here, we have loaded two files: ``meta.zcml`` and ``configure.zcml``.
The first call to ``xmlconfig.file()`` creates and returns a configuration context.
We reuse that for the subsequent invocation, so that the directives configured are available.

Installing a Zope product
-------------------------

Some packages (including all those in the ``Products.*`` namespace) have the special status of being Zope "products".
These are recorded in a special registry, and may have an ``initialize()`` hook in their top-level ``__init__.py`` that needs to be called for the package to be fully configured.

Zope 2 will find and execute any products during startup.
For testing, we need to explicitly list the products to install.
Provided you are using ``plone.testing`` with Zope, you can use the following:::

    from plone.testing import zope

    with zope.zopeApp() as app:
        zope.installProduct(app, 'Products.ZCatalog')

This would normally be used during layer ``setUp()``.
Note that the basic Zope application context must have been set up before doing this.
The usual way to ensure this, is to use a layer that is based on ``zope.STARTUP`` - see below.

To tear down such a layer, you should do:::

    from plone.testing import zope

    with zope.zopeApp() as app:
        zope.uninstallProduct(app, 'Products.ZCatalog')

Note:

* Unlike the similarly-named function from ``ZopeTestCase``, these helpers will work with any type of product.
  There is no distinction between a "product" and a "package" (and no ``installPackage()``).
  However, you must use the full name (``Products.*``) when registering a product.

* Installing a product in this manner is independent of ZCML configuration.
  However, it is almost always necessary to install the package's ZCML configuration first.

Functional testing
------------------

For functional tests that aim to simulate the browser, you can use `zope.testbrowser`_ in a Python test or doctest:::

    >>> from zope.testbrowser.browser import Browser
    >>> browser = Browser()

This provides a simple API to simulate browser input, without actually running a web server thread or scripting a live browser (as tools such as Selenium_ do).
The downside is that it is not possible to test JavaScript- dependent behaviour.

If you are testing a Zope application, you need to change the import location slightly, and pass the application root to the method:::

    from plone.testing.zope import Browser
    browser = Browser(app)

You can get the application root from the ``app`` resource in any of the Zope layers in this package.

Beyond that, the `zope.testbrowser`_ documentation should cover how to use the test browser.

    **Hint:** The test browser will usually commit at the end of a request.
    To avoid test fixture contamination, you should use a layer that fully isolates each test, such as the ``zope.INTEGRATION_TESTING`` layer described below.

Layer reference
===============

``plone.testing`` comes with several layers that are available to use directly or extend.
These are outlined below.

Zope Component Architecture
---------------------------

The Zope Component Architecture layers are found in the module ``plone.testing.zca``.
If you depend on this, you can use the ``[zca]`` extra when depending on ``plone.testing``.

Unit testing
~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.UNIT_TESTING``               |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.UnitTesting``                |
+------------+--------------------------------------------------+
| Bases:     | None                                             |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer does not set up a fixture per se, but cleans up global state before and after each test, using ``zope.testing.cleanup`` as described above.

The net result is that each test has a clean global component registry.
Thus, it is safe to use the `zope.component`_ Python API (``provideAdapter()``, ``provideUtility()``, ``provideHandler()`` and so on) to register components.

Be careful with using this layer in combination with other layers.
Because it tears down the component registry between each test, it will clobber any layer that sets up more permanent test fixture in the component registry.

Event testing
~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.EVENT_TESTING``              |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.EventTesting``               |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.UNIT_TESTING``               |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer extends the ``zca.UNIT_TESTING`` layer to enable the ``eventtesting`` support from ``zope.component``.
Using this layer, you can import and use ``zope.component.eventtesting.getEvent`` to inspect events fired by the code under test.

See above for details.

Layer cleanup
~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.LAYER_CLEANUP``              |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.LayerCleanup``               |
+------------+--------------------------------------------------+
| Bases:     | None                                             |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer calls the cleanup functions from ``zope.testing.cleanup`` on setup and tear-down (but not between each test).
It is useful as a base layer for other layers that need an environment as pristine as possible.

Basic ZCML directives
~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zca.ZCML_DIRECTIVES``            |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.ZCMLDirectives``             |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.LAYER_CLEANUP``              |
+------------+--------------------------------------------------+
| Resources: | ``configurationContext``                         |
+------------+--------------------------------------------------+

This registers a minimal set of ZCML directives, principally those found in the ``zope.component`` package, and makes available a configuration context.
This allows custom ZCML to be loaded as described above.

The ``configurationContext`` resource should be used when loading custom ZCML.
To ensure isolation, you should stack this using the ``stackConfigurationContext()`` helper.
For example, if you were writing a ``setUp()`` method in a layer that had ``zca.ZCML_DIRECTIVES`` as a base, you could do:::

    self['configurationContext'] = context = zca.stackConfigurationContext(self.get('configurationContext'))
    xmlconfig.string(someZCMLString, context=context)

This will create a new configuration context with the state of the base layer's context.
On tear-down, you should delete the layer-specific resource:::

    del self['configurationContext']

.. note::

   If you fail to do this, you may get problems if your layer is torn down and then needs to be set up again later.

See above for more details about loading custom ZCML in a layer or test.

ZCML files helper class
~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zca.ZCMLSandbox``                |
+------------+--------------------------------------------------+
| Resources: | ``configurationContext``                         |
+------------+--------------------------------------------------+

The ``ZCMLSandbox`` can be instantiated with a ``filename`` and ``package`` arguments::

    ZCML_SANDBOX = zca.ZCMLSandbox(filename="configure.zcml",
        package=my.package)


That layer ``setUp`` loads the ZCML file.
It avoids the need to using (and understand) ``configurationContext`` and ``globalRegistry`` until you need more flexibility or modularity for your layer and tests.

See above for more details about loading custom ZCML in a layer or test.

Helper functions
~~~~~~~~~~~~~~~~

The following helper functions are available in the ``plone.testing.zca`` module.

``stackConfigurationContext(context=None)``

    Create and return a copy of the passed-in ZCML configuration context, or a brand new context if it is ``None``.

    The purpose of this is to ensure that if a layer loads some ZCML files (using the ``zope.configuration`` API during) during its ``setUp()``, the state of the configuration registry (which includes registered directives as well as a list of already imported files, which will not be loaded again even if explicitly included) can be torn down during ``tearDown()``.

    The usual pattern is to keep the configuration context in a layer resource called ``configurationContext``.
    In ``setUp()``, you would then use::

        self['configurationContext'] = context = zca.stackConfigurationContext(self.get('configurationContext'))

        # use 'context' to load some ZCML

    In ``tearDown()``, you can then simply do::

        del self['configurationContext']

``pushGlobalRegistry(new=None)``

    Create or obtain a stack of global component registries, and push a new registry to the top of the stack.
    The net result is that ``zope.component.getGlobalSiteManager()`` and (an un-hooked) ``getSiteManager()`` will return the new registry instead of the default, module-scope one.
    From this point onwards, calls to ``provideAdapter()``, ``provideUtility()`` and other functions that modify the global registry will use the new registry.

    If ``new`` is not given, a new registry is created that has the previous global registry (site manager) as its sole base.
    This has the effect that registrations in the previous default global registry are still available, but new registrations are confined to the new registry.

    **Warning**: If you call this function, you *must* reciprocally call ``popGlobalRegistry()``.
    That is, if you "push" a registry during layer ``setUp()``, you must "pop" it during ``tearDown()``.
    If you "push" during ``testSetUp()``, you must "pop" during ``testTearDown()``.
    If the calls to push and pop are not balanced, you will leave your global registry in a mess, which is not pretty.

    Returns the new default global site manager.
    Also causes the site manager hook from ``zope.component.hooks`` to be reset, clearing any local site managers as appropriate.

``popGlobalRegistry()``

    Pop the global site registry, restoring the previous registry to be the default.

    Please heed the warning above: push and pop must be balanced.

    Returns the new default global site manager.
    Also causes the site manager hook from ``zope.component.hooks`` to be reset, clearing any local site managers as appropriate.

Zope Security
-------------

The Zope Security layers build can be found in the module ``plone.testing.security``.

If you depend on this, you can use the ``[security]`` extra when depending on ``plone.testing``.

Security checker isolation
~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.security.CHECKERS``              |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.security.Checkers``              |
+------------+--------------------------------------------------+
| Bases:     | None                                             |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer ensures that security checkers used by ``zope.security`` are isolated.
Any checkers set up in a child layer will be removed cleanly during tear-down.

Helper functions
~~~~~~~~~~~~~~~~

The security checker isolation outlined above is managed using two helper functions found in the module ``plone.testing.security``:

``pushCheckers()``

    Copy the current set of security checkers for later tear-down.

``popCheckers()``

    Restore the set of security checkers to the state of the most recent call to ``pushCheckers()``.

You *must* keep calls to ``pushCheckers()`` and ``popCheckers()`` in balance.
That usually means that if you call the former during layer setup, you should call the latter during layer tear-down.
Ditto for calls during test setup/tear-down or within tests themselves.

Zope Publisher
--------------

The Zope Publisher layers build on the Zope Component Architecture layers.
They can be found in the module ``plone.testing.publisher``.

If you depend on this, you can use the ``[publisher]`` extra when depending on ``plone.testing``.

Publisher directives
~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.publisher.PUBLISHER_DIRECTIVES`` |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.publisher.PublisherDirectives``  |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.ZCML_DIRECTIVES``            |
+------------+--------------------------------------------------+
| Resources: | None                                             |
+------------+--------------------------------------------------+

This layer extends the ``zca.ZCML_DIRECTIVES`` layer to install additional ZCML directives in the ``browser`` namespace (from ``zope.app.publisher.browser``) as well as those from ``zope.security``.
This allows browser views, browser pages and other UI components to be registered, as well as the definition of new permissions.

As with ``zca.ZCML_DIRECTIVES``, you should use the ``configurationContext`` resource when loading ZCML strings or files, and the ``stackConfigurationRegistry()`` helper to create a layer-specific version of this resource resource.
See above.

ZODB
----

The ZODB layers set up a test fixture with a persistent ZODB.
The ZODB instance uses ``DemoStorage``, so it will not interfere with any "live" data.

ZODB layers can be found in the module ``plone.testing.zodb``.
If you depend on this, you can use the ``[zodb]`` extra when depending on ``plone.testing``.

Empty ZODB sandbox
~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zodb.EMPTY_ZODB``                |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zodb.EmptyZODB``                 |
+------------+--------------------------------------------------+
| Bases:     |  None                                            |
+------------+--------------------------------------------------+
| Resources: | ``zodbRoot``                                     |
|            +--------------------------------------------------+
|            | ``zodbDB`` (test set-up only)                    |
|            +--------------------------------------------------+
|            | ``zodbConnection`` (test set-up only)            |
+------------+--------------------------------------------------+

This layer sets up a simple ZODB sandbox using ``DemoStorage``.
The ZODB root object is a simple persistent mapping, available as the resource ``zodbRoot``.
The ZODB database object is available as the resource ``zodbDB``.
The connection used in the test is available as ``zodbConnection``.

Note that the ``zodbConnection`` and ``zodbRoot`` resources are created and destroyed for each test.
You can use ``zodbDB`` (and the ``open()`` method) if you are writing a layer based on this one and need to set up a fixture during layer set up.
Don't forget to close the connection before concluding the test setup!

A new transaction is begun for each test, and rolled back (aborted) on test tear-down.
This means that so long as you don't use ``transaction.commit()`` explicitly in your code, it should be safe to add or modify items in the ZODB root.

If you want to create a test fixture with persistent data in your own layer based on ``EMPTY_ZODB``, you can use the following pattern::

    from plone.layer import Layer
    from plone.layer import zodb

    class MyLayer(Layer):
        defaultBases = (zodb.EMPTY_ZODB,)

        def setUp(self):

            import transaction
            self['zodbDB'] = db = zodb.stackDemoStorage(self.get('zodbDB'), name='MyLayer')

            conn = db.open()
            root = conn.root()

            # modify the root object here

            transaction.commit()
            conn.close()

        def tearDown(self):

            self['zodbDB'].close()
            del self['zodbDB']

This shadows the ``zodbDB`` resource with a new database that uses a new ``DemoStorage`` stacked on top of the underlying database storage.
The fixture is added to this storage and committed during layer setup.
(The base layer test set-up/tear-down will still begin and abort a new transaction for each *test*).
On layer tear-down, the database is closed and the resource popped, leaving the original ``zodbDB`` database with the original, pristine storage.

Helper functions
~~~~~~~~~~~~~~~~

One helper function is available in the ``plone.testing.zodb`` module.

``stackDemoStorage(db=None, name=None)``

Create a new ``DemoStorage`` using the storage from the passed-in database as a base.
If ``db`` is None, a brand new storage is created.

A ``name`` can be given to uniquely identify the storage.
It is optional, but it is often useful for debugging purposes to pass the name of the layer.

The usual pattern is::

    def setUp(self):
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name='MyLayer')

    def tearDown(self):
        self['zodbDB'].close()
        del self['zodbDB']

This will shadow the ``zodbDB`` resource with an isolated ``DemoStorage``, creating a new one if that resource does not already exist.
All existing data continues to be available, but new changes are written to the stacked storage.
On tear-down, the stacked database is closed and the resource removed, leaving the original data.

Zope
----

The Zope layers provide test fixtures suitable for testing Zope applications.
They set up a Zope application root, install core Zope products, and manage security.

Zope layers can be found in the module ``plone.testing.zope``.
If you depend on this, you can use the ``[zope]`` extra when depending on ``plone.testing``.

Startup
~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zope.STARTUP``                   |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zope.Startup``                   |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.LAYER_CLEANUP``              |
+------------+--------------------------------------------------+
| Resources: | ``zodbDB``                                       |
|            +--------------------------------------------------+
|            | ``configurationContext``                         |
|            +--------------------------------------------------+
|            | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

This layer sets up a Zope environment, and is a required base for all other Zope layers.
You cannot run two instances of this layer in parallel, since Zope depends on some module-global state to run, which is managed by this layer.

On set-up, the layer will configure a Zope environment with:

.. note::

    The ``STARTUP`` layer is a useful base layer for your own fixtures, but should not be used directly, since it provides no test lifecycle or transaction management.
    See the "Integration test" and "Functional" test sections below for examples of how to create your own layers.

* Debug mode enabled.

* ZEO client cache disabled.

* Some patches installed, which speed up Zope startup by disabling some superfluous aspects of Zope.

* One thread (this only really affects the ``WSGI_SERVER``, ``ZSERVER`` and ``FTP_SERVER`` layers).

* A pristine database using ``DemoStorage``, exposed as the resource ``zodbDB``.
  Zope is configured to use this database in a way that will also work if the ``zodbDB`` resource is shadowed using the pattern shown above in the description of the ``zodb.EMPTY_ZODB`` layer.

* A fake hostname and port, exposed as the ``host`` and ``port`` resource, respectively.

* A minimal set of products installed (``Products.OFSP`` and ``Products.PluginIndexes``, both required for Zope to start up).

* A stacked ZCML configuration context, exposed as the resource ``configurationContext``.
  As illustrated above, you should use the ``zca.stackConfigurationContext()`` helper to stack your own configuration context if you use this.

* A minimal set of global Zope components configured.

Note that unlike a "real" Zope site, products in the ``Products.*`` namespace are not automatically loaded, nor is any ZCML.

Integration test
~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zope.INTEGRATION_TESTING``       |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zope.IntegrationTesting``        |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zope.STARTUP``                   |
+------------+--------------------------------------------------+
| Resources: | ``app``                                          |
|            +--------------------------------------------------+
|            | ``request``                                      |
+------------+--------------------------------------------------+

This layer is intended for integration testing against the simple ``STARTUP`` fixture.
If you want to create your own layer with a more advanced, shared fixture, see "Integration and functional testing with custom fixtures" below.

For each test, it exposes the Zope application root as the resource ``app``.
This is wrapped in the request container, so you can do ``app.REQUEST`` to acquire a fake request, but the request is also available as the resource ``request``.

A new transaction is begun for each test and rolled back on test tear-down, meaning that so long as the code under test does not explicitly commit any changes, the test may modify the ZODB.

    *Hint:* If you want to set up a persistent test fixture in a layer based on this one (or ``zope.FUNCTIONAL_TESTING``), you can stack a new ``DemoStorage`` in a shadowing ``zodbDB`` resource, using the pattern described above for the ``zodb.EMPTY_ZODB`` layer.

    Once you've shadowed the ``zodbDB`` resource, you can do (e.g. in your layer's ``setUp()`` method)::

        ...
        with zope.zopeApp() as app:
            # modify the Zope application root

    The ``zopeApp()`` context manager will open a new connection to the Zope application root, accessible here as ``app``.
    Provided the code within the ``with`` block does not raise an exception, the transaction will be committed and the database closed properly upon exiting the block.

Functional testing
~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zope.FUNCTIONAL_TESTING``        |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zope.FunctionalTesting``         |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zope.STARTUP``                   |
+------------+--------------------------------------------------+
| Resources: | ``app``                                          |
|            +--------------------------------------------------+
|            | ``request``                                      |
+------------+--------------------------------------------------+

This layer is intended for functional testing against the simple ``STARTUP`` fixture.
If you want to create your own layer with a more advanced, shared fixture, see "Integration and functional testing with custom fixtures" below.

As its name implies, this layer is intended mainly for functional end-to-end testing using tools like `zope.testbrowser`_.
See also the ``Browser`` object as described under "Helper functions" below.

This layer is very similar to ``INTEGRATION_TESTING``, but is not based on it.
It sets up the same fixture and exposes the same resources.
However, instead of using a simple transaction abort to isolate the ZODB between tests, it uses a stacked ``DemoStorage`` for each test.
This is slower, but allows test code to perform and explicit commit, as will usually happen in a functional test.

Integration and functional testing with custom fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to extend the ``STARTUP`` fixture for use with integration or functional testing, you should use the following pattern:

* Create a layer class and a "fixture" base layer instance that has ``zope.STARTUP`` (or some intermediary layer, such as ``zope.WSGI_SERVER_FIXTURE``, shown below) as a base.

* Create "end user" layers by instantiating the ``zope.IntegrationTesting`` and/or ``FunctionalTesting`` classes with this new "fixture" layer as a base.

This allows the same fixture to be used regardless of the "style" of testing, minimising the amount of set-up and tear-down.
The "fixture" layers manage the fixture as part of the *layer* lifecycle.
The layer class (``IntegrationTesting`` or ``FunctionalTesting``), manages the *test* lifecycle, and the test lifecycle only.

For example::

    from plone.testing import Layer, zope, zodb

    class MyLayer(Layer):
        defaultBases = (zope.STARTUP,)

        def setUp(self):
            # Set up the fixture here
            ...

        def tearDown(self):
            # Tear down the fixture here
            ...

    MY_FIXTURE = MyLayer()

    MY_INTEGRATION_TESTING = zope.IntegrationTesting(bases=(MY_FIXTURE,), name="MyFixture:Integration")
    MY_FUNCTIONAL_TESTING = zope.FunctionalTesting(bases=(MY_FIXTURE,), name="MyFixture:Functional")

(Note that we need to give an explicit, unique name to the two layers that reuse the ``IntegrationTesting`` and ``FunctionalTesting`` classes.)

In this example, other layers could extend the "MyLayer" fixture by using ``MY_FIXTURE`` as a base.
Tests would use either ``MY_INTEGRATION_TESTING`` or ``MY_FUNCTIONAL_TESTING`` as appropriate.
However, even if both these two layers were used, the fixture in ``MY_FIXTURE`` would only be set up once.

.. note::

    If you implement the ``testSetUp()`` and ``testTearDown()`` test lifecycle methods in your "fixture" layer (e.g. in the the ``MyLayer`` class above), they will execute before the corresponding methods from ``IntegrationTesting`` and ``FunctionalTesting``.
    Hence, they cannot use those layers' resources (``app`` and ``request``).

It may be preferable, therefore, to have your own "test lifecycle" layer classes that subclass ``IntegrationTesting`` and/or ``FunctionalTesting`` and call base class methods as appropriate.
``plone.app.testing`` takes this approach, for example.

HTTP WSGI server thread (fixture only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zope.WSGI_SERVER_FIXTURE``       |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zope.WSGIServer``                |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zope.STARTUP``                   |
+------------+--------------------------------------------------+
| Resources: | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

This layer extends the ``zope.STARTUP`` layer to start the Zope HTTP WSGI server in a separate thread.
This means the test site can be accessed through a web browser, and can thus be used with tools like `Selenium`_.

.. note::

    This layer is useful as a fixture base layer only, because it does not manage the test lifecycle.
    Use the ``WSGI_SERVER`` layer if you want to execute functional tests against this fixture.

The WSGI server's hostname (normally ``localhost``) is available through the resource ``host``, whilst the port it is running on is available through the resource ``port``.

  *Hint:* Whilst the layer is set up, you can actually access the test Zope site through a web browser.
  The default URL will be ``http://localhost:55001``.

HTTP WSGI server functional testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zope.WSGI_SERVER``               |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zope.FunctionalTesting``         |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zope.WSGI_SERVER_FIXTURE``       |
+------------+--------------------------------------------------+
| Resources: |                                                  |
+------------+--------------------------------------------------+

This layer provides the functional testing lifecycle against the fixture set up by the ``zope.WSGI_SERVER_FIXTURE`` layer.

You can use this to run "live" functional tests against a basic Zope site.
You should **not** use it as a base.
Instead, create your own "fixture" layer that extends ``zope.WSGI_SERVER_FIXTURE``, and then instantiate the ``FunctionalTesting`` class with this extended fixture layer as a base, as outlined above.

Helper functions
~~~~~~~~~~~~~~~~

Several helper functions are available in the ``plone.testing.zope`` module.

``zopeApp(db=None, conn=Non, environ=None)``

    This function can be used as a context manager for any code that requires access to the Zope application root.
    By using it in a ``with`` block, the database will be opened, and the application root will be obtained and request-wrapped.
    When exiting the ``with`` block, the transaction will be committed and the database properly closed, unless an exception was raised::

        with zope.zopeApp() as app:
            # do something with app

    If you want to use a specific database or database connection, pass either the ``db`` or ``conn`` arguments.
    If the context manager opened a new connection, it will close it, but it will not close a connection passed with ``conn``.

    To set keys in the (fake) request environment, pass a dictionary of environment values as ``environ``.

    Note that ``zopeApp()`` should *not* normally be used in tests or test set-up/tear-down, because the ``INTEGRATOIN_TEST`` and ``FUNCTIONAL_TESTING`` layers both manage the application root (as the ``app`` resource) and close it for you.
    It is very useful in layer setup, however.

``installProduct(app, product, quiet=False)``

    Install a Zope 2 style product, ensuring that its ``initialize()`` function is called.
    The product name must be the full dotted name, e.g. ``plone.app.portlets`` or ``Products.CMFCore``.
    If ``quiet`` is true, duplicate registrations will be ignored silently, otherwise a message is logged.

    To get hold of the application root, passed as the ``app`` argument, you would normally use the ``zopeApp()`` context manager outlined above.

``uninstallProduct(app, product, quiet=False)``

    This is the reciprocal of ``installProduct()``, normally used during layer tear-down.
    Again, you should use ``zopeApp()`` to obtain the application root.

``login(userFolder, userName)``

    Create a new security manager that simulates being logged in as the given user.
    ``userFolder`` is an ``acl_users`` object, e.g. ``app['acl_users']`` for the root user folder.

``logout()``

    Simulate being the anonymous user by unsetting the security manager.

``setRoles(userFolder, userName, roles)``

    Set the roles of the given user in the given user folder to the given list of roles.

``makeTestRequest()``

    Create a fake Zope request.

``addRequestContainer(app, environ=None)``

    Create a fake request and wrap the given object (normally an application root) in a ``RequestContainer`` with this request.
    This makes acquisition of ``app.REQUEST`` possible.
    To initialise the request environment with non-default values, pass a dictionary as ``environ``.

    .. note::

       This method is rarely used, because both the ``zopeApp()``
       context manager and the layer set-up/tear-down for
       ``zope.INTEGRATION_TESTING`` and ``zope.FUNCTIONAL_TESTING`` will wrap the
       ``app`` object before exposing it.

``Browser(app)``

    Obtain a test browser client, for use with `zope.testbrowser`_.
    You should use this in conjunction with the ``zope.FUNCTIONAL_TESTING`` layer or a derivative.
    You must pass the app root, usually obtained from the ``app`` resource of the layer, e.g.::

        app = self.layer['app']
        browser = zope.Browser(app)

    You can then use ``browser`` as described in the `zope.testbrowser`_ documentation.

    Bear in mind that the test browser runs separately from the test fixture.
    In particular, calls to helpers such as ``login()`` or ``logout()`` do not affect the state that the test browser sees.
    If you want to set up a persistent fixture (e.g. test content), you can do so before creating the test browser, but you will need to explicitly commit your changes, with::

        import transaction
        transaction.commit()


ZServer
-------

The ZServer layers provide test fixtures suitable for testing Zope applications while using ZServer instead of a WSGI server.
They set up a Zope application root, install core Zope products, and manage security.

ZServer layers can be found in the module ``plone.testing.zserver``.
If you depend on this, you can use the ``[zope,zserver]`` extra when depending on ``plone.testing``.

Startup
~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.STARTUP``                |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.Startup``                |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zca.LAYER_CLEANUP``              |
+------------+--------------------------------------------------+
| Resources: | ``zodbDB``                                       |
|            +--------------------------------------------------+
|            | ``configurationContext``                         |
|            +--------------------------------------------------+
|            | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

This layer sets up a Zope environment for ZServer, and is a required base for all other ZServer layers.
You cannot run two instances of this layer in parallel, since Zope depends on some module-global state to run, which is managed by this layer.

On set-up, the layer will configure a Zope environment with the same options as ``zope.Startup``, see there.

Integration test
~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.INTEGRATION_TESTING``    |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.IntegrationTesting``     |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.STARTUP``                |
+------------+--------------------------------------------------+
| Resources: | ``app``                                          |
|            +--------------------------------------------------+
|            | ``request``                                      |
+------------+--------------------------------------------------+

This layer is intended for integration testing against the simple ``STARTUP`` fixture.
If you want to create your own layer with a more advanced, shared fixture, see "Integration and functional testing with custom fixtures" below.

For each test, it exposes the Zope application root as the resource ``app``.
This is wrapped in the request container, so you can do ``app.REQUEST`` to acquire a fake request, but the request is also available as the resource ``request``.

A new transaction is begun for each test and rolled back on test tear-down, meaning that so long as the code under test does not explicitly commit any changes, the test may modify the ZODB.

    *Hint:* If you want to set up a persistent test fixture in a layer based on this one (or ``zserver.FUNCTIONAL_TESTING``), you can stack a new ``DemoStorage`` in a shadowing ``zodbDB`` resource, using the pattern described above for the ``zodb.EMPTY_ZODB`` layer.

    Once you've shadowed the ``zodbDB`` resource, you can do (e.g. in your layer's ``setUp()`` method)::

        ...
        with zserver.zopeApp() as app:
            # modify the Zope application root

    The ``zserver.zopeApp()`` context manager will open a new connection to the Zope application root, accessible here as ``app``.
    Provided the code within the ``with`` block does not raise an exception, the transaction will be committed and the database closed properly upon exiting the block.

Functional testing
~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.FUNCTIONAL_TESTING``     |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.FunctionalTesting``      |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.STARTUP``                |
+------------+--------------------------------------------------+
| Resources: | ``app``                                          |
|            +--------------------------------------------------+
|            | ``request``                                      |
+------------+--------------------------------------------------+

It behaves the same as ``zope.FunctionalTesting``, see there.


Integration and functional testing with custom fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to extend the ``STARTUP`` fixture for use with integration or functional testing, you should use the following pattern:

* Create a layer class and a "fixture" base layer instance that has ``zserver.STARTUP`` (or some intermediary layer, such as ``zserver.ZSERVER_FIXTURE`` or ``zserver.FTP_SERVER_FIXTURE``, shown below) as a base.

* Create "end user" layers by instantiating the ``zserver.IntegrationTesting`` and/or ``FunctionalTesting`` classes with this new "fixture" layer as a base.

This allows the same fixture to be used regardless of the "style" of testing, minimising the amount of set-up and tear-down.
The "fixture" layers manage the fixture as part of the *layer* lifecycle.
The layer class (``IntegrationTesting`` or ``FunctionalTesting``), manages the *test* lifecycle, and the test lifecycle only.

For example::

    from plone.testing import Layer, zserver, zodb

    class MyLayer(Layer):
        defaultBases = (zserver.STARTUP,)

        def setUp(self):
            # Set up the fixture here
            ...

        def tearDown(self):
            # Tear down the fixture here
            ...

    MY_FIXTURE = MyLayer()

    MY_INTEGRATION_TESTING = zserver.IntegrationTesting(bases=(MY_FIXTURE,), name="MyFixture:Integration")
    MY_FUNCTIONAL_TESTING = zserver.FunctionalTesting(bases=(MY_FIXTURE,), name="MyFixture:Functional")

(Note that we need to give an explicit, unique name to the two layers that reuse the ``IntegrationTesting`` and ``FunctionalTesting`` classes.)

In this example, other layers could extend the "MyLayer" fixture by using ``MY_FIXTURE`` as a base.
Tests would use either ``MY_INTEGRATION_TESTING`` or ``MY_FUNCTIONAL_TESTING`` as appropriate.
However, even if both these two layers were used, the fixture in ``MY_FIXTURE`` would only be set up once.

.. note::

    If you implement the ``testSetUp()`` and ``testTearDown()`` test lifecycle methods in your "fixture" layer (e.g. in the the ``MyLayer`` class above), they will execute before the corresponding methods from ``IntegrationTesting`` and ``FunctionalTesting``.
    Hence, they cannot use those layers' resources (``app`` and ``request``).

It may be preferable, therefore, to have your own "test lifecycle" layer classes that subclass ``IntegrationTesting`` and/or ``FunctionalTesting`` and call base class methods as appropriate.
``plone.app.testing`` takes this approach, for example.


HTTP ZServer thread (fixture only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.ZSERVER_FIXTURE``        |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.ZServer``                |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.STARTUP``                |
+------------+--------------------------------------------------+
| Resources: | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

This layer extends the ``zserver.STARTUP`` layer to start the Zope HTTP server (ZServer) in a separate thread.
This means the test site can be accessed through a web browser, and can thus be used with tools like `Selenium`_.

.. note::

    This layer is useful as a fixture base layer only, because it does not manage the test lifecycle.
    Use the ``ZSERVER`` layer if you want to execute functional tests against this fixture.

The ZServer's hostname (normally ``localhost``) is available through the resource ``host``, whilst the port it is running on is available through the resource ``port``.

  *Hint:* Whilst the layer is set up, you can actually access the test Zope site through a web browser.
  The default URL will be ``http://localhost:55001``.

HTTP ZServer functional testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.ZSERVER``                |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.FunctionalTesting``      |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.ZSERVER_FIXTURE``        |
+------------+--------------------------------------------------+
| Resources: |                                                  |
+------------+--------------------------------------------------+

This layer provides the functional testing lifecycle against the fixture set up by the ``zserver.ZSERVER_FIXTURE`` layer.

You can use this to run "live" functional tests against a basic Zope site.
You should **not** use it as a base.
Instead, create your own "fixture" layer that extends ``zserver.ZSERVER_FIXTURE``, and then instantiate the ``FunctionalTesting`` class with this extended fixture layer as a base, as outlined above.


FTP server thread (fixture only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.FTP_SERVER_FIXTURE``     |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.FTPServer``              |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.STARTUP``                |
+------------+--------------------------------------------------+
| Resources: | ``host``                                         |
|            +--------------------------------------------------+
|            | ``port``                                         |
+------------+--------------------------------------------------+

This layer is the FTP server equivalent of the ``zserver.ZSERVER_FIXTURE`` layer.
It can be used to functionally test Zope FTP servers.

.. note::

    This layer is useful as a fixture base layer only, because it does not manage the test lifecycle.
    Use the ``FTP_SERVER`` layer if you want to execute functional tests against this fixture.

    *Hint:* Whilst the layer is set up, you can actually access the test Zope site through an FTP client.
    The default URL will be ``ftp://localhost:55002``.

.. warning::

    Do not run the ``FTP_SERVER`` and ``ZSERVER`` layers concurrently in the same process.

If you need both ZServer and FTPServer running together, you can subclass the ``ZServer`` layer class (like the ``FTPServer`` layer class does) and implement the ``setUpServer()`` and ``tearDownServer()`` methods to set up and close down two servers on different ports.
They will then share a main loop.

FTP server functional testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------+--------------------------------------------------+
| Layer:     | ``plone.testing.zserver.FTP_SERVER``             |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.zserver.FunctionalTesting``      |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.zserver.FTP_SERVER_FIXTURE``     |
+------------+--------------------------------------------------+
| Resources: |                                                  |
+------------+--------------------------------------------------+

This layer provides the functional testing lifecycle against the fixture set up by the ``zserver.FTP_SERVER_FIXTURE`` layer.

You can use this to run "live" functional tests against a basic Zope site.
You should **not** use it as a base.
Instead, create your own "fixture" layer that extends ``zserver.FTP_SERVER_FIXTURE``, and then instantiate the ``FunctionalTesting`` class with this extended fixture layer as a base, as outlined above.

Helper functions
~~~~~~~~~~~~~~~~

Several helper functions are available in the ``plone.testing.zserver`` module.

``zopeApp(db=None, conn=Non, environ=None)``

    This function can be used as a context manager for any code that requires access to the Zope application root.
    By using it in a ``with`` block, the database will be opened, and the application root will be obtained and request-wrapped.
    When exiting the ``with`` block, the transaction will be committed and the database properly closed, unless an exception was raised::

        with zserver.zopeApp() as app:
            # do something with app

    If you want to use a specific database or database connection, pass either the ``db`` or ``conn`` arguments.
    If the context manager opened a new connection, it will close it, but it will not close a connection passed with ``conn``.

    To set keys in the (fake) request environment, pass a dictionary of environment values as ``environ``.

    Note that ``zopeApp()`` should *not* normally be used in tests or test set-up/tear-down, because the ``INTEGRATOIN_TEST`` and ``FUNCTIONAL_TESTING`` layers both manage the application root (as the ``app`` resource) and close it for you.
    It is very useful in layer setup, however.

The other helper functions defined in ``plone.testing.zope`` can also be used in a ZServer context but together with the ZServer layers.

.. _zope.testing: https://pypi.org/project/zope.testing/
.. _zope.testbrowser: https://pypi.org/project/zope.testbrowser
.. _zope.component: https://pypi.org/project/zope.component
.. _zope.publisher: https://pypi.org/project/zope.publisher
.. _plone.app.testing: https://pypi.org/project/plone.app.testing
.. _zc.recipe.testrunner: https://pypi.org/project/zc.recipe.testrunner
.. _coverage: https://pypi.org/project/coverage
.. _Cobertura: https://wiki.jenkins.io/display/JENKINS/Cobertura+Plugin
.. _Jenkins: https://jenkins.io
.. _unittest: http://doc.python.org/library/unittest.html
.. _doctest: http://docs.python.org/dev/library/doctest.html
.. _Selenium: http://seleniumhq.org/
