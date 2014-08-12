from collections import OrderedDict
import importlib

__author__ = 'alfred'


class DirtyLoaderException(Exception):
    pass


class AlreadyRegistered(DirtyLoaderException):
    pass


class NoRegistered(DirtyLoaderException):
    pass


class Loader():

    def __init__(self, modules=None):
        self._modules = modules if modules is not None else list()

    def register_module(self, module, idx=-1):
        if module in self._modules:
            raise AlreadyRegistered("Module '{0}' is already registered on loader.".format(module))

        if idx < 0:
            self._modules.append(module)
        else:
            self._modules.insert(idx, module)

    def unregister_module(self, module):
        if module not in self._modules:
            raise NoRegistered("Module '{0}' is not registered on loader.".format(module))

        self._modules.remove(module)

    def get_registered_modules(self):
        return self._modules.copy()

    def load_class(self, classname):
        module_list = self._get_module_list()

        submodule = False
        if '.' in classname:
            submodule, classname = classname.rsplit('.', 1)
            submodule = '.' + submodule
        for module in module_list:
            try:
                if submodule:
                    try:
                        module = importlib.import_module(submodule, module.__name__)
                    except ImportError:
                        continue
                return getattr(module, classname)
            except AttributeError:
                pass

        raise ImportError("Class '{0}' could not be loaded.".format(classname))

    def _get_module_list(self):
        return [importlib.import_module(name) if isinstance(name, str) else name
                for name in self._modules]

    def factory(self, classname, *args, **kwargs):
        klass = self.load_class(classname)
        return klass(*args, **kwargs)


class ReversedMixin():

    def _get_module_list(self):
        return reversed(super(ReversedMixin, self)._get_module_list())


class LoaderReversed(ReversedMixin, Loader):
    pass


class CacheLoaderMixin():

    def __init__(self, *args, **kwargs):
        super(CacheLoaderMixin, self).__init__(*args, **kwargs)
        self._cache = {}

    def invalidate_cache(self):
        self._cache = {}

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


class LoaderCached(CacheLoaderMixin, Loader):
    pass


class LoaderReversedCached(CacheLoaderMixin, LoaderReversed):
    pass


class LoaderNamespace(Loader):

    def __init__(self, namespaces=None):
        self._namespaces = namespaces if namespaces is not None else OrderedDict()

    def register_module(self, module, namespace=None):
        namespace = namespace if namespace is not None else str(module)
        self.register_namespace(namespace, module)

    def register_namespace(self, namespace, module):
        if namespace in self._namespaces:
            raise AlreadyRegistered("Namespace '{0}' is already registered on loader.".format(namespace))

        self._namespaces[namespace] = module

    def unregister_module(self, module):
        if module not in self._namespaces.values():
            raise NoRegistered("Module '{0}' is not registered on loader.".format(module))

        for ns, mod in list(self._namespaces.items()):
            if mod == module:
                self.unregister_namespace(ns)

    def unregister_namespace(self, namespace):
        if namespace not in self._namespaces:
            raise NoRegistered("Namespace '{0}' is not registered on loader.".format(namespace))

        del self._namespaces[namespace]

    def get_registered_modules(self):
        return self._namespaces.values()

    def get_registered_namespaces(self):
        return OrderedDict(self._namespaces)

    def load_class(self, classname, namespace=None):
        if namespace is None and ':' in classname:
            namespace, classname = classname.split(':', 1)
            return self.load_class(classname, namespace)
        if namespace:
            if namespace not in self._namespaces:
                raise NoRegistered("Namespace '{0}' is not registered on loader.".format(namespace))
            try:
                module = importlib.import_module(self._namespaces[namespace]) \
                    if isinstance(self._namespaces[namespace], str) else self._namespaces[namespace]
                if '.' in classname:
                    submodule, classname = classname.rsplit('.', 1)
                    module = importlib.import_module('.' + submodule, module.__name__)

                return getattr(module, classname)
            except AttributeError:
                raise ImportError("Class '{0}' could not be loaded from namespace '{1}'.".format(classname,
                                                                                                 namespace))
        return super(LoaderNamespace, self).load_class(classname)

    def _get_module_list(self):
        return [importlib.import_module(name) if isinstance(name, str) else name
                for name in self._namespaces.values()]


class LoaderNamespaceReversed(ReversedMixin, LoaderNamespace):
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
    pass


class LoaderNamespaceReversedCached(CacheLoaderNamespaceMixin, LoaderNamespaceReversed):
    pass
