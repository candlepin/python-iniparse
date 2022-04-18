import unittest
from six import StringIO

from iniparse import ini
from iniparse import compat
from iniparse import config


class TestSectionLine(unittest.TestCase):
    invalid_lines = [
        '# this is a comment',
        '; this is a comment',
        '  [sections must start on column1]',
        '[incomplete',
        '[ no closing ]brackets]',
        'ice-cream = mmmm',
        'ic[e-c]ream = mmmm',
        '[ice-cream] = mmmm',
        '-$%^',
    ]

    def test_invalid(self):
        for l in self.invalid_lines:
            p = ini.SectionLine.parse(l)
            self.assertEqual(p, None)

    lines = [
        ('[section]',          ('section', None, None, -1)),
        ('[se\ct%[ion\t]',     ('se\ct%[ion\t', None, None, -1)),
        ('[sec tion]  ; hi',   ('sec tion', ' hi', ';', 12)),
        ('[section]  #oops!',  ('section', 'oops!', '#', 11)),
        ('[section]   ;  ',    ('section', '', ';', 12)),
        ('[section]      ',    ('section', None, None, -1)),
    ]

    def test_parsing(self):
        for l in self.lines:
            p = ini.SectionLine.parse(l[0])
            self.assertNotEqual(p, None)
            self.assertEqual(p.name, l[1][0])
            self.assertEqual(p.comment, l[1][1])
            self.assertEqual(p.comment_separator, l[1][2])
            self.assertEqual(p.comment_offset, l[1][3])

    def test_printing(self):
        for l in self.lines:
            p = ini.SectionLine.parse(l[0])
            self.assertEqual(str(p), l[0])
            self.assertEqual(p.to_string(), l[0].strip())

    indent_test_lines = [
        ('[oldname]             ; comment', 'long new name',
         '[long new name]       ; comment'),
        ('[oldname]             ; comment', 'short',
         '[short]               ; comment'),
        ('[oldname]             ; comment', 'really long new name',
         '[really long new name] ; comment'),
    ]

    def test_preserve_indentation(self):
        for l in self.indent_test_lines:
            p = ini.SectionLine.parse(l[0])
            p.name = l[1]
            self.assertEqual(str(p), l[2])


class TestOptionLine(unittest.TestCase):
    lines = [
        ('option = value', 'option', ' = ', 'value', None, None, -1),
        ('option:   value', 'option', ':   ', 'value', None, None, -1),
        ('option=value', 'option', '=', 'value', None, None, -1),
        ('op[ti]on=value', 'op[ti]on', '=', 'value', None, None, -1),

        ('option = value # no comment', 'option', ' = ', 'value # no comment',
                                         None, None, -1),
        ('option = value     ;', 'option', ' = ', 'value',
                                         ';', '', 19),
        ('option = value     ; comment', 'option', ' = ', 'value',
                                         ';', ' comment', 19),
        ('option = value;1   ; comment', 'option', ' = ', 'value;1   ; comment',
                                         None, None, -1),
        ('op;ti on = value      ;; comm;ent', 'op;ti on', ' = ', 'value',
                                         ';', '; comm;ent', 22),
    ]
    def test_parsing(self):
        for l in self.lines:
            p = ini.OptionLine.parse(l[0])
            self.assertEqual(p.name, l[1])
            self.assertEqual(p.separator, l[2])
            self.assertEqual(p.value, l[3])
            self.assertEqual(p.comment_separator, l[4])
            self.assertEqual(p.comment, l[5])
            self.assertEqual(p.comment_offset, l[6])

    invalid_lines = [
        '  option = value',
        '# comment',
        '; comment',
        '[section 7]',
        '[section=option]',
        'option',
    ]

    def test_invalid(self):
        for l in self.invalid_lines:
            p = ini.OptionLine.parse(l)
            self.assertEqual(p, None)

    print_lines = [
        'option = value',
        'option= value',
        'option : value',
        'option: value  ',
        'option   =    value  ',
        'option = value   ;',
        'option = value;2    ;; 4 5',
        'option = value     ; hi!',
    ]

    def test_printing(self):
        for l in self.print_lines:
            p = ini.OptionLine.parse(l)
            self.assertEqual(str(p), l)
            self.assertEqual(p.to_string(), l.rstrip())

    indent_test_lines = [
        ('option = value   ;comment', 'newoption', 'newval',
         'newoption = newval ;comment'),
        ('option = value       ;comment', 'newoption', 'newval',
         'newoption = newval   ;comment'),
    ]

    def test_preserve_indentation(self):
        for l in self.indent_test_lines:
            p = ini.OptionLine.parse(l[0])
            p.name = l[1]
            p.value = l[2]
            self.assertEqual(str(p), l[3])


class TestCommentLine(unittest.TestCase):
    invalid_lines = [
        '[section]',
        'option = value ;comment',
        '  # must start on first column',
    ]

    def test_invalid(self):
        for l in self.invalid_lines:
            p = ini.CommentLine.parse(l)
            self.assertEqual(p, None)

    lines = [
        '#this is a comment',
        ';; this is also a comment',
        '; so is this   ',
        'Rem and this'
    ]

    def test_parsing(self):
        for l in self.lines:
            p = ini.CommentLine.parse(l)
            self.assertEqual(str(p), l)
            self.assertEqual(p.to_string(), l.rstrip())


class TestOtherLines(unittest.TestCase):
    def test_empty(self):
        for s in ['asdf', '; hi', '  #rr', '[sec]', 'opt=val']:
            self.assertEqual(ini.EmptyLine.parse(s), None)
        for s in ['', '  ', '\t  \t']:
            self.assertEqual(str(ini.EmptyLine.parse(s)), s)

    def test_continuation(self):
        for s in ['asdf', '; hi', '[sec]', 'a=3']:
            self.assertEqual(ini.ContinuationLine.parse(s), None)
        for s in [' asdfasd ', '\t mmmm']:
            self.assertEqual(ini.ContinuationLine.parse(s).value,
                             s.strip())
            self.assertEqual(ini.ContinuationLine.parse(s).to_string(),
                             s.rstrip().replace('\t',' '))


class TestIni(unittest.TestCase):
    s1 = """
[section1]
help = me
I'm  = desperate     ; really!

[section2]
# comment and empty line before the first option

just = what?
just = kidding

[section1]
help = yourself
but = also me
"""

    def test_basic(self):
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        section1_but = p._data.find('section1').find('but')
        self.assertEqual(section1_but.value, 'also me')
        self.assertEqual(section1_but.line_number, 14)
        section1_help = p._data.find('section1').find('help')
        self.assertEqual(section1_help.value, 'yourself')
        self.assertEqual(section1_help.line_number, 13)
        section2_just = p._data.find('section2').find('just')
        self.assertEqual(section2_just.value, 'kidding')
        self.assertEqual(section2_just.line_number, 10)

        itr = p._data.finditer('section1')
        v = next(itr)
        self.assertEqual(v.find('help').value, 'yourself')
        self.assertEqual(v.find('but').value, 'also me')
        v = next(itr)
        self.assertEqual(v.find('help').value, 'me')
        self.assertEqual(v.find('I\'m').value, 'desperate')
        self.assertRaises(StopIteration, next, itr)

        self.assertRaises(KeyError, p._data.find, 'section')
        self.assertRaises(KeyError, p._data.find('section2').find, 'ahem')

    def test_lookup(self):
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        self.assertEqual(p.section1.help, 'yourself')
        self.assertEqual(p.section1.but, 'also me')
        self.assertEqual(getattr(p.section1, 'I\'m'), 'desperate')
        self.assertEqual(p.section2.just, 'kidding')

        self.assertEqual(p.section1.just.__class__, config.Undefined)
        self.assertEqual(p.section2.help.__class__, config.Undefined)

    def test_newsection(self):
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        p.new1.created = 1
        setattr(getattr(p, 'new2'), 'created', 1)
        p.new3['created'] = 1
        p['new4'].created = 1
        p['new5']['created'] = 1
        self.assertEqual(p.new1.created, 1)
        self.assertEqual(p.new2.created, 1)
        self.assertEqual(p.new3.created, 1)
        self.assertEqual(p.new4.created, 1)
        self.assertEqual(p.new5.created, 1)

    def test_order(self):
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        self.assertEqual(list(p), ['section1','section2'])
        self.assertEqual(list(p.section1), ['help', "i'm", 'but'])
        self.assertEqual(list(p.section2), ['just'])

    def test_delete(self):
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        del p.section1.help
        self.assertEqual(list(p.section1), ["i'm", 'but'])
        self.assertEqual(str(p), """
[section1]
I'm  = desperate     ; really!

[section2]
# comment and empty line before the first option

just = what?
just = kidding

[section1]
but = also me
""")
        del p.section2
        self.assertEqual(str(p), """
[section1]
I'm  = desperate     ; really!


[section1]
but = also me
""")

    def check_order(self, c):
        sio = StringIO(self.s1)
        c = c({'pi':'3.14153'})
        c.readfp(sio)
        self.assertEqual(c.sections(), ['section1','section2'])
        self.assertEqual(c.options('section1'), ['help', "i'm", 'but', 'pi'])
        self.assertEqual(c.items('section1'), [
            ('help', 'yourself'),
            ("i'm", 'desperate'),
            ('but', 'also me'),
            ('pi', '3.14153'),
        ])

    def test_compat_order(self):
        self.check_order(compat.RawConfigParser)
        self.check_order(compat.ConfigParser)

    inv = (
("""
# values must be in a section
value = 5
""",
"""
# values must be in a section
#value = 5
"""),
("""
# continuation lines only allowed after options
[section]
op1 = qwert
    yuiop
op2 = qwert

    yuiop
op3 = qwert
# yup
    yuiop

[another section]
    hmmm
""",
"""
# continuation lines only allowed after options
[section]
op1 = qwert
    yuiop
op2 = qwert

    yuiop
op3 = qwert
# yup
    yuiop

[another section]
#    hmmm
"""))

    def test_invalid(self):
        for (org, mod) in self.inv:
            ip = ini.INIConfig(StringIO(org), parse_exc=False)
            self.assertEqual(str(ip), mod)

    # test multi-line values
    s2 = (
"""
[section]
option =
  foo
  bar

  baz
  yam
"""
)

    s3 = (
"""
[section]
option =
  foo
  bar
  mum

  baz
  yam
"""
)

    def test_option_continuation(self):
        ip = ini.INIConfig(StringIO(self.s2))
        self.assertEqual(str(ip), self.s2)
        value = ip.section.option.split('\n')
        value.insert(3, 'mum')
        ip.section.option = '\n'.join(value)
        self.assertEqual(str(ip), self.s3)

    s5 = (
"""
[section]
option =
  foo
  bar
"""
)

    s6 = (
"""
[section]
option =


  foo



another = baz
"""
)

    def test_option_continuation_single(self):
        ip = ini.INIConfig(StringIO(self.s5))
        self.assertEqual(str(ip), self.s5)
        ip.section.option = '\n'.join(['', '', '', 'foo', '', '', ''])
        ip.section.another = 'baz'
        self.assertEqual(str(ip), self.s6)


class Suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(TestSectionLine, 'test'),
                unittest.makeSuite(TestOptionLine, 'test'),
                unittest.makeSuite(TestCommentLine, 'test'),
                unittest.makeSuite(TestOtherLines, 'test'),
                unittest.makeSuite(TestIni, 'test'),
        ])
