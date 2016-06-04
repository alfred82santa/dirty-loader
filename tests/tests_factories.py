from logging import NullHandler, Filter, Formatter, getLogger
from unittest.case import TestCase
from dirty_loader import LoaderNamespace
from dirty_loader.factories import register_logging_factories

__author__ = 'alfred'


class LoggingHandlerFactoryTest(TestCase):

    def setUp(self):
        self.loader = LoaderNamespace()
        self.loader.register_namespace('logging', 'logging')
        register_logging_factories(self.loader)

    def test_simple_handler(self):
        handler = self.loader.factory('logging:NullHandler')
        self.assertIsInstance(handler, NullHandler)
        self.assertEqual(len(handler.filters), 0)

    def test_simple_handler_with_simple_filter(self):
        handler = self.loader.factory('logging:NullHandler', filters=['logging:Filter'])
        self.assertIsInstance(handler, NullHandler)
        self.assertEqual(len(handler.filters), 1)
        self.assertIsInstance(handler.filters[0], Filter)

    def test_simple_handler_with_parametrized_filter(self):
        handler = self.loader.factory('logging:NullHandler', filters=[{'type': 'logging:Filter',
                                                                       'params': {'name': 'foo.bar'}},
                                                                      {'type': 'logging:Filter'},
                                                                      'logging:Filter'])
        self.assertIsInstance(handler, NullHandler)
        self.assertEqual(len(handler.filters), 3)
        self.assertIsInstance(handler.filters[0], Filter)
        self.assertEqual(handler.filters[0].name, 'foo.bar')
        self.assertIsInstance(handler.filters[1], Filter)
        self.assertEqual(handler.filters[1].name, '')
        self.assertIsInstance(handler.filters[2], Filter)
        self.assertEqual(handler.filters[2].name, '')

    def test_simple_handler_with_simple_formatter(self):
        handler = self.loader.factory('logging:NullHandler', formatter='logging:Formatter')
        self.assertIsInstance(handler, NullHandler)
        self.assertIsInstance(handler.formatter, Formatter)

    def test_simple_handler_with_parametrized_formatter(self):
        handler = self.loader.factory('logging:NullHandler', formatter={'type': 'logging:Formatter',
                                                                        'params': {'datefmt': 'foo.bar'}})
        self.assertIsInstance(handler, NullHandler)
        self.assertIsInstance(handler.formatter, Formatter)
        self.assertEqual(handler.formatter.datefmt, 'foo.bar')


class LoggerFactoryTest(TestCase):

    def setUp(self):
        self.loader = LoaderNamespace()
        self.loader.register_namespace('logging', 'logging')
        register_logging_factories(self.loader)

    def test_simple_logger(self):
        logger = self.loader.factory('logging:Logger', name='foo.bar.test.1')
        self.assertEqual(logger, getLogger('foo.bar.test.1'))

    def test_simple_logger_with_simple_handler(self):
        logger = self.loader.factory('logging:Logger', name='foo.bar.test.2', handlers=['logging:NullHandler'])
        self.assertEqual(logger, getLogger('foo.bar.test.2'))
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], NullHandler)

