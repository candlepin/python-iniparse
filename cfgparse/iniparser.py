# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import re

__metaclass__ = type

class section_line:
    regex =  re.compile(r'^\['
                        r'(?P<name>[^]]+)'
                        r'\]\s*'
                        r'((?P<csep>;|#)(?P<comment>.*))?$')

    def __init__(self, name, comment=None,
                 comment_separator=None, comment_offset=-1):
        self.name = name
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def __str__(self):
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
                   m.group('csep'), m.start('csep'))
    parse = classmethod(parse)

class option_line:
    def __init__(self, option, value, separator='=', comment=None,
                 comment_separator=None, comment_offset=-1):
        self.option = option
        self.value = value
        self.separator = separator
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def __str__(self):
        out = '%s %s %s' % (self.option, self.separator, self.value)
        if self.comment is not None:
            # try to preserve indentation of comments
            out = (out+' ').ljust(self.comment_offset)
            out = out + self.comment_separator + self.comment
        return out

    regex = re.compile(r'^(?P<option>[^:=\s[][^:=]*)'
                       r'\s*(?P<sep>[:=])\s*'
                       r'(?P<value>.*)$')

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None

        option = m.group('option').rstrip()
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

        return cls(option, value, sep, comment, csep, coff)
    parse = classmethod(parse)

class comment_line:
    regex = re.compile(r'^(?P<csep>[;#]|[rR][eE][mM])'
                       r'(?P<comment>.*)$')

    def __init__(self, comment='', separator='#'):
        self.comment = comment
        self.separator = separator

    def __str__(self):
        return self.separator + self.comment

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('comment'), m.group('csep'))
    parse = classmethod(parse)

class empty_line:
    # could make this a singleton
    def __str__(self):
        return ''

    def parse(cls, line):
        if line.strip(): return None
        return cls()
    parse = classmethod(parse)

class continuation_line:
    pass
