# compatibility interfaces for ConfigParser

import iniparser
import ConfigParser

class RawConfigParser(object):
    def __init__(self, defaults=None):
        self.data = iniparser.inifile(defaults=defaults)

    def defaults(self):
        d = {}
        for name, value in self.data.defaults.options.iteritems():
            d[name] = value.get()
        return d

    def sections(self):
        """Return a list of section names, excluding [DEFAULT]"""
        return list(self.data.iterkeys())

    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        """
        if self.has_section(section):
            raise ConfigParser.DuplicateSectionError(section)
        else:
            self.data.new_namespace(section)

    def has_section(self, section):
        """Indicate whether the named section is present in the configuration.

        The DEFAULT section is not acknowledged.
        """
        try:
            self.data.get(section)
            return True
        except KeyError:
            return False

    def options(self, section):
        """Return a list of option names for the given section name."""
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        else:
            return list(self.data.get(section).iterkeys())

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
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        elif not self.has_option(section, option):
            raise ConfigParser.NoOptionError(option, section)
        else:
            return self.data.get(section).get(option).get()

    def items(self, section):
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        else:
            ans = []
            for opt in self.data.get(section).iterkeys():
                ans.append((opt, self.data.get(section).get(opt).get()))
            return ans

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

    def get_oxf(self): return self.data.optionxform
    def set_oxf(self, value): self.data.optionxform = value
    optionxform = property(get_oxf, set_oxf)

    def has_option(self, section, option):
        """Check for the existence of a given option in a given section."""
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        else:
            try:
                self.data.get(section).get(option)
                return True
            except KeyError:
                return False

    def set(self, section, option, value):
        """Set an option."""
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        setattr(self.data.get(section), option, value)

    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        fp.write(str(self.data))

    def remove_option(self, section, option):
        """Remove an option."""
        if not self.has_section(section):
            raise ConfigParser.NoSectionError(section)
        if not self.has_option(section, option):
            return 0
        self.data.get(section).delete(option)
        return 1

    def remove_section(self, section):
        """Remove a file section."""
        if not self.has_section(section):
            return False
        self.data.delete(section)
        return True

