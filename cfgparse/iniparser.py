# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import config
import line_types

def print_warning(w):
    #print >>sys.stderr, 'Warning:', w
    pass

class line_container(object):
    def __init__(self, d=None):
        self.contents = []
        if d:
            if isinstance(d, list): self.extend(d)
            else: self.add(d)

    def get_name(self):
        return self.contents[0].name

    def get_value(self):
        if len(self.contents) == 1:
            return self.contents[0].value
        else:
            return '\n'.join([str(x.value) for x in self.contents])

    name = property(get_name)
    value = property(get_value)

    def add(self, x):
        self.contents.append(x)

    def extend(self, x):
        for i in x: self.add(i)

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
        obj = line_container(line_types.option_line(name, ''))
        self.lineobj.add(obj)
        self.options[name] = opt = option(obj)
        # we call opt.set() explicitly to avoid handling
        # the case of data having multiple lines
        opt.set(data)
        return opt

    def new_namespace(self, name):
        raise Exception('No sub-sections allowed', name)

    def rename(self, oldname, newname):
        raise NotImplementedError(oldname, newname)

    def delete(self, name):
        raise NotImplementedError(name)

    def get(self, name):
        return self.options[name]

    def iterkeys(self):
        return NotImplementedError()

class option(config.value):
    def __init__(self, lineobj):
        self.lineobj = lineobj

    def get(self):
        if len(self.lineobj.contents) == 1:
            return self.lineobj.contents[0].value
        else:
            return '\n'.join([str(x.value) for x in self.lineobj.contents])

    def set(self, data):
        lines = data.split('\n')
        linediff = len(lines) - len(self.lineobj.contents)
        if linediff > 0:
            for _ in range(linediff):
                self.lineobj.add(line_types.continuation_line(''))
        elif linediff < 0:
            self.lineobj.contents = self.lineobj.contents[:linediff]
        for i,v in enumerate(lines):
            self.lineobj.contents[i].value = v

def make_comment(line):
    print_warning('can\'t parse "%s"' % line)
    return line_types.comment_line(line.rstrip())

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
            self.data.add(line_types.empty_line())
        obj = line_container(line_types.section_line(name))
        self.data.add(obj)
        self.sections[name] = ns = section(obj)
        return ns

    def rename(self, oldname, newname):
        raise NotImplementedError(oldname, newname)

    def delete(self, name):
        raise NotImplementedError(name)

    def get(self, name):
        return self.sections[name]

    def iterkeys(self):
        return NotImplementedError()

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
                    cur_option = line_container(lineobj)
                    cur_section.add(cur_option)
                    self.sections[cur_section.name].\
                         options[cur_option.name] = option(cur_option)
                else:
                    # illegal option line - convert to comment
                    lineobj = make_comment(line)

            if isinstance(lineobj, line_types.section_line):
                self.data.extend(pending_lines)
                pending_lines = []
                cur_section = line_container(lineobj)
                self.data.add(cur_section)
                if not self.sections.has_key(cur_section.name):
                    self.sections[cur_section.name] = section(cur_section)
                else:
                    self.sections[cur_section.name].lineobj = cur_section

            if isinstance(lineobj, (line_types.comment_line, line_types.empty_line)):
                pending_lines.append(lineobj)

        self.data.extend(pending_lines)
        if line and line[-1]=='\n':
            self.data.add(line_types.empty_line())

