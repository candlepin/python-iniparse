# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import re
import config

from ConfigParser import DEFAULTSECT, ParsingError, MissingSectionHeaderError

class line_type(object):
    line = None

    def __init__(self, line=None):
        if line is not None:
            self.line = line.strip('\n')

    # Return the original line for unmodified objects
    # Otherwise construct using the current attribute values
    def __str__(self):
        if self.line is not None:
            return self.line
        else:
            return self.to_string()

    # If an attribute is modified after initialization
    # set line to None since it is no longer accurate.
    def __setattr__(self, name, value):
        if hasattr(self,name):
            self.__dict__['line'] = None
        self.__dict__[name] = value

    def to_string(self):
        raise Exception('This method must be overridden in derived classes')


class section_line(line_type):
    regex =  re.compile(r'^\['
                        r'(?P<name>[^]]+)'
                        r'\]\s*'
                        r'((?P<csep>;|#)(?P<comment>.*))?$')

    def __init__(self, name, comment=None, comment_separator=None,
                             comment_offset=-1, line=None):
        super(section_line, self).__init__(line)
        self.name = name
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def to_string(self):
        out = '[' + self.name + ']'
        if self.comment is not None:
            # try to preserve indentation of comments
            out = (out+' ').ljust(self.comment_offset)
            out = out + self.comment_separator + self.comment
        return out

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('name'), m.group('comment'),
                   m.group('csep'), m.start('csep'),
                   line)
    parse = classmethod(parse)


class option_line(line_type):
    def __init__(self, name, value, separator='=', comment=None,
                 comment_separator=None, comment_offset=-1, line=None):
        super(option_line, self).__init__(line)
        self.name = name
        self.value = value
        self.separator = separator
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def to_string(self):
        out = '%s %s %s' % (self.name, self.separator, self.value)
        if self.comment is not None:
            # try to preserve indentation of comments
            out = (out+' ').ljust(self.comment_offset)
            out = out + self.comment_separator + self.comment
        return out

    regex = re.compile(r'^(?P<name>[^:=\s[][^:=]*)'
                       r'\s*(?P<sep>[:=])\s*'
                       r'(?P<value>.*)$')

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None

        name = m.group('name').rstrip()
        value = m.group('value')
        sep = m.group('sep')

        # comments are not detected in the regex because
        # ensuring total compatibility with ConfigParser
        # requires that:
        #     option = value    ;comment   // value=='value'
        #     option = value;1  ;comment   // value=='value;1  ;comment'
        #
        # Doing this in a regex would be complicated.  I
        # think this is a bug.  The whole issue of how to
        # include ';' in the value needs to be addressed.
        # Also, '#' doesn't mark comments in options...

        coff = value.find(';')
        if coff != -1 and value[coff-1].isspace():
            comment = value[coff+1:]
            csep = value[coff]
            value = value[:coff].rstrip()
            coff = m.start('value') + coff
        else:
            comment = None
            csep = None
            coff = -1

        return cls(name, value, sep, comment, csep, coff, line)
    parse = classmethod(parse)


class comment_line(line_type):
    regex = re.compile(r'^(?P<csep>[;#]|[rR][eE][mM])'
                       r'(?P<comment>.*)$')

    def __init__(self, comment='', separator='#', line=None):
        super(comment_line, self).__init__(line)
        self.comment = comment
        self.separator = separator

    def to_string(self):
        return self.separator + self.comment

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('comment'), m.group('csep'), line)
    parse = classmethod(parse)


class empty_line(line_type):
    # could make this a singleton
    def to_string(self):
        return ''

    def parse(cls, line):
        if line.strip(): return None
        return cls(line)
    parse = classmethod(parse)


class continuation_line(line_type):
    regex = re.compile(r'^\s+(?P<value>.*)$')

    def __init__(self, value, value_offset=8, line=None):
        super(continuation_line, self).__init__(line)
        self.value = value
        self.value_offset = value_offset

    def to_string(self):
        return ' '*self.value_offset + self.value

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('value'), m.start('value'), line)
    parse = classmethod(parse)


class line_container(object):
    def __init__(self, d=None):
        self.contents = []
        if d:
            if isinstance(d, list): self.extend(d)
            else: self.add(d)

    def add(self, x):
        self.contents.append(x)

    def extend(self, x):
        for i in x: self.add(i)

    def get_name(self):
        return self.contents[0].name

    def set_name(self, data):
        self.contents[0].name = data

    def get_value(self):
        if len(self.contents) == 1:
            return self.contents[0].value
        else:
            return '\n'.join([str(x.value) for x in self.contents])

    def set_value(self, data):
        lines = str(data).split('\n')
        linediff = len(lines) - len(self.contents)
        if linediff > 0:
            for _ in range(linediff):
                self.add(continuation_line(''))
        elif linediff < 0:
            self.contents = self.contents[:linediff]
        for i,v in enumerate(lines):
            self.contents[i].value = v

    name = property(get_name, set_name)
    value = property(get_value, set_value)

    def __str__(self):
        s = [str(x) for x in self.contents]
        return '\n'.join(s)

    def finditer(self, key):
        for x in self.contents[::-1]:
            if hasattr(x, 'name') and x.name==key:
                yield x

    def find(self, key):
        for x in self.finditer(key):
            return x
        raise KeyError(key)


class section(config.namespace):
    lineobj = None
    options = None
    defaults = None
    optionxform = None
    def __init__(self, lineobj, defaults = None, optionxform=None):
        self.lineobj = lineobj
        self.defaults = defaults
        self.optionxform = optionxform
        self.options = {}

    def new_value(self, name, data):
        obj = line_container(option_line(name, ''))
        self.lineobj.add(obj)
        if self.optionxform: name = self.optionxform(name)
        self.options[name] = opt = option(obj)
        # we call opt.set() explicitly to automatically
        # handle the case of data having multiple lines
        opt.set(data)
        return opt

    def new_namespace(self, name):
        raise Exception('No sub-sections allowed', name)

    def rename(self, oldname, newname):
        if self.optionxform: oldname = self.optionxform(oldname)
        self.options[oldname].name = newname
        if self.optionxform: newname = self.optionxform(newname)
        self.options[newname] = self.options[oldname]
        del self.options[oldname]

    def delete(self, name):
        if self.optionxform: name = self.optionxform(name)
        self.lineobj.contents.remove(self.options[name].lineobj)
        del self.options[name]

    def get(self, name):
        if self.optionxform: name = self.optionxform(name)
        try:
            return self.options[name]
        except KeyError:
            if self.defaults and name in self.defaults.options:
                return self.defaults.options[name]
            else:
                raise

    def iterkeys(self):
        for x in self.options.iterkeys():
            yield x
        if self.defaults:
            for x in self.defaults.options.iterkeys():
                yield x


class option(config.value):
    def __init__(self, lineobj):
        self.lineobj = lineobj

    def get(self):
        return self.lineobj.value

    def set(self, data):
        self.lineobj.value = data


def make_comment(line):
    return comment_line(line.rstrip())


class inifile(config.namespace):
    data = None
    sections = None
    defaults = None
    sectionxform = None
    optionxform = None
    parse_exc = None
    def __init__(self, fobj=None, defaults = None, parse_exc=True,
                 optionxform=str.lower, sectionxform=None):
        self.data = line_container()
        self.parse_exc = parse_exc
        self.optionxform = optionxform
        self.sectionxform = sectionxform
        self.sections = {}
        if defaults is None: defaults = {}
        self.defaults = section(line_container(), optionxform=optionxform)
        for name, value in defaults.iteritems():
            self.defaults.new_value(name, value)
        if fobj is not None:
            self.read(fobj)

    def new_value(self, name, data):
        raise Exception('No values allowed at the top level', name, data)

    def new_namespace(self, name):
        if (self.data.contents):
            self.data.add(empty_line())
        obj = line_container(section_line(name))
        self.data.add(obj)
        if self.sectionxform: name = self.sectionxform(name)
        self.sections[name] = ns = section(obj, defaults=self.defaults,
                                           optionxform=self.optionxform)
        return ns

    def rename(self, oldname, newname):
        if self.sectionxform: oldname = self.sectionxform(oldname)
        self.sections[oldname].name = newname
        if self.sectionxform: newname = self.sectionxform(newname)
        self.sections[newname] = self.sections[oldname]
        del self.sections[oldname]

    def delete(self, name):
        if self.sectionxform: name = self.sectionxform(name)
        self.data.contents.remove(self.sections[name].lineobj)
        del self.sections[name]

    def get(self, name):
        if self.sectionxform: name = self.sectionxform(name)
        return self.sections[name]

    def iterkeys(self):
        return self.sections.iterkeys()

    def __str__(self):
        return str(self.data)

    line_types = [empty_line, comment_line,
                  section_line, option_line,
                  continuation_line]

    def parse(self, line):
        for linetype in self.line_types:
            lineobj = linetype.parse(line)
            if lineobj:
                return lineobj
        else:
            # can't parse line - convert to comment
            return None

    def read(self, fobj):
        cur_section = None
        cur_option = None
        cur_section_name = None
        cur_option_name = None
        pending_lines = []
        try:
            fname = fobj.name
        except AttributeError:
            fname = '<???>'
        linecount = 0
        exc = None
        for line in fobj:
            lineobj = self.parse(line)
            linecount += 1

            if not cur_section and not isinstance(lineobj,
                                (comment_line, empty_line, section_line)):
                if self.parse_exc:
                    raise MissingSectionHeaderError(fname, linecount, line)
                else:
                    lineobj = make_comment(line)

            if lineobj is None:
                if self.parse_exc:
                    if exc is None: exc = ParsingError(fname)
                    exc.append(linecount, line)
                lineobj = make_comment(line)

            if isinstance(lineobj, continuation_line):
                if cur_option:
                    cur_option.add(lineobj)
                else:
                    # illegal continuation line - convert to comment
                    if self.parse_exc:
                        if exc is None: exc = ParsingError(fname)
                        exc.append(linecount, line)
                    lineobj = make_comment(line)
            else:
                cur_option = None
                cur_option_name = None

            if isinstance(lineobj, option_line):
                cur_section.extend(pending_lines)
                pending_lines = []
                cur_option = line_container(lineobj)
                cur_section.add(cur_option)
                if self.optionxform:
                    cur_option_name = self.optionxform(cur_option.name)
                else:
                    cur_option_name = cur_option.name
                if cur_section_name == DEFAULTSECT:
                    optobj = self.defaults
                else:
                    optobj = self.sections[cur_section_name]
                optobj.options[cur_option_name] = option(cur_option)

            if isinstance(lineobj, section_line):
                self.data.extend(pending_lines)
                pending_lines = []
                cur_section = line_container(lineobj)
                self.data.add(cur_section)
                if cur_section.name == DEFAULTSECT:
                    self.defaults.lineobj = cur_section
                    cur_section_name = DEFAULTSECT
                else:
                    if self.sectionxform:
                        cur_section_name = self.sectionxform(cur_section.name)
                    else:
                        cur_section_name = cur_section.name
                    if not self.sections.has_key(cur_section_name):
                        self.sections[cur_section_name] = \
                                section(cur_section, defaults=self.defaults,
                                        optionxform=self.optionxform)
                    else:
                        self.sections[cur_section_name].lineobj = cur_section

            if isinstance(lineobj, (comment_line, empty_line)):
                pending_lines.append(lineobj)

        self.data.extend(pending_lines)
        if line and line[-1]=='\n':
            self.data.add(empty_line())

        if exc:
            raise exc

