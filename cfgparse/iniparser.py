# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import sys
import StringIO
import line_types

def print_warning(w):
    print >>sys.stderr, "Warning:", w

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
    def add_option(self, opt):
        self.options[opt.name] = opt

    def get(self, opt):
        return self.options[opt].value

    def __getitem__(self, key):
        if key in self.options:
            return self.options[key].value
        else:
            raise IndexError, '%s not found' % key

class option(object):
    def __init__(self, lineobj, cur_section):
        self.lines = [lineobj]
        self.section = cur_section
        self.name = lineobj.option
        self.value = lineobj.value

    def add_line(self,lineobj):
        self.lines.append(lineobj)
        self.value += "\n%s" % lineobj.value


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
                return lineobj
        else:
            # can't parse line - convert to comment
            print_warning('can\'t parse "%s"' % line)
            return line_types.comment_line(line)

    def read_file(self, f):
        cur_section = self.sections['DEFAULT']
        cur_option = None
        for line in f:
            lineobj = self.parse(line)
            if isinstance(lineobj, line_types.option_line):
                cur_option = option(lineobj, cur_section)
                cur_section.add_option(cur_option)
            elif isinstance(lineobj, line_types.continuation_line):
                if cur_option:
                    cur_option.add_line(lineobj)
                else:
                    # illegal continuation line - convert to comment
                    print_warning('can\'t parse: "%s"' % lineobj.line)
                    lineobj = line_types.comment_line(lineobj.line)
            else:
                cur_option = None
                if isinstance(lineobj, line_types.section_line):
                    cur_section = self.sections.get(lineobj.name)
                    if cur_section is None:
                        cur_section = section()
                        self.sections[lineobj.name] = cur_section
            self.lines.append(lineobj)

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
