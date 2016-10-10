import logging


def instance_params(desc):
    if isinstance(desc, str):
        return desc, {}
    try:
        klass = desc['type']
        try:
            params = desc['params']
        except KeyError:
            params = {}
    except KeyError:
        klass = list(desc.keys())[0]
        params = desc.pop(klass)

    return klass, params


class BaseFactory:
    """
    Base class factory. It should be used in order to implement specific ones.
    """

    def __init__(self, loader, klass):
        self.loader = loader
        self.klass = klass

    def __call__(self, *args, **kwargs):
        return self.klass(*args, **kwargs)

    def load_item(self, item, allowed_classes=tuple()):
        if isinstance(item, allowed_classes):
            return item
        klass, params = instance_params(item)
        return self.loader.factory(klass, **params)

    def iter_loaded_item_list(self, item_list, allowed_classes=tuple()):
        try:
            for item in item_list:
                yield self.load_item(item, allowed_classes)
        except TypeError:
            pass

    def iter_loaded_named_item_list(self, item_list, allowed_classes=tuple()):
        try:
            for name, item in item_list.items():
                yield name, self.load_item(item, allowed_classes)
        except AttributeError:
            pass


class BaseLoggingFactory(BaseFactory):

    def add_filters(self, obj, filters):
        list(map(obj.addFilter, self.iter_loaded_item_list(filters, logging.Filter)))


class LoggerFactory(BaseLoggingFactory):
    """
    Logger factory.
    """

    def __call__(self, name, propagate=True, level=logging.DEBUG, handlers=None, filters=None):
        logger = logging.getLogger(name)
        logger.propagate = propagate
        logger.setLevel(level)

        list(map(logger.addHandler, self.iter_loaded_item_list(handlers, logging.Handler)))
        self.add_filters(logger, filters)

        return logger


class LoggingHandlerFactory(BaseLoggingFactory):
    """
    Logger handle factory.
    """

    def __call__(self, formatter=None, filters=None, *args, **kwargs):
        handler = self.klass(*args, **kwargs)

        if formatter:
            handler.setFormatter(self.load_item(formatter, logging.Formatter))

        self.add_filters(handler, filters)

        return handler


def register_logging_factories(loader):
    """
    Registers default factories for logging standard package.

    :param loader: Loader where you want register default logging factories
    """
    loader.register_factory(logging.Logger, LoggerFactory)
    loader.register_factory(logging.Handler, LoggingHandlerFactory)
