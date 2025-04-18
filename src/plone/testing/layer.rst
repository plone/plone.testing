Layer base class
----------------

This package provides a layer base class which can be used by the test runner.
It is available as a convenience import from the package root.::

    >>> from plone.testing import Layer

A layer may be instantiated directly, though in this case the ``name`` argument is required (see below).::

    >>> NULL_LAYER = Layer(name="Null layer")

This is not very useful on its own.
It has an empty list of bases, and each of the layer lifecycle methods does nothing.::

    >>> NULL_LAYER.__bases__
    ()
    >>> NULL_LAYER.__name__
    'Null layer'
    >>> NULL_LAYER.__module__
    'plone.testing.layer'

    >>> NULL_LAYER.setUp()
    >>> NULL_LAYER.testSetUp()
    >>> NULL_LAYER.tearDown()
    >>> NULL_LAYER.testTearDown()

Just about the only reason to use this directly (i.e. not as a base class) is to group together other layers.::

    >>> SIMPLE_LAYER = Layer(bases=(NULL_LAYER,), name="Simple layer", module='plone.testing.tests')

Here, we've also set the module name directly.
The default for all layers is to take the module name from the stack frame where the layer was instantiated.
In doctests, that doesn't work, though, so we fall back on the module name of the layer class.
The two are often the same, of course.

This layer now has the bases, name and module we set:::

    >>> SIMPLE_LAYER.__bases__
    (<Layer 'plone.testing.layer.Null layer'>,)

    >>> SIMPLE_LAYER.__name__
    'Simple layer'

    >>> SIMPLE_LAYER.__module__
    'plone.testing.tests'

The ``name`` argument is required when using ``Layer`` directly (but not when using a subclass):::

    >>> Layer((SIMPLE_LAYER,))
    Traceback (most recent call last):
    ...
    ValueError: The `name` argument is required when instantiating `Layer` directly

    >>> class NullLayer(Layer):
    ...     pass
    >>> NullLayer()
    <Layer 'builtins.NullLayer'>

Using ``Layer`` as a base class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The usual pattern is to use ``Layer`` as a base class for a custom layer.
This can then override the lifecycle methods as appropriate, as well as set a default list of bases.::

    >>> class BaseLayer(Layer):
    ...
    ...     def setUp(self):
    ...         print("Setting up base layer")
    ...
    ...     def tearDown(self):
    ...         print("Tearing down base layer")

    >>> BASE_LAYER = BaseLayer()

The layer name and module are taken from the class.::

    >>> BASE_LAYER.__bases__
    ()
    >>> BASE_LAYER.__name__
    'BaseLayer'
    >>> BASE_LAYER.__module__
    'builtins'

We can now create a new layer that has this one as a base.
We can do this in the instance constructor, as shown above, but the most common pattern is to set the default bases in the class body, using the variable ``defaultBases``.

We'll also set the default name explicitly here by passing a name to the the super-constructor.
This is mostly cosmetic, but may be desirable if the class name would be misleading in the test runner output.::

    >>> class ChildLayer(Layer):
    ...     defaultBases = (BASE_LAYER,)
    ...
    ...     def __init__(self, bases=None, name='Child layer', module=None):
    ...         super(ChildLayer, self).__init__(bases, name, module)
    ...
    ...     def setUp(self):
    ...         print("Setting up child layer")
    ...
    ...     def tearDown(self):
    ...         print("Tearing down child layer")

    >>> CHILD_LAYER = ChildLayer()

Notice how the bases have now been set using the value in ``defaultBases``.::

    >>> CHILD_LAYER.__bases__
    (<Layer 'builtins.BaseLayer'>,)
    >>> CHILD_LAYER.__name__
    'Child layer'
    >>> CHILD_LAYER.__module__
    'builtins'

Overriding the default list of bases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can override the list of bases on a per-instance basis.
This may be dangerous, i.e.
the layer is likely to expect that its bases are set up.
Sometimes, it may be useful to inject a new base, however, especially when reusing layers from other packages.

The new list of bases is passed to the constructor.
When creating a second instance of a layer (most layers are global singletons created only once), it's useful to give the new instance a unique name, too.::

    >>> NEW_CHILD_LAYER = ChildLayer(bases=(SIMPLE_LAYER, BASE_LAYER,), name='New child')

    >>> NEW_CHILD_LAYER.__bases__
    (<Layer 'plone.testing.tests.Simple layer'>, <Layer 'builtins.BaseLayer'>)
    >>> NEW_CHILD_LAYER.__name__
    'New child'
    >>> NEW_CHILD_LAYER.__module__
    'builtins'

Inconsistent bases
~~~~~~~~~~~~~~~~~~

Layer bases are maintained in an order that is semantically equivalent to the "method resolution order" Python maintains for base classes.
We can get this from the ``baseResolutionOrder`` attribute:::

    >>> CHILD_LAYER.baseResolutionOrder
    (<Layer 'builtins.Child layer'>, <Layer 'builtins.BaseLayer'>)

    >>> NEW_CHILD_LAYER.baseResolutionOrder
    (<Layer 'builtins.New child'>, <Layer 'plone.testing.tests.Simple layer'>,
     <Layer 'plone.testing.layer.Null layer'>,
     <Layer 'builtins.BaseLayer'>)

As with Python classes, it is possible to construct an invalid set of bases.
In this case, layer instantiation will fail.::

    >>> INCONSISTENT_BASE1 = Layer(name="Inconsistent 1")
    >>> INCONSISTENT_BASE2 = Layer((INCONSISTENT_BASE1,), name="Inconsistent 1")
    >>> INCONSISTENT_BASE3 = Layer((INCONSISTENT_BASE1, INCONSISTENT_BASE2,), name="Inconsistent 1")
    Traceback (most recent call last):
    ...
    TypeError: Inconsistent layer hierarchy!

Using the resource manager
~~~~~~~~~~~~~~~~~~~~~~~~~~

Layers are also resource managers.
Resources can be set, retrieved and deleted using dictionary syntax.
Resources in base layers are available in child layers.
When an item is set on a child layer, it shadows any items with the same key in any base layer (until it is deleted), but the original item still exists.

Let's create a somewhat complex hierarchy of layers that all set resources under a key ``'foo'`` in their ``setUp()`` methods.::

    >>> class Layer1(Layer):
    ...     def setUp(self):
    ...         self['foo'] = 1
    ...     def tearDown(self):
    ...         del self['foo']
    >>> LAYER1 = Layer1()

    >>> class Layer2(Layer):
    ...     defaultBases = (LAYER1,)
    ...     def setUp(self):
    ...         self['foo'] = 2
    ...     def tearDown(self):
    ...         del self['foo']
    >>> LAYER2 = Layer2()

    >>> class Layer3(Layer):
    ...     def setUp(self):
    ...         self['foo'] = 3
    ...     def tearDown(self):
    ...         del self['foo']
    >>> LAYER3 = Layer3()

    >>> class Layer4(Layer):
    ...     defaultBases = (LAYER2, LAYER3,)
    ...     def setUp(self):
    ...         self['foo'] = 4
    ...     def tearDown(self):
    ...         del self['foo']
    >>> LAYER4 = Layer4()

    **Important:** Resources that are created in ``setUp()`` must be deleted in ``tearDown()``.
    Similarly, resources created in ``testSetUp()`` must be deleted in ``testTearDown()``.
    This ensures resources are properly stacked and do not leak between layers.

If a test was using ``LAYER4``, the test runner would call each setup step in turn, starting with the "deepest" layer.
We'll simulate that here, so that each of the resources is created.::

    >>> LAYER1.setUp()
    >>> LAYER2.setUp()
    >>> LAYER3.setUp()
    >>> LAYER4.setUp()

The layers are ordered in a known "resource resolution order", which is used to determine in which order the layers shadow one another.
This is based on the same algorithm as Python's method resolution order.::

    >>> LAYER4.baseResolutionOrder
    (<Layer 'builtins.Layer4'>,
     <Layer 'builtins.Layer2'>,
     <Layer 'builtins.Layer1'>,
     <Layer 'builtins.Layer3'>)

When fetching and item from a layer, it will be obtained according to the resource resolution order.::

    >>> LAYER4['foo']
    4

This is not terribly interesting, since ``LAYER4`` has the resource ``'foo'`` set directly.
Let's tear down the layer (which deletes the resource) and see what happens.::

    >>> LAYER4.tearDown()
    >>> LAYER4['foo']
    2

We can continue up the chain:::

    >>> LAYER2.tearDown()
    >>> LAYER4['foo']
    1

    >>> LAYER1.tearDown()
    >>> LAYER4['foo']
    3

Once we've deleted the last key, we'll get a ``KeyError``:::

    >>> LAYER3.tearDown()
    >>> LAYER4['foo']
    Traceback (most recent call last):
    ...
    KeyError: 'foo'

To guard against this, we can use the ``get()`` method.::

    >>> LAYER4.get('foo', -1)
    -1

We can also test with 'in':::

    >>> 'foo' in LAYER4
    False

To illustrate that this indeed works, let's set the resource back on one of the bases.::

    >>> LAYER3['foo'] = 10
    >>> LAYER4.get('foo', -1)
    10

Let's now consider a special case: a base layer sets up a resource in layer setup, and uses it in test setup.
A child layer then shadows this resource in its own layer setup method.
In this case, we want the base layer's ``testSetUp()`` to use the shadowed version that the child provided.

(This is similar to how instance variables work: a base class may set an attribute on ``self`` and use it in a method.
If a subclass then sets the same attribute to a different value and the base class method is called on an instance of the subclass, the base class attribute is used).

    *Hint:* If you definitely need to access the "original" resource in your ``testSetUp()``/``testTearDown()`` methods, you can store a reference to the resource as a layer instance variable::

        self.someResource = self['someResource'] = SomeResource()

    ``self.someResource`` will now be the exact resource created here, whereas ``self['someResource']`` will retain the layer shadowing semantics.
    In most cases, you probably *don't* want to do this, allowing child layers to supply overridden versions of resources as appropriate.

First, we'll create some base layers.
We want to demonstrate having two "branches" of bases that both happen to define the same resource.::

    >>> class ResourceBaseLayer1(Layer):
    ...     def setUp(self):
    ...         self['resource'] = "Base 1"
    ...     def testSetUp(self):
    ...         print(self['resource'])
    ...     def tearDown(self):
    ...         del self['resource']

    >>> RESOURCE_BASE_LAYER1 = ResourceBaseLayer1()

    >>> class ResourceBaseLayer2(Layer):
    ...     defaultBases = (RESOURCE_BASE_LAYER1,)
    ...     def testSetUp(self):
    ...         print(self['resource'])

    >>> RESOURCE_BASE_LAYER2 = ResourceBaseLayer2()

    >>> class ResourceBaseLayer3(Layer):
    ...     def setUp(self):
    ...         self['resource'] = "Base 3"
    ...     def testSetUp(self):
    ...         print(self['resource'])
    ...     def tearDown(self):
    ...         del self['resource']

    >>> RESOURCE_BASE_LAYER3 = ResourceBaseLayer3()

We'll then create the child layer that overrides this resource.::

    >>> class ResourceChildLayer(Layer):
    ...     defaultBases = (RESOURCE_BASE_LAYER2, RESOURCE_BASE_LAYER3)
    ...     def setUp(self):
    ...         self['resource'] = "Child"
    ...     def testSetUp(self):
    ...         print(self['resource'])
    ...     def tearDown(self):
    ...         del self['resource']

    >>> RESOURCE_CHILD_LAYER = ResourceChildLayer()

We'll first set up the base layers on their own and simulate two tests.

A test with RESOURCE_BASE_LAYER1 only would look like this:::

    >>> RESOURCE_BASE_LAYER1.setUp()

    >>> RESOURCE_BASE_LAYER1.testSetUp()
    Base 1
    >>> RESOURCE_BASE_LAYER1.testTearDown()

    >>> RESOURCE_BASE_LAYER1.tearDown()

A test with RESOURCE_BASE_LAYER2 would look like this:::

    >>> RESOURCE_BASE_LAYER1.setUp()
    >>> RESOURCE_BASE_LAYER2.setUp()

    >>> RESOURCE_BASE_LAYER1.testSetUp()
    Base 1
    >>> RESOURCE_BASE_LAYER2.testSetUp()
    Base 1
    >>> RESOURCE_BASE_LAYER2.testTearDown()
    >>> RESOURCE_BASE_LAYER1.testTearDown()

    >>> RESOURCE_BASE_LAYER2.tearDown()
    >>> RESOURCE_BASE_LAYER1.tearDown()

A test with RESOURCE_BASE_LAYER3 only would look like this:::

    >>> RESOURCE_BASE_LAYER3.setUp()

    >>> RESOURCE_BASE_LAYER3.testSetUp()
    Base 3
    >>> RESOURCE_BASE_LAYER3.testTearDown()

    >>> RESOURCE_BASE_LAYER3.tearDown()

Now let's set up the child layer and simulate another test.
We should now be using the shadowed resource.::

    >>> RESOURCE_BASE_LAYER1.setUp()
    >>> RESOURCE_BASE_LAYER2.setUp()
    >>> RESOURCE_BASE_LAYER3.setUp()
    >>> RESOURCE_CHILD_LAYER.setUp()

    >>> RESOURCE_BASE_LAYER1.testSetUp()
    Child
    >>> RESOURCE_BASE_LAYER2.testSetUp()
    Child
    >>> RESOURCE_BASE_LAYER3.testSetUp()
    Child
    >>> RESOURCE_CHILD_LAYER.testSetUp()
    Child

    >>> RESOURCE_CHILD_LAYER.testTearDown()
    >>> RESOURCE_BASE_LAYER3.testTearDown()
    >>> RESOURCE_BASE_LAYER2.testTearDown()
    >>> RESOURCE_BASE_LAYER1.testTearDown()

Finally, we'll tear down the child layer again and simulate another test.
we should have the original resources back.
Note that the first and third layers no longer share a resource, since they don't have a common ancestor.::

    >>> RESOURCE_CHILD_LAYER.tearDown()

    >>> RESOURCE_BASE_LAYER1.testSetUp()
    Base 1
    >>> RESOURCE_BASE_LAYER2.testSetUp()
    Base 1
    >>> RESOURCE_BASE_LAYER2.testTearDown()
    >>> RESOURCE_BASE_LAYER1.testTearDown()

    >>> RESOURCE_BASE_LAYER3.testSetUp()
    Base 3
    >>> RESOURCE_BASE_LAYER3.testTearDown()

Finally, we'll tear down the remaining layers..::

    >>> RESOURCE_BASE_LAYER3.tearDown()
    >>> RESOURCE_BASE_LAYER2.tearDown()
    >>> RESOURCE_BASE_LAYER1.tearDown()

Asymmetric deletion
+++++++++++++++++++

It is an error to create or shadow a resource in a set-up lifecycle method and not delete it again in the tear-down.
It is also an error to delete a resource that was not explicitly created.
These two layers break those roles:::

    >>> class BadLayer1(Layer):
    ...     def setUp(self):
    ...         pass
    ...     def tearDown(self):
    ...         del self['foo']
    >>> BAD_LAYER1 = BadLayer1()

    >>> class BadLayer2(Layer):
    ...     defaultBases = (BAD_LAYER1,)
    ...     def setUp(self):
    ...         self['foo'] = 1
    ...         self['bar'] = 2
    >>> BAD_LAYER2 = BadLayer2()

Let's simulate a test that uses ``BAD_LAYER2``:::

    >>> BAD_LAYER1.setUp()
    >>> BAD_LAYER2.setUp()

    >>> BAD_LAYER1.testSetUp()
    >>> BAD_LAYER2.testSetUp()

    >>> BAD_LAYER2.testTearDown()
    >>> BAD_LAYER1.testTearDown()

    >>> BAD_LAYER2.tearDown()
    >>> BAD_LAYER1.tearDown()
    Traceback (most recent call last):
    ...
    KeyError: 'foo'

Here, we've got an error in the base layer.
This is because the resource is actually associated with the layer that first created it, in this case ``BASE_LAYER2``.
This one remains intact and orphaned:::

    >>> 'foo' in BAD_LAYER2._resources
    True
    >>> 'bar' in BAD_LAYER2._resources
    True

Doctest layer helper
~~~~~~~~~~~~~~~~~~~~

The ``doctest`` module is not aware of ``zope.testing``'s layers concept.
Therefore, the syntax for creating a doctest with a layer and adding it to a test suite is somewhat contrived: the test suite has to be created first, and then the layer attribute set on it:::

    >>> class DoctestLayer(Layer):
    ...     pass
    >>> DOCTEST_LAYER = DoctestLayer()

    >>> import unittest
    >>> import doctest

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     layerDoctest = doctest.DocFileSuite('layer.rst', package='plone.testing')
    ...     layerDoctest.layer = DOCTEST_LAYER
    ...     suite.addTest(layerDoctest)
    ...     return suite

    >>> suite = test_suite()
    >>> tests = list(suite)
    >>> len(tests)
    1
    >>> tests[0].layer is DOCTEST_LAYER
    True


To make this a little easier - especially when setting up multiple tests - a helper function called ``layered`` is provided:::

    >>> from plone.testing import layered

    >>> def test_suite():
    ...     suite = unittest.TestSuite()
    ...     suite.addTests([
    ...         layered(doctest.DocFileSuite('layer.rst', package='plone.testing'), layer=DOCTEST_LAYER),
    ...         # repeat with more suites if necessary
    ...     ])
    ...     return suite

This does the same as the sample above.::

    >>> suite = test_suite()
    >>> tests = list(suite)
    >>> len(tests)
    1
    >>> tests[0].layer is DOCTEST_LAYER
    True

In addition, a 'layer' glob is added to each test in the suite.
This allows the test to access layer resources.::

    >>> len(list(tests[0]))
    1
    >>> list(tests[0])[0]._dt_test.globs['layer'] is DOCTEST_LAYER
    True
