"""
<description>
"""

# ---- Abstract classes

class value(object):
    def get(self):
        raise NotImplementedError()

    def set(self, data):
        raise NotImplementedError(data)


class namespace(object):
    def new_value(self, name, data):
        raise NotImplementedError(name, data)

    def new_namespace(self, name):
        raise NotImplementedError(name)

    def rename(self, oldname, newname):
        raise NotImplementedError(oldname, newname)

    def delete(self, name):
        raise NotImplementedError(name)

    def get(self, name):
        return NotImplementedError(name)

    def iterkeys(self):
        return NotImplementedError()

    def __getattr__(self, name):
        try:
            obj = self.get(name)
            if isinstance(obj, value):
                return obj.get()
            else:
                return obj
        except KeyError:
            return unknown(name, self)

    def __setattr__(self, name, data):
        try:
            object.__getattribute__(self, name)
            object.__setattr__(self, name, data)
            return
        except AttributeError:
            pass

        try:
            obj = self.get(name)
            if isinstance(obj, value):
                obj.set(data)
            else:
                raise TypeError("Attempt to set a non-value", name)
        except KeyError:
            self.new_value(name, data)

    def __delattr__(self, name):
        self.delete(name)


class unknown(object):
    def __init__(self, name, namespace):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'namespace', namespace)

    def __setattr__(self, name, data):
        obj = self.namespace.new_namespace(self.name)
        setattr(obj, name, data)


# ---- Basic implementations of value and namespace

class basic_value(value):
    """Represents a value

    >>> v = basic_value('paramjit')
    >>> v.get()
    'paramjit'
    >>> v.set('oberoi')
    >>> v.get()
    'oberoi'
    """

    def __init__(self, data=None):
        self.data = data

    def get(self):
        return self.data

    def set(self, data):
        self.data = data


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

    >>> l = list(n.iterkeys())
    >>> l.sort()
    >>> l
    ['name', 'x']
    >>> l = list(n.name.iterkeys())
    >>> l.sort()
    >>> l
    ['first', 'last']

    >>> n.aaa = 42
    >>> del n.x
    >>> n.rename('name', 'user')
    >>> l = list(n.iterkeys())
    >>> l.sort()
    >>> l
    ['aaa', 'user']
    """

    # this makes sure that __setattr__ knows this is not a value key
    named_values = None

    def __init__(self):
        self.named_values = {}

    def new_value(self, name, data):
        obj = basic_value(data)
        self.named_values[name] = obj
        return obj

    def new_namespace(self, name):
        obj = basic_namespace()
        self.named_values[name] = obj
        return obj

    def rename(self, oldname, newname):
        self.named_values[newname] = self.named_values[oldname]
        del self.named_values[oldname]

    def delete(self, name):
        del self.named_values[name]

    def get(self, name):
        return self.named_values[name]

    def iterkeys(self):
        return self.named_values.iterkeys()
