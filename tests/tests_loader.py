from collections import OrderedDict
from unittest.case import TestCase
from dirty_loader import Loader, NoRegisteredError, AlreadyRegisteredError, LoaderReversed, LoaderNamespace, \
    LoaderNamespaceReversed, LoaderCached, LoaderReversedCached, LoaderNamespaceReversedCached, LoaderNamespaceCached

__author__ = 'alfred'


class LoaderTest(TestCase):

    def setUp(self):
        self.loader = Loader()

    def test_register_module(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')

        self.assertEqual(self.loader.get_registered_modules(), ['tests.fake.namespace1',
                                                                'tests.fake.namespace2'])

    def test_register_indexed_module(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)

        self.assertEqual(self.loader.get_registered_modules(), ['tests.fake.namespace2',
                                                                'tests.fake.namespace1'])

    def test_load_class_1(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')
        self.loader.register_module('tests.fake.namespace3')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3
        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

        klass = self.loader.load_class('subnamespace.FakeClass4')
        from tests.fake.namespace3.subnamespace import FakeClass4
        self.assertEquals(klass, FakeClass4)

        klass = self.loader.load_class('subsubnamespace.subnamespace.FakeClass4')
        from tests.fake.namespace3.subsubnamespace.subnamespace import FakeClass4 as SubFakeClass4
        self.assertEquals(klass, SubFakeClass4)

    def test_load_class_2(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)

        from tests.fake.namespace1 import FakeClass3
        from tests.fake.namespace2 import FakeClass1, FakeClass2

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_unregister(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)

        self.loader.unregister_module('tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_unregister_fail(self):
        with self.assertRaises(NoRegisteredError):
            self.loader.unregister_module('tests.fake.namespace2')

    def test_register_fail(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)
        with self.assertRaises(AlreadyRegisteredError):
            self.loader.register_module('tests.fake.namespace1')

    def test_load_fail(self):
        self.loader.register_module('tests.fake.namespace2')
        with self.assertRaises(ImportError):
            self.loader.load_class('FakeClass3')

    def test_factory(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)

        from tests.fake.namespace1 import FakeClass3
        from tests.fake.namespace2 import FakeClass1, FakeClass2

        obj = self.loader.factory('FakeClass1', var1='a', var2=2)
        self.assertIsInstance(obj, FakeClass1)
        self.assertEquals(obj.var1, 'a')
        self.assertEquals(obj.var2, 2)

        obj = self.loader.factory('FakeClass2')
        self.assertIsInstance(obj, FakeClass2)
        self.assertIsNone(obj.var1)
        self.assertIsNone(obj.var2)

        obj = self.loader.factory('FakeClass3', var1='a', var2=2)
        self.assertIsInstance(obj, FakeClass3)
        self.assertEquals(obj.var1, 'a')
        self.assertEquals(obj.var2, 2)


class LoaderReversedTest(TestCase):

    def setUp(self):
        self.loader = LoaderReversed()

    def test_load_class_1(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass3
        from tests.fake.namespace2 import FakeClass1, FakeClass2

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_load_class_2(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2', idx=0)

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)


class LoaderCachedTest(LoaderTest):

    def setUp(self):
        self.loader = LoaderCached()

    def test_load_class_cached(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass1

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1})

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1})

    def test_invalidate_cache(self):
        self.loader.register_module('tests.fake.namespace1')

        from tests.fake.namespace1 import FakeClass1

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1})

        self.loader.register_module('tests.fake.namespace2')

        self.assertEquals(self.loader._cache, {})


class LoaderReversedCachedTest(LoaderReversedTest):

    def setUp(self):
        self.loader = LoaderReversedCached()


class LoaderNamespaceTest(TestCase):

    def setUp(self):
        self.loader = LoaderNamespace()

    def test_register_module(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')

        self.assertEqual(list(self.loader.get_registered_modules()), ['tests.fake.namespace1',
                                                                      'tests.fake.namespace2'])

    def test_register_namespace(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        self.assertEqual(list(self.loader.get_registered_modules()), ['tests.fake.namespace1',
                                                                      'tests.fake.namespace2'])

        self.assertEqual(self.loader.get_registered_namespaces(), OrderedDict([('fake1', 'tests.fake.namespace1'),
                                                                               ('fake2', 'tests.fake.namespace2')]))

    def test_load_class_1(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        self.loader.register_namespace('fake3', 'tests.fake.namespace3')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

        klass = self.loader.load_class('subnamespace.FakeClass4')
        from tests.fake.namespace3.subnamespace import FakeClass4

        self.assertEquals(klass, FakeClass4)

        klass = self.loader.load_class('fake3:subsubnamespace.subnamespace.FakeClass4')
        from tests.fake.namespace3.subsubnamespace.subnamespace import FakeClass4 as SubFakeClass4

        self.assertEquals(klass, SubFakeClass4)

    def test_load_class_2(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass3
        from tests.fake.namespace2 import FakeClass1, FakeClass2

        klass = self.loader.load_class('fake2:FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2', namespace='fake2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_unregister_module(self):
        self.loader.register_module('tests.fake.namespace2')
        self.loader.register_module('tests.fake.namespace1')

        self.loader.unregister_module('tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_unregister_namespace(self):
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')

        self.loader.unregister_namespace('fake2')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_unregister_module_fail(self):
        with self.assertRaises(NoRegisteredError):
            self.loader.unregister_module('tests.fake.namespace2')

    def test_unregister_namespace_fail(self):
        with self.assertRaises(NoRegisteredError):
            self.loader.unregister_namespace('fake2')

    def test_register_module_fail(self):
        self.loader.register_module('tests.fake.namespace1')
        self.loader.register_module('tests.fake.namespace2')
        with self.assertRaises(AlreadyRegisteredError):
            self.loader.register_module('tests.fake.namespace1')

    def test_register_namespace_fail(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        with self.assertRaises(AlreadyRegisteredError):
            self.loader.register_namespace('fake1', 'tests.fake.namespace1')

    def test_load_fail_1(self):
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        with self.assertRaises(ImportError):
            self.loader.load_class('FakeClass3')

    def test_load_fail_2(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        with self.assertRaises(ImportError):
            self.loader.load_class('fake2:FakeClass3')

    def test_load_fail_3(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        with self.assertRaises(NoRegisteredError):
            self.loader.load_class('fake3:FakeClass3')

    def test_factory(self):
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')

        from tests.fake.namespace1 import FakeClass2, FakeClass3
        from tests.fake.namespace2 import FakeClass1

        obj = self.loader.factory('FakeClass1', var1='a', var2=2)
        self.assertIsInstance(obj, FakeClass1)
        self.assertEquals(obj.var1, 'a')
        self.assertEquals(obj.var2, 2)

        obj = self.loader.factory('fake1:FakeClass2')
        self.assertIsInstance(obj, FakeClass2)
        self.assertIsNone(obj.var1)
        self.assertIsNone(obj.var2)

        obj = self.loader.factory('FakeClass3', var1='a', var2=2)
        self.assertIsInstance(obj, FakeClass3)
        self.assertEquals(obj.var1, 'a')
        self.assertEquals(obj.var2, 2)


class LoaderNamespaceReversedTest(TestCase):

    def setUp(self):
        self.loader = LoaderNamespaceReversed()

    def test_load_class_1(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass3
        from tests.fake.namespace2 import FakeClass1, FakeClass2

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)

    def test_load_class_2(self):
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')

        from tests.fake.namespace1 import FakeClass1, FakeClass2, FakeClass3

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)

        klass = self.loader.load_class('FakeClass2')
        self.assertEquals(klass, FakeClass2)

        klass = self.loader.load_class('FakeClass3')
        self.assertEquals(klass, FakeClass3)


class LoaderNamespaceCachedTest(LoaderNamespaceTest):

    def setUp(self):
        self.loader = LoaderNamespaceCached()

    def test_load_class_cached(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass1

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1})

        klass = self.loader.load_class('fake1:FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1,
                                               'fake1:FakeClass1': FakeClass1})

    def test_load_class_no_cached(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')
        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        from tests.fake.namespace1 import FakeClass1

        klass = self.loader.load_class('FakeClass1', namespace='fake1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {})

    def test_invalidate_cache(self):
        self.loader.register_namespace('fake1', 'tests.fake.namespace1')

        from tests.fake.namespace1 import FakeClass1

        klass = self.loader.load_class('FakeClass1')
        self.assertEquals(klass, FakeClass1)
        self.assertEquals(self.loader._cache, {'FakeClass1': FakeClass1})

        self.loader.register_namespace('fake2', 'tests.fake.namespace2')

        self.assertEquals(self.loader._cache, {})


class LoaderNamespaceReversedCachedTest(LoaderNamespaceReversedTest):

    def setUp(self):
        self.loader = LoaderNamespaceReversedCached()
