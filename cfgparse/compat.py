# compatibility interfaces for ConfigParser

from ConfigParser import DuplicateSectionError, NoSectionError, NoOptionError

import iniparser

class RawConfigParser(object):
    def __init__(self, defaults=None):
        self.data = iniparser.inifile(defaults=defaults)

    def defaults(self):
        d = {}
        for name, lineobj in self.data._defaults._options:
            d[name] = lineobj.value
        return d

    def sections(self):
        """Return a list of section names, excluding [DEFAULT]"""
        return list(self.data)

    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        """
        if self.has_section(section):
            raise DuplicateSectionError(section)
        else:
            self.data._new_namespace(section)

    def has_section(self, section):
        """Indicate whether the named section is present in the configuration.

        The DEFAULT section is not acknowledged.
        """
        try:
            self.data[section]
            return True
        except KeyError:
            return False

    def options(self, section):
        """Return a list of option names for the given section name."""
        try:
            return list(self.data[section])
        except KeyError:
            raise NoSectionError(section)

    def read(self, filenames):
        """Read and parse a filename or a list of filenames.

        Files that cannot be opened are silently ignored; this is
        designed so that you can specify a list of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), and all existing
        configuration files in the list will be read.  A single
        filename may also be given.
        """
        if isinstance(filenames, basestring):
            filenames = [filenames]
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue
            self.data.read(fp)
            fp.close()

    def readfp(self, fp, filename=None):
        """Like read() but the argument must be a file-like object.

        The `fp' argument must have a `readline' method.  Optional
        second argument is the `filename', which if not given, is
        taken from fp.name.  If fp has no `name' attribute, `<???>' is
        used.
        """
        self.data.read(fp)

    def get(self, section, option):
        try:
            return self.data[section][option]
        except KeyError:
            if not self.has_section(section):
                raise NoSectionError(section)
            else:
                raise NoOptionError(option, section)

    def items(self, section):
        try:
            ans = []
            for opt in self.data[section]:
                ans.append((opt, self.data[section][opt]))
            return ans
        except KeyError:
            raise NoSectionError(section)

    def getint(self, section, option):
        return int(self.get(section, option))

    def getfloat(self, section, option):
        return float(self.get(section, option))

    _boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                       '0': False, 'no': False, 'false': False, 'off': False}

    def getboolean(self, section, option):
        v = self.get(section, option)
        if v.lower() not in self._boolean_states:
            raise ValueError, 'Not a boolean: %s' % v
        return self._boolean_states[v.lower()]

    def get_oxf(self): return self.data._optionxform
    def set_oxf(self, value): self.data._optionxform = value
    optionxform = property(get_oxf, set_oxf)

    def has_option(self, section, option):
        """Check for the existence of a given option in a given section."""
        try:
            sec = self.data[section]
        except KeyError:
            raise NoSectionError(section)
        try:
            sec[option]
            return True
        except KeyError:
            return False

    def set(self, section, option, value):
        """Set an option."""
        try:
            self.data[section][option] = value
        except KeyError:
            raise NoSectionError(section)

    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        fp.write(str(self.data))

    def remove_option(self, section, option):
        """Remove an option."""
        try:
            sec = self.data[section]
        except KeyError:
            raise NoSectionError(section)
        try:
            sec[option]
            del sec[option]
            return 1
        except KeyError:
            return 0

    def remove_section(self, section):
        """Remove a file section."""
        if not self.has_section(section):
            return False
        del self.data[section]
        return True


class ConfigParser(RawConfigParser):

    def get(self, section, option, raw=False, vars=None):
        """Get an option value for a given section.

        All % interpolations are expanded in the return values, based on the
        defaults passed into the constructor, unless the optional argument
        `raw' is true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT is special.
        """
        d = self._defaults.copy()
        try:
            d.update(self._sections[section])
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)
        # Update with the entry specific variables
        if vars is not None:
            d.update(vars)
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            raise NoOptionError(option, section)

        if raw:
            return value
        else:
            return self._interpolate(section, option, value, d)

    def items(self, section, raw=False, vars=None):
        """Return a list of tuples with (name, value) for each option
        in the section.

        All % interpolations are expanded in the return values, based on the
        defaults passed into the constructor, unless the optional argument
        `raw' is true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT is special.
        """
        d = self._defaults.copy()
        try:
            d.update(self._sections[section])
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)
        # Update with the entry specific variables
        if vars:
            d.update(vars)
        options = d.keys()
        if "__name__" in options:
            options.remove("__name__")
        if raw:
            return [(option, d[option])
                    for option in options]
        else:
            return [(option, self._interpolate(section, option, d[option], d))
                    for option in options]

    def _interpolate(self, section, option, rawval, vars):
        # do the string interpolation
        value = rawval
        depth = MAX_INTERPOLATION_DEPTH
        while depth:                    # Loop through this until it's done
            depth -= 1
            if value.find("%(") != -1:
                try:
                    value = value % vars
                except KeyError, e:
                    raise InterpolationMissingOptionError(
                        option, section, rawval, e[0])
            else:
                break
        if value.find("%(") != -1:
            raise InterpolationDepthError(option, section, rawval)
        return value

