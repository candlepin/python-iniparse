# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import re, StringIO
import line_types

class getter(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        value = self.obj.get(name)
        if hasattr(value, 'get'):
            return getter(value)
        else:
            return value

class section(object):
    def __init__(self):
        self.options = {}

    # keeping copy of name---if the name is
    # modified, the dict must be a well
    def add_option(self, l):
        self.options[l.option] = l

    def get(self, option):
        return self.options[option].value

    def get_line(self, option):
        return self.options[option]

    def __getitem__(self, key):
        if key in self.options:
            return self.options[key].value
        else:
            raise IndexError, '%s not found' % key


class iniparser(object):
    line_types = [line_types.empty_line,
                  line_types.comment_line,
                  line_types.section_line,
                  line_types.option_line,
                  line_types.continuation_line]

    def __init__(self, f=None):
        self.lines = []
        self.sections = {'DEFAULT' : section()}
        self.options = getter(self)
        if f is not None:
            self.read_file(f)

    def parse(self, line):
        for linetype in self.line_types:
            lineobj = linetype.parse(line)
            if lineobj:
                return lineobj, linetype
        else:
            # can't parse line - convert to comment
            return comment_line(line), comment_line

    def read_file(self, f):
        cur_section = self.sections['DEFAULT']
        for line in f:
            lineobj, linetype = self.parse(line)
            self.lines.append(lineobj)
            if linetype == line_types.option_line:
                cur_section.add_option(lineobj)
            elif linetype == line_types.section_line:
                cur_section = self.sections.get(lineobj.name)
                if cur_section is None:
                    cur_section = section()
                    self.sections[lineobj.name] = cur_section

    def write_file(self, f):
        for lineobj in self.lines:
            f.write(str(lineobj))
            f.write('\n')

    def __str__(self):
        s = StringIO.StringIO()
        self.write_file(s)
        return s.getvalue()

    def get(self, secname):
        return self.sections[secname]

    def __getitem__(self, key):
        if key in self.sections:
            return self.sections[key]
        else:
            raise IndexError, '%s not found' % key
