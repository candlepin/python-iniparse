"""
<description>
"""

# ---- Abstract classes


class namespace(object):
    def __getitem__(self, key):
        return NotImplementedError(key)

    def __setitem__(self, key, value):
        raise NotImplementedError(key, value)

    def __delitem__(self, key):
        raise NotImplementedError(key)

    def __iter__(self):
        return NotImplementedError()

    def _new_namespace(self, name):
        raise NotImplementedError(name)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return unknown(name, self)

    def __setattr__(self, name, value):
        try:
            object.__getattribute__(self, name)
            object.__setattr__(self, name, value)
            return
        except AttributeError:
            self.__setitem__(name, value)

    def __delattr__(self, name):
        try:
            object.__getattribute__(self, name)
            object.__delattr__(self, name)
        except AttributeError:
            self.__delitem__(name)


class unknown(object):
    def __init__(self, name, namespace):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'namespace', namespace)

    def __setattr__(self, name, value):
        obj = self.namespace._new_namespace(self.name)
        obj[name] = value


# ---- Basic implementation of namespace


class basic_namespace(namespace):
    """Represents a collection of named values

    >>> n = basic_namespace()
    >>> n.x = 7
    >>> n.x
    7
    >>> n.name.first = 'paramjit'
    >>> n.name.last = 'oberoi'
    >>> isinstance(n.name, namespace)
    True
    >>> n.name.first
    'paramjit'
    >>> n.name.last
    'oberoi'

    >>> l = list(n)
    >>> l.sort()
    >>> l
    ['name', 'x']
    >>> l = list(n.name)
    >>> l.sort()
    >>> l
    ['first', 'last']

    >>> n.aaa = 42
    >>> del n.x
    >>> l = list(n)
    >>> l.sort()
    >>> l
    ['aaa', 'name']
    """

    # this makes sure that __setattr__ knows this is not a value key
    _data = None

    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def _new_namespace(self, name):
        obj = basic_namespace()
        self._data[name] = obj
        return obj

