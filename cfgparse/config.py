"""
<description>
"""

class namespace(object):
    """Represents a collection of named values

    >>> n = namespace(datasource())
    >>> n.x = 7
    >>> n.x
    7
    >>> n.name.first = 'paramjit'
    >>> n.name.last = 'oberoi'
    >>> type(n.name)
    <class 'cfgparse.config.namespace'>
    >>> n.name.first
    'paramjit'
    >>> n.name.last
    'oberoi'
    """

    def __init__(self, datasource):
        object.__setattr__(self, '_data', datasource)

    def _new_value(self, name, data):
        obj = self._data.create_value(name, data)
        object.__setattr__(self, name, obj)
        return obj

    def _new_namespace(self, name):
        obj = self._data.create_namespace(name)
        object.__setattr__(self, name, obj)
        return obj

    def __getattribute__(self, name):
        try:
            obj = object.__getattribute__(self, name)
            if isinstance(obj, value):
                return obj.get()
            else:
                return obj
        except AttributeError:
            return unknown(name, self)


    def __setattr__(self, name, data):
        try:
            obj = object.__getattribute__(self, name)
            if isinstance(obj, value):
                obj.set(data)
            else:
                object.__setattr__(self, name, data)
        except AttributeError:
            self._new_value(name, data)


class unknown(object):
    def __init__(self, name, namespace):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'namespace', namespace)

    def __setattr__(self, name, data):
        obj = self.namespace._new_namespace(self.name)
        setattr(obj, name, data)


class datasource(object):
    def __init__(self):
        self._dict = {}

    def create_value(self, name, data):
        v = value(name, data)
        self._dict[name] = v
        return v

    def create_namespace(self, name):
        d = datasource()
        n = namespace(d)
        self._dict[name] = d
        return n


class value(object):
    """Represents a value

    >>> v = value('user', 'paramjit')
    >>> v.get()
    'paramjit'
    >>> v.set('oberoi')
    >>> v.get()
    'oberoi'
    """

    def __init__(self, name=None, data=None):
        self.name = name
        self.data = data

    def get(self):
        return self.data

    def set(self, data):
        self.data = data

    def rename(self, name):
        self.name = name
