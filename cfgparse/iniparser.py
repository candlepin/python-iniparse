# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import line_types

def print_warning(w):
    #print >>sys.stderr, 'Warning:', w
    pass

class line_container(object):
    def __init__(self):
        self.contents = []

    def add(self, x):
        self.contents.append(x)

    def extend(self, x):
        for i in x: self.add(i)

    def __str__(self):
        s = [str(x) for x in self.contents]
        return '\n'.join(s)

    def get(self, key):
        matches = []
        for x in self.contents[::-1]:
            if hasattr(x, 'name') and x.name==key:
                matches.append(x)

        if not matches:
            raise KeyError(key)
        elif len(matches) == 1:
            return matches[0]
        else:
            r = multiple_matches()
            r.contents.extend(matches)
            return r

class multiple_matches(line_container):
    def get(self, key):
        for x in self.contents:
            try:
                return x.get(key)
            except KeyError:
                pass
        raise KeyError(key)


class section(line_container):
    def __init__(self, lineobj):
        super(section, self).__init__()
        self.add(lineobj)
        self.name = lineobj.name

    def get(self, key):
        return super(section, self).get(key).value()

class option(line_container):
    def __init__(self, lineobj):
        super(option, self).__init__()
        self.add(lineobj)
        self.name = lineobj.name

    def value(self):
        return '\n'.join([x.value for x in self.contents])

def make_comment(line):
    print_warning('can\'t parse "%s"' % line)
    return line_types.comment_line(line.rstrip())

class inifile(line_container):
    def __init__(self, fobj=None):
        super(inifile, self).__init__()
        if fobj is not None:
            self.read(fobj)

    line_types = [line_types.empty_line,
                  line_types.comment_line,
                  line_types.section_line,
                  line_types.option_line,
                  line_types.continuation_line]

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

            if isinstance(lineobj, line_types.continuation_line):
                if cur_option:
                    cur_option.add(lineobj)
                else:
                    # illegal continuation line - convert to comment
                    lineobj = make_comment(line)
            else:
                cur_option = None

            if isinstance(lineobj, line_types.option_line):
                if cur_section:
                    cur_section.extend(pending_lines)
                    pending_lines = []
                    cur_option = option(lineobj)
                    cur_section.add(cur_option)
                else:
                    # illegal option line - convert to comment
                    lineobj = make_comment(line)

            if isinstance(lineobj, line_types.section_line):
                self.extend(pending_lines)
                pending_lines = []
                cur_section = section(lineobj)
                self.add(cur_section)

            if isinstance(lineobj, (line_types.comment_line, line_types.empty_line)):
                pending_lines.append(lineobj)

        self.extend(pending_lines)
        if line and line[-1]=='\n':
            self.add(line_types.empty_line())


#class getter(object):
#    def __init__(self, obj):
#        self.obj = obj
#
#    def __getattr__(self, name):
#        value = self.obj.get(name)
#        if hasattr(value, 'get'):
#            return getter(value)
#        else:
#            return value
#
#class section(object):
#    def __init__(self):
#        self.options = {}
#
#    # keeping copy of name---if the name is
#    # modified, the dict must be a well
#    def add_option(self, opt):
#        self.options[opt.name] = opt
#
#    def get(self, opt):
#        return self.options[opt].value
#
#    def __getitem__(self, key):
#        if key in self.options:
#            return self.options[key].value
#        else:
#            raise IndexError, '%s not found' % key
#
#class option(object):
#    def __init__(self, lineobj, cur_section):
#        self.lines = [lineobj]
#        self.section = cur_section
#        self.name = lineobj.option
#        self.value = lineobj.value
#
#    def add_line(self,lineobj):
#        self.lines.append(lineobj)
#        self.value += "\n%s" % lineobj.value
#
#
#class iniparser(object):
#    line_types = [line_types.empty_line,
#                  line_types.comment_line,
#                  line_types.section_line,
#                  line_types.option_line,
#                  line_types.continuation_line]
#
#    def __init__(self, f=None):
#        self.lines = []
#        self.sections = {'DEFAULT' : section()}
#        self.options = getter(self)
#        if f is not None:
#            self.read_file(f)
#
#    def parse(self, line):
#        for linetype in self.line_types:
#            lineobj = linetype.parse(line)
#            if lineobj:
#                return lineobj
#        else:
#            # can't parse line - convert to comment
#            print_warning('can\'t parse "%s"' % line)
#            return line_types.comment_line(line)
#
#    def read_file(self, f):
#        cur_section = self.sections['DEFAULT']
#        cur_option = None
#        for line in f:
#            lineobj = self.parse(line)
#            if isinstance(lineobj, line_types.option_line):
#                cur_option = option(lineobj, cur_section)
#                cur_section.add_option(cur_option)
#            elif isinstance(lineobj, line_types.continuation_line):
#                if cur_option:
#                    cur_option.add_line(lineobj)
#                else:
#                    # illegal continuation line - convert to comment
#                    print_warning('can\'t parse: "%s"' % lineobj.line)
#                    lineobj = line_types.comment_line(lineobj.line)
#            else:
#                cur_option = None
#                if isinstance(lineobj, line_types.section_line):
#                    cur_section = self.sections.get(lineobj.name)
#                    if cur_section is None:
#                        cur_section = section()
#                        self.sections[lineobj.name] = cur_section
#            self.lines.append(lineobj)
#
#    def write_file(self, f):
#        for lineobj in self.lines:
#            f.write(str(lineobj))
#            f.write('\n')
#
#    def __str__(self):
#        s = StringIO.StringIO()
#        self.write_file(s)
#        return s.getvalue()
#
#    def get(self, secname):
#        return self.sections[secname]
#
#    def __getitem__(self, key):
#        if key in self.sections:
#            return self.sections[key]
#        else:
#            raise IndexError, '%s not found' % key
