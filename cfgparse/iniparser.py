# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import re
import config

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
        lines = data.split('\n')
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
    def __init__(self, lineobj):
        self.lineobj = lineobj
        self.options = {}

    def new_value(self, name, data):
        obj = line_container(option_line(name, ''))
        self.lineobj.add(obj)
        self.options[name] = opt = option(obj)
        # we call opt.set() explicitly to automatically
        # handle the case of data having multiple lines
        opt.set(data)
        return opt

    def new_namespace(self, name):
        raise Exception('No sub-sections allowed', name)

    def rename(self, oldname, newname):
        self.options[oldname].name = newname
        self.options[newname] = self.options[oldname]
        del self.options[oldname]

    def delete(self, name):
        self.lineobj.contents.remove(self.options[name])
        del self.options[name]

    def get(self, name):
        return self.options[name]

    def iterkeys(self):
        return self.options.iterkeys()


class option(config.value):
    def __init__(self, lineobj):
        self.lineobj = lineobj

    def get(self):
        return self.lineobj.value

    def set(self, data):
        self.lineobj.value = data


def make_comment(line):
    # print_warning('can\'t parse "%s"' % line)
    return comment_line(line.rstrip())


class inifile(config.namespace):
    data = None
    sections = None
    def __init__(self, fobj=None):
        self.data = line_container()
        self.sections = {}
        if fobj is not None:
            self.read(fobj)

    def new_value(self, name, data):
        raise Exception('No values allowed at the top level', name, data)

    def new_namespace(self, name):
        if (self.data.contents):
            self.data.add(empty_line())
        obj = line_container(section_line(name))
        self.data.add(obj)
        self.sections[name] = ns = section(obj)
        return ns

    def rename(self, oldname, newname):
        self.sections[oldname].name = newname
        self.sections[newname] = self.sections[oldname]
        del self.sections[oldname]

    def delete(self, name):
        self.data.contents.remove(self.sections[name])
        del self.sections[name]

    def get(self, name):
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
            return make_comment(line)

    def read(self, fobj):
        cur_section = None
        cur_option = None
        pending_lines = []
        for line in fobj:
            lineobj = self.parse(line)

            if isinstance(lineobj, continuation_line):
                if cur_option:
                    cur_option.add(lineobj)
                else:
                    # illegal continuation line - convert to comment
                    lineobj = make_comment(line)
            else:
                cur_option = None

            if isinstance(lineobj, option_line):
                if cur_section:
                    cur_section.extend(pending_lines)
                    pending_lines = []
                    cur_option = line_container(lineobj)
                    cur_section.add(cur_option)
                    self.sections[cur_section.name].\
                         options[cur_option.name] = option(cur_option)
                else:
                    # illegal option line - convert to comment
                    lineobj = make_comment(line)

            if isinstance(lineobj, section_line):
                self.data.extend(pending_lines)
                pending_lines = []
                cur_section = line_container(lineobj)
                self.data.add(cur_section)
                if not self.sections.has_key(cur_section.name):
                    self.sections[cur_section.name] = section(cur_section)
                else:
                    self.sections[cur_section.name].lineobj = cur_section

            if isinstance(lineobj, (comment_line, empty_line)):
                pending_lines.append(lineobj)

        self.data.extend(pending_lines)
        if line and line[-1]=='\n':
            self.data.add(empty_line())

