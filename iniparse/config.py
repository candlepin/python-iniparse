# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

"""Implements basic mechanisms for managing configuration information

* A NAMESPACE is a collection of values and other namepsaces
* A VALUE is a basic value, like 3.1415, or 'Hello World!'
* A NAME identifies a value or namespace within a namespace

The namespace class is an abstract class that defines the basic
interface implemented by all namespace objects.  Two concrete
implementations are include: basic_namespace and ini_namespace.

Each is described in detail elsewhere.  However, here's an
example of the capabilities available:

Create namespace and populate it:

    >>> n = basic_namespace()
    >>> n.playlist.expand_playlist = True
    >>> n.ui.display_clock = True
    >>> n.ui.display_qlength = True
    >>> n.ui.width = 150

Examine data:

    >>> print n.playlist.expand_playlist
    True
    >>> print n['ui']['width']
    150

    >>> print n
    playlist.expand_playlist = True
    ui.display_clock = True
    ui.display_qlength = True
    ui.width = 150

Delete items:

    >>> del n.playlist
    >>> print n
    ui.display_clock = True
    ui.display_qlength = True
    ui.width = 150

Convert it to ini format:

    >>> from cfgparse import iniparser
    >>> i = iniparser.ini_namespace()
    >>> i.import_namespace(n)

    >>> print i
    [ui]
    display_clock = True
    display_qlength = True
    width = 150
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

    def new_namespace(self, name):
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

    def import_namespace(self, ns):
        for name in ns:
            value = ns[name]
            if isinstance(value, namespace):
                try:
                    myns = self[name]
                    if not isinstance(myns, namespace):
                        raise TypeError('value-namespace conflict')
                except KeyError:
                    myns = self.new_namespace(name)
                myns.import_namespace(value)
            else:
                self[name] = value

class unknown(object):
    def __init__(self, name, namespace):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'namespace', namespace)

    def __setattr__(self, name, value):
        obj = self.namespace.new_namespace(self.name)
        obj[name] = value


# ---- Basic implementation of namespace


class basic_namespace(namespace):
    """Represents a collection of named values

    Values are added using dotted notation:

    >>> n = basic_namespace()
    >>> n.x = 7
    >>> n.name.first = 'paramjit'
    >>> n.name.last = 'oberoi'

    ...and accessed the same way, or with [...]:

    >>> n.x
    7
    >>> n.name.first
    'paramjit'
    >>> n.name.last
    'oberoi'
    >>> n['x']
    7

    The namespace object is a 'container object'.  The default
    iterator returns the names of values (i.e. keys).

    >>> l = list(n)
    >>> l.sort()
    >>> l
    ['name', 'x']

    Values can be deleted using 'del' and printed using 'print'.

    >>> n.aaa = 42
    >>> del n.x
    >>> print n
    aaa = 42
    name.first = paramjit
    name.last = oberoi

    Nested namepsaces are also namespaces:

    >>> isinstance(n.name, namespace)
    True
    >>> print n.name
    first = paramjit
    last = oberoi

    Finally, values can be read from a file as follows:

    >>> from StringIO import StringIO
    >>> sio = StringIO('''
    ... # comment
    ... ui.height = 100
    ... ui.width = 150
    ... complexity = medium
    ... have_python
    ... data.secret.password = goodness=gracious me
    ... ''')
    >>> n = basic_namespace()
    >>> n.readfp(sio)
    >>> print n
    complexity = medium
    data.secret.password = goodness=gracious me
    have_python
    ui.height = 100
    ui.width = 150
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

    def __str__(self, prefix=''):
        lines = []
        keys = self._data.keys()
        keys.sort()
        for name in keys:
            value = self._data[name]
            if isinstance(value, namespace):
                lines.append(value.__str__(prefix='%s%s.' % (prefix,name)))
            else:
                if value is None:
                    lines.append('%s%s' % (prefix, name))
                else:
                    lines.append('%s%s = %s' % (prefix, name, value))
        return '\n'.join(lines)

    def new_namespace(self, name):
        obj = basic_namespace()
        self._data[name] = obj
        return obj

    def readfp(self, fp):
        for line in fp:
            line = line.strip()
            if not line: continue
            if line[0] == '#': continue
            data = line.split('=', 1)
            if len(data) == 1:
                name = line
                value = None
            else:
                name = data[0].strip()
                value = data[1].strip()
            name_components = name.split('.')
            ns = self
            for n in name_components[:-1]:
                try:
                    ns = ns[n]
                    if not isinstance(ns, namespace):
                        raise TypeError('value-namespace conflict', n)
                except KeyError:
                    ns = ns.new_namespace(n)
            ns[name_components[-1]] = value
