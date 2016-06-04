import logging


def instance_params(desc):
    if isinstance(desc, str):
        return desc, {}

    klass = desc['type']
    try:
        params = desc['params']
    except KeyError:
        params = {}

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


class BaseLoggingFactory(BaseFactory):

    def add_filters(self, obj, filters):
        try:
            for f in filters:
                if not isinstance(f, logging.Filter):
                    klass, params = instance_params(f)
                    f = self.loader.factory(klass, **params)
                obj.addFilter(f)
        except TypeError:
            pass


class LoggerFactory(BaseLoggingFactory):
    """
    Logger factory.
    """

    def __call__(self, name, propagate=True, level=logging.DEBUG, handlers=None, filters=None):
        logger = logging.getLogger(name)
        logger.propagate = propagate
        logger.setLevel(level)

        try:
            for handler in handlers:
                if not isinstance(handler, logging.Handler):
                    klass, params = instance_params(handler)
                    handler = self.loader.factory(klass, **params)
                logger.addHandler(handler)
        except TypeError:
            pass

        self.add_filters(logger, filters)

        return logger


class LoggingHandlerFactory(BaseLoggingFactory):
    """
    Logger handle factory.
    """

    def __call__(self, formatter=None, filters=None, *args, **kwargs):
        handler = self.klass(*args, **kwargs)

        if formatter:
            if not isinstance(formatter, logging.Formatter):
                klass, params = instance_params(formatter)
                formatter = self.loader.factory(klass, **params)
            handler.setFormatter(formatter)

        self.add_filters(handler, filters)

        return handler


def register_logging_factories(loader):
    """
    Registers default factories for logging standard package.

    :param loader: Loader where you want register default logging factories
    """
    loader.register_factory(logging.Logger, LoggerFactory)
    loader.register_factory(logging.Handler, LoggingHandlerFactory)
