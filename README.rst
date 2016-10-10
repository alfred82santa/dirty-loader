|travis-master| |coverall-master| |docs-master|

.. |travis-master| image:: https://travis-ci.org/alfred82santa/dirty-loader.svg?branch=master
    :target: https://travis-ci.org/alfred82santa/dirty-loader

.. |coverall-master| image:: https://coveralls.io/repos/alfred82santa/dirty-loader/badge.png?branch=master
    :target: https://coveralls.io/r/alfred82santa/dirty-loader?branch=master

.. |docs-master| image:: https://readthedocs.org/projects/dirty-loader/badge/?version=latest
    :target: https://readthedocs.org/projects/dirty-loader/?badge=latest
    :alt: Documentation Status

dirty-loader
============

Easy to use loader library.

---------
Changelog
---------

Version 0.2.2
-------------

- Simplified code.
- Added BaseFactory methods to load items from list or dictionaries.

Version 0.2.1
-------------

- Three types of instance definition allowed: string, structured and structure simplified.


Version 0.2.0
-------------

- Custom factories for classes.
- Default factories for logging package.

Version 0.1.0
-------------

* Some refactors.
* New function ``import_class``.


-----------
Instalation
-----------

.. code-block:: bash

    $ pip install dirty-loader

-------------
Documentation
-------------

http://dirty-loader.readthedocs.io

------------
Main loaders
------------

Loader
------

With Loader you could register sorted python modules. When you ask for a class
it will try to load it for each module until it find one.

**Example**:

.. code-block:: python

    from dirty_loader import Loader

    loader = Loader()
    loader.register_module('tests.fake.namespace1')
    loader.register_module('tests.fake.namespace2')
    loader.register_module('tests.fake.namespace3')

    klass = loader.load_class('FakeClass1')

    from tests.fake.namespace1 import FakeClass1
    assert klass == FakeClass1

    # klass is tests.fake.namespace1.FakeClass1 because it exists in first module registered.
    # Also, you could get an instance of class using factory
    obj = loader.factory('FakeClass1', var1='a', var2=2)

    # You could load classes from packages inside modules registered
    klass = loader.load_class('subnamespace.FakeClass1')
    from tests.fake.namespace3.subnamespace import FakeClass1 as SubFakeClass1
    assert klass == SubFakeClass1
    # klass is tests.fake.namespace3.subnamespace.FakeClass1 because it exists in first module registered.



LoaderReversed
--------------

It works in same way of Loader but it revers the sort when try to load a class.

**Example**:

.. code-block:: python

    from dirty_loader import LoaderReversed

    loader = LoaderReversed()
    loader.register_module('tests.fake.namespace1')
    loader.register_module('tests.fake.namespace2')

    klass = loader.load_class('FakeClass1')

    from tests.fake.namespace2 import FakeClass1
    assert klass == FakeClass1

    # klass is tests.fake.namespace2.FakeClass1 because it exists in last module registered.


LoaderNamespace
---------------

With LoaderNamespace you could register sorted namespaces. When you ask for a class
it will try to load it for each namespace until it find one. Each namespace has a python
module associated. You could use the regular Loader way to load a class or you could
specify the namespace you would like to use.

**Example**:

.. code-block:: python

    from dirty_loader import LoaderNamespace

    loader = LoaderNamespace()
    loader.register_namespace('fake1', 'tests.fake.namespace1')
    loader.register_namespace('fake2', 'tests.fake.namespace2')

    from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

    klass = loader.load_class('FakeClass1')

    from tests.fake.namespace1 import FakeClass1
    assert klass == FakeClass1
    # klass is tests.fake.namespace1.FakeClass1 because it exists in last module registered.

    # Also, you could get a class from specific namespace

    klass = loader.load_class('FakeClass1', namespace='fake2)

    from tests.fake.namespace2 import FakeClass1
    assert klass == FakeClass1
    # klass is tests.fake.namespace2.FakeClass1 because you specified it.

    # Namespace could be specified in string class, too
    klass = loader.load_class('fake2:FakeClass1')

    assert klass == FakeClass1
    # klass is tests.fake.namespace2.FakeClass1 because you specified it.


LoaderNamespaceReversed
-----------------------

It works in same way of LoaderNamespace but it revers the sort when try to load a class.


LoaderCached
------------

A version of Loader with cache.


LoaderReversedCached
--------------------

A version of LoaderReversed with cache.


LoaderNamespaceCached
---------------------

A version of LoaderNamespace with cache.


LoaderNamespaceReversedCached
-----------------------------

A version of LoaderNamespaceReversed with cache.
