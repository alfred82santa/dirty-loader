from importlib import import_module

from collections import OrderedDict
import importlib

__author__ = 'alfred'


class DirtyLoaderException(Exception):
    pass


class AlreadyRegisteredError(DirtyLoaderException):
    pass


class NoRegisteredError(DirtyLoaderException):
    pass


class Loader:

    """
    Loader is a class loader. You must register python modules where to look for classes.
    First modules registered has preference in front last ones, but you could indicate index where
    you want insert new module.
    """

    def __init__(self, modules=None, factories=None):
        """
        Loader initialitzer.

        :param modules: must be a list of python modules. Modules can be strings or module objects
        :type modules: list
        """

        self._modules = modules or []
        self._factories = factories or {}

    def register_module(self, module, idx=-1):
        """
        Register a module. You could indicate position inside inner list.

        :param module: must be a string or a module object to register.
        :type module: str
        :param idx: position where you want to insert new module. By default it is inserted at the end.
        :type idx: int
        """

        if module in self._modules:
            raise AlreadyRegisteredError("Module '{0}' is already registered on loader.".format(module))

        if idx < 0:
            self._modules.append(module)
        else:
            self._modules.insert(idx, module)

    def unregister_module(self, module):
        """
        Unregister a module.

        :param module: must be a string or a module object to unregistered
        :type module: str
        """

        if module not in self._modules:
            raise NoRegisteredError("Module '{0}' is not registered on loader.".format(module))

        self._modules.remove(module)

    def get_registered_modules(self):
        """
        Return registered modules.

        :return: list of registered modules.
        :rtype: list
        """

        return self._modules.copy()

    def load_class(self, classname):
        """
        Loads a class looking for it in each module registered.

        :param classname: Class name you want to load.
        :type classname: str
        :return: Class object
        :rtype: type
        """

        module_list = self._get_module_list()

        for module in module_list:
            try:
                return import_class(classname, module.__name__)
            except (AttributeError, ImportError):
                pass

        raise ImportError("Class '{0}' could not be loaded.".format(classname))

    def _get_module_list(self):
        return [importlib.import_module(name) if isinstance(name, str) else name
                for name in self._modules]

    def factory(self, classname, *args, **kwargs):
        """
        Creates an instance of class looking for it in each module registered. You can
        add needed params to instance the class.

        :param classname: Class name you want to create an instance.
        :type classname: str
        :return: An instance of classname
        :rtype: object
        """

        klass = self.load_class(classname)

        return self.get_factory_by_class(klass)(*args, **kwargs)

    def get_factory_by_class(self, klass):
        """
        Returns a custom factory for class. By default it will return the class itself.

        :param klass: Class type
        :type klass: type
        :return: Class factory
        :rtype: callable
        """
        for check, factory in self._factories.items():
            if klass is check:
                return factory(self, klass)
        for check, factory in self._factories.items():
            if issubclass(klass, check):
                return factory(self, klass)
        return klass

    def register_factory(self, klass, factory):
        self._factories[klass] = factory

    def unregister_factory(self, klass):
        del self._factories[klass]


class ReversedMixin:

    def _get_module_list(self):
        return reversed(super(ReversedMixin, self)._get_module_list())


class LoaderReversed(ReversedMixin, Loader):

    """
    LoaderReversed is a class loader. You must register python modules where to look for classes.
    Last modules registered has preference in front first ones, but you could indicate index where
    you want insert new module.
    """
    pass


class CacheLoaderMixin:

    def __init__(self, *args, **kwargs):
        super(CacheLoaderMixin, self).__init__(*args, **kwargs)
        self._cache = {}
        self._cache_factories = {}

    def invalidate_cache(self):
        """
        Invalidate class cache.
        """
        self._cache = {}

    def invalidate_cache_factories(self):
        """
        Invalidate factories cache.
        """
        self._cache_factories = {}

    def register_module(self, *args, **kwargs):
        super(CacheLoaderMixin, self).register_module(*args, **kwargs)
        self.invalidate_cache()

    def unregister_module(self, *args, **kwargs):
        super(CacheLoaderMixin, self).unregister_module(*args, **kwargs)
        self.invalidate_cache()

    def load_class(self, classname, avoid_cache=False, *args, **kwargs):
        if not avoid_cache:
            try:
                return self._cache[classname]
            except KeyError:
                pass

        result = super(CacheLoaderMixin, self).load_class(classname, *args, **kwargs)

        if not avoid_cache:
            self._cache[classname] = result
        return result

    def get_factory_by_class(self, klass, avoid_cache=False):
        if not avoid_cache:
            try:
                return self._cache_factories[klass]
            except KeyError:
                pass

        result = super(CacheLoaderMixin, self).get_factory_by_class(klass)

        if not avoid_cache:
            self._cache_factories[klass] = result
        return result

    def register_factory(self, klass, factory):
        super(CacheLoaderMixin, self).register_factory(klass, factory)
        self.invalidate_cache_factories()

    def unregister_factory(self, klass):
        super(CacheLoaderMixin, self).unregister_factory(klass)
        self.invalidate_cache_factories()


class LoaderCached(CacheLoaderMixin, Loader):

    """
    LoaderCached is a class loader. You must register python modules where to look for classes.
    First modules registered has preference in front last ones, but you could indicate index where
    you want insert new module.

    Already looked up classes are cached.
    """
    pass


class LoaderReversedCached(CacheLoaderMixin, LoaderReversed):

    """
    Already looked up classes are cached.LoaderReversedCached is a class loader. You must register
    python modules where to look for classes. Last modules registered has preference in front
    first ones, but you could indicate index where you want insert new module.
    """
    pass


class LoaderNamespace(Loader):

    """
    LoaderNamespace is a class loader. You must register python modules with a namespace tag where
    to look for classes. First namespace registered has preference in front last ones.
    """

    def __init__(self, namespaces=None, factories=None):
        """
        LoaderNamespace initialitzer.

        :param namespaces: must be a OrderedDict of namespace as key and python module as value.
            Modules can be strings or module objects
        :type namespaces: OrderedDict
        """
        self._namespaces = namespaces or OrderedDict()
        self._factories = factories or {}

    def register_module(self, module, namespace=None):
        """
        Register a module.

        :param module: must be a string or a module object to register.
        :type module: str
        :param namespace: Namespace tag. If it is None module will be used as namespace tag
        :type namespace: str
        """
        namespace = namespace if namespace is not None else module \
            if isinstance(module, str) else module.__name__
        self.register_namespace(namespace, module)

    def register_namespace(self, namespace, module):
        """
        Register a namespace.

        :param namespace: Namespace tag.
        :type namespace: str
        :param module: must be a string or a module object to register.
        :type module: str
        """
        if namespace in self._namespaces:
            raise AlreadyRegisteredError("Namespace '{0}' is already registered on loader.".format(namespace))

        self._namespaces[namespace] = module

    def unregister_module(self, module):
        """
        Unregister a module.

        :param module: must be a string or a module object to unregistered
        :type module: str
        """
        if module not in self._namespaces.values():
            raise NoRegisteredError("Module '{0}' is not registered on loader.".format(module))

        for ns, mod in list(self._namespaces.items()):
            if mod == module:
                self.unregister_namespace(ns)

    def unregister_namespace(self, namespace):
        """
        Unregister a namespace.

        :param namespace: Namespace tag.
        :type namespace: str
        """
        if namespace not in self._namespaces:
            raise NoRegisteredError("Namespace '{0}' is not registered on loader.".format(namespace))

        del self._namespaces[namespace]

    def get_registered_modules(self):
        """
        Return registered modules.

        :return: list of registered modules.
        :rtype: list
        """
        return self._namespaces.values()

    def get_registered_namespaces(self):
        """
        Return registered namespaces.

        :return: Dict with namespaces as key and modules as value.
        :rtype: OrderedDict
        """
        return OrderedDict(self._namespaces)

    def load_class(self, classname, namespace=None):
        """
        Loads a class looking for it in each module registered. It's possible to load a class from
        specific namespace using **namespace** parameter or using classname as "namespace:classname".

        :param classname: Class name you want to load.
        :type classname: str
        :param namespace: Specific namespace where to look for class.
        :type namespace: str
        :return: Class object
        :rtype: type
        """
        if namespace is None and ':' in classname:
            namespace, classname = classname.split(':', 1)
            return self.load_class(classname, namespace)
        if namespace:
            if namespace not in self._namespaces:
                raise NoRegisteredError("Namespace '{0}' is not registered on loader.".format(namespace))
            try:
                module = importlib.import_module(self._namespaces[namespace]) \
                    if isinstance(self._namespaces[namespace], str) else self._namespaces[namespace]

                return import_class(classname, module.__name__)
            except (AttributeError, ImportError):
                raise ImportError("Class '{0}' could not be loaded from namespace '{1}'.".format(classname,
                                                                                                 namespace))
        return super(LoaderNamespace, self).load_class(classname)

    def _get_module_list(self):
        return [importlib.import_module(name) if isinstance(name, str) else name
                for name in self._namespaces.values()]


class LoaderNamespaceReversed(ReversedMixin, LoaderNamespace):

    """
    LoaderNamespaceReversed is a class loader. You must register python modules with a namespace tag where
    to look for classes. Last namespaces registered has preference in front first ones.
    """
    pass


class CacheLoaderNamespaceMixin(CacheLoaderMixin):

    def register_namespace(self, *args, **kwargs):
        super(CacheLoaderNamespaceMixin, self).register_namespace(*args, **kwargs)
        self.invalidate_cache()

    def unregister_namespace(self, *args, **kwargs):
        super(CacheLoaderNamespaceMixin, self).unregister_namespace(*args, **kwargs)
        self.invalidate_cache()

    def load_class(self, classname, namespace=None, avoid_cache=False):
        if namespace is None and not avoid_cache:
            try:
                return self._cache[classname]
            except KeyError:
                pass
        result = super(CacheLoaderNamespaceMixin, self).load_class(classname,
                                                                   namespace=namespace,
                                                                   avoid_cache=True)

        if namespace is None and not avoid_cache:
            self._cache[classname] = result

        return result


class LoaderNamespaceCached(CacheLoaderNamespaceMixin, LoaderNamespace):

    """
    LoaderNamespace is a class loader. You must register python modules with a namespace tag where
    to look for classes. First namespace registered has preference in front last ones.

    Already looked up classes are cached.
    """
    pass


class LoaderNamespaceReversedCached(CacheLoaderNamespaceMixin, LoaderNamespaceReversed):

    """
    LoaderNamespaceReversed is a class loader. You must register python modules with a namespace tag where
    to look for classes. Last namespaces registered has preference in front first ones.

    Already looked up classes are cached.
    """
    pass


def import_class(classpath, package=None):
    """
    Load and return a class
    """
    if '.' in classpath:
        module, classname = classpath.rsplit('.', 1)
        if package and not module.startswith('.'):
            module = '.{0}'.format(module)
        mod = import_module(module, package)
    else:
        classname = classpath
        mod = import_module(package)

    return getattr(mod, classname)
