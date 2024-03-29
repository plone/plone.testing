Zope Object Database layers
---------------------------

The ZODB layers are found in the module ``plone.testing.zodb``:::

    >>> from plone.testing import zodb

For testing, we need a testrunner:::

    >>> from zope.testrunner import runner

Empty ZODB layer
~~~~~~~~~~~~~~~~

The ``EMPTY_ZODB`` layer is used to set up an empty ZODB using ``DemoStorage``.

The storage and database are set up as layer fixtures.
The database is exposed as the resource ``zodbDB``.

A connection is opened for each test and exposed as ``zodbConnection``.
The ZODB root is also exposed, as ``zodbRoot``.
A new transaction is begun for each test.
On test tear-down, the transaction is aborted, the connection is closed, and the two test-specific resources are deleted.

The layer has no bases.::

    >>> "%s.%s" % (zodb.EMPTY_ZODB.__module__, zodb.EMPTY_ZODB.__name__,)
    'plone.testing.zodb.EmptyZODB'

    >>> zodb.EMPTY_ZODB.__bases__
    ()

Layer setup creates the database, but not a connection.::

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, zodb.EMPTY_ZODB, setupLayers)
    Set up plone.testing.zodb.EmptyZODB in ... seconds.

    >>> db = zodb.EMPTY_ZODB['zodbDB']
    >>> db.storage
    EmptyZODB

    >>> zodb.EMPTY_ZODB.get('zodbConnection', None) is None
    True
    >>> zodb.EMPTY_ZODB.get('zodbRoot', None) is None
    True

Let's now simulate a test.::

    >>> zodb.EMPTY_ZODB.testSetUp()

The test would then execute. It may use the ZODB root.::

    >>> zodb.EMPTY_ZODB['zodbConnection']
    <...Connection...at ...>

    >>> zodb.EMPTY_ZODB['zodbRoot']
    {}

    >>> zodb.EMPTY_ZODB['zodbRoot']['foo'] = 'bar'

On test tear-down, the transaction is aborted and the connection is closed.::

    >>> zodb.EMPTY_ZODB.testTearDown()

    >>> zodb.EMPTY_ZODB.get('zodbConnection', None) is None
    True

    >>> zodb.EMPTY_ZODB.get('zodbRoot', None) is None
    True

The transaction has been rolled back.::

    >>> conn = zodb.EMPTY_ZODB['zodbDB'].open()
    >>> conn.root()
    {}
    >>> conn.close()

Layer tear-down closes and deletes the database.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.testing.zodb.EmptyZODB in ... seconds.

    >>> zodb.EMPTY_ZODB.get('zodbDB', None) is None
    True

Extending the ZODB layer
~~~~~~~~~~~~~~~~~~~~~~~~

When creating a test fixture, it is often desirable to add some initial data to the database.
If you want to do that once on layer setup, you can create your own layer class based on ``EmptyZODB`` and override its ``createStorage()`` and/or ``createDatabase()`` methods to return a pre-populated database.::

    >>> import transaction
    >>> from ZODB.DemoStorage import DemoStorage
    >>> from ZODB.DB import DB

    >>> class PopulatedZODB(zodb.EmptyZODB):
    ...
    ...     def createStorage(self):
    ...         return DemoStorage("My storage")
    ...
    ...     def createDatabase(self, storage):
    ...         db = DB(storage)
    ...         conn = db.open()
    ...
    ...         conn.root()['someData'] = 'a string'
    ...
    ...         transaction.commit()
    ...         conn.close()
    ...
    ...         return db

    >>> POPULATED_ZODB = PopulatedZODB()

We'll use this new layer in a similar manner to the test above, showing that the data is there for each test, but that other changes are rolled back.::

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, POPULATED_ZODB, setupLayers)
    Set up ...PopulatedZODB in ... seconds.

    >>> db = POPULATED_ZODB['zodbDB']
    >>> db.storage
    My storage

    >>> POPULATED_ZODB.get('zodbConnection', None) is None
    True
    >>> POPULATED_ZODB.get('zodbRoot', None) is None
    True

Let's now simulate a test.::

    >>> POPULATED_ZODB.testSetUp()

The test would then execute. It may use the ZODB root.::

    >>> POPULATED_ZODB['zodbConnection']
    <...Connection...at ...>

    >>> POPULATED_ZODB['zodbRoot']
    {'someData': 'a string'}

    >>> POPULATED_ZODB['zodbRoot']['foo'] = 'bar'

On test tear-down, the transaction is aborted and the connection is closed.::

    >>> POPULATED_ZODB.testTearDown()

    >>> POPULATED_ZODB.get('zodbConnection', None) is None
    True

    >>> POPULATED_ZODB.get('zodbRoot', None) is None
    True

The transaction has been rolled back.::

    >>> conn = POPULATED_ZODB['zodbDB'].open()
    >>> conn.root()
    {'someData': 'a string'}
    >>> conn.close()

Layer tear-down closes and deletes the database.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down ...PopulatedZODB in ... seconds.

    >>> POPULATED_ZODB.get('zodbDB', None) is None
    True

Stacking ``DemoStorage`` storages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The example above shows how to create a simple test fixture with a custom database.
It is sometimes useful to be able to stack these fixtures, so that a base layer sets up some data for one set of tests, and a child layer extends this, temporarily, with more data.

This can be achieved using layer bases and resource shadowing, combined with ZODB's stackable DemoStorage.
There is even a helper function available:::

    >>> from plone.testing import Layer
    >>> from plone.testing import zodb
    >>> import transaction

    >>> class ExpandedZODB(Layer):
    ...     defaultBases = (POPULATED_ZODB,)
    ...
    ...     def setUp(self):
    ...         # Get the database from the base layer
    ...
    ...         self['zodbDB'] = db = zodb.stackDemoStorage(self.get('zodbDB'), name='ExpandedZODB')
    ...
    ...         conn = db.open()
    ...         conn.root()['additionalData'] = "Some new data"
    ...         transaction.commit()
    ...         conn.close()
    ...
    ...     def tearDown(self):
    ...         # Close the database and delete the shadowed copy
    ...
    ...         self['zodbDB'].close()
    ...         del self['zodbDB']

    >>> EXPANDED_ZODB = ExpandedZODB()

Notice that we are using plain ``Layer`` as a base class here.
We obtain the underlying database from our bases using the resource manager, and then create a shadow copy using a stacked storage.
Stacked storages contain the data of the original storage, but save changes in a separate (and, in this case, temporary) storage.

Let's simulate a test run again to show how this would work.::

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, EXPANDED_ZODB, setupLayers)
    Set up ...PopulatedZODB in ... seconds.
    Set up ...ExpandedZODB in ... seconds.

    >>> db = EXPANDED_ZODB['zodbDB']
    >>> db.storage
    ExpandedZODB

    >>> EXPANDED_ZODB.get('zodbConnection', None) is None
    True
    >>> EXPANDED_ZODB.get('zodbRoot', None) is None
    True

Let's now simulate a test.::

    >>> POPULATED_ZODB.testSetUp()
    >>> EXPANDED_ZODB.testSetUp()

The test would then execute. It may use the ZODB root.::

    >>> EXPANDED_ZODB['zodbConnection']
    <...Connection...at ...>

    >>> EXPANDED_ZODB['zodbRoot'] == dict(someData='a string', additionalData='Some new data')
    True

    >>> POPULATED_ZODB['zodbRoot']['foo'] = 'bar'

On test tear-down, the transaction is aborted and the connection is closed.::

    >>> EXPANDED_ZODB.testTearDown()
    >>> POPULATED_ZODB.testTearDown()

    >>> EXPANDED_ZODB.get('zodbConnection', None) is None
    True

    >>> EXPANDED_ZODB.get('zodbRoot', None) is None
    True

The transaction has been rolled back.::

    >>> conn = EXPANDED_ZODB['zodbDB'].open()
    >>> conn.root() == dict(someData='a string', additionalData='Some new data')
    True
    >>> conn.close()

We'll now tear down the expanded layer and inspect the database again.::

    >>> runner.tear_down_unneeded(options, [POPULATED_ZODB], setupLayers, [])
    Tear down ...ExpandedZODB in ... seconds.

    >>> conn = EXPANDED_ZODB['zodbDB'].open()
    >>> conn.root()
    {'someData': 'a string'}

    >>> conn.close()

Finally, we'll tear down the rest of the layers.::

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down ...PopulatedZODB in ... seconds.

    >>> EXPANDED_ZODB.get('zodbDB', None) is None
    True
    >>> POPULATED_ZODB.get('zodbDB', None) is None
    True
