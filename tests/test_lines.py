import unittest
from cfgparse import line_types

class test_section_line(unittest.TestCase):
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
            p = line_types.section_line.parse(l)
            self.assertEqual(p, None)

    lines = [
        ('[section]' ,          ('section', None, None, -1)),
        ('[se\ct%[ion\t]' ,     ('se\ct%[ion\t', None, None, -1)),
        ('[sec tion]  ; hi' ,   ('sec tion', ' hi', ';', 12)),
        ('[section]  #oops!' ,  ('section', 'oops!', '#', 11)),
        ('[section]   ;  ' ,    ('section', '', ';', 12)),
        ('[section]      ' ,    ('section', None, None, -1)),
    ]
    def test_parsing(self):
        for l in self.lines:
            p = line_types.section_line.parse(l[0])
            self.assertNotEqual(p, None)
            self.assertEqual(p.name, l[1][0])
            self.assertEqual(p.comment, l[1][1])
            self.assertEqual(p.comment_separator, l[1][2])
            self.assertEqual(p.comment_offset, l[1][3])

    def test_printing(self):
        for l in self.lines:
            p = line_types.section_line.parse(l[0])
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
            p = line_types.section_line.parse(l[0])
            p.name = l[1]
            self.assertEqual(str(p), l[2])

class test_option_line(unittest.TestCase):
    lines = [
        ('option = value', 'option', '=', 'value', None, None, -1),
        ('option:   value', 'option', ':', 'value', None, None, -1),
        ('option=value', 'option', '=', 'value', None, None, -1),
        ('op[ti]on=value', 'op[ti]on', '=', 'value', None, None, -1),

        ('option = value # no comment', 'option', '=', 'value # no comment',
                                         None, None, -1),
        ('option = value     ;', 'option', '=', 'value',
                                         ';', '', 19),
        ('option = value     ; comment', 'option', '=', 'value',
                                         ';', ' comment', 19),
        ('option = value;1   ; comment', 'option', '=', 'value;1   ; comment',
                                         None, None, -1),
        ('op;ti on = value      ;; comm;ent', 'op;ti on', '=', 'value',
                                         ';', '; comm;ent', 22),
    ]
    def test_parsing(self):
        for l in self.lines:
            p = line_types.option_line.parse(l[0])
            self.assertEqual(p.option, l[1])
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
            p = line_types.option_line.parse(l)
            self.assertEqual(p, None)

    print_lines = [
        ('option = value',
         'option = value'),
        ('option= value',
         'option = value'),
        ('option : value',
         'option : value'),
        ('option: value  ',
         'option : value'),
        ('option   =    value  ',
         'option = value'),
        ('option = value   ;',
         'option = value   ;'),
        ('option = value;2    ;; 4 5',
         'option = value;2    ;; 4 5'),
        ('option = value     ; hi!',
         'option = value     ; hi!'),
    ]
    def test_printing(self):
        for l in self.print_lines:
            p = line_types.option_line.parse(l[0])
            self.assertEqual(str(p), l[0])
            self.assertEqual(p.to_string(), l[1])

    indent_test_lines = [
        ('option = value   ;comment', 'newoption', 'newval',
         'newoption = newval ;comment'),
        ('option = value       ;comment', 'newoption', 'newval',
         'newoption = newval   ;comment'),
    ]
    def test_preserve_indentation(self):
        for l in self.indent_test_lines:
            p = line_types.option_line.parse(l[0])
            p.option = l[1]
            p.value = l[2]
            self.assertEqual(str(p), l[3])

class test_comment_line(unittest.TestCase):
    invalid_lines = [
        '[section]',
        'option = value ;comment',
        '  # must start on first column',
    ]
    def test_invalid(self):
        for l in self.invalid_lines:
            p = line_types.comment_line.parse(l)
            self.assertEqual(p, None)

    lines = [
        '#this is a comment',
        ';; this is also a comment',
        '; so is this   ',
        'Rem and this',
        'remthis too!'
    ]
    def test_parsing(self):
        for l in self.lines:
            p = line_types.comment_line.parse(l)
            self.assertEqual(str(p), l)
            self.assertEqual(p.to_string(), l.rstrip())

class test_other_lines(unittest.TestCase):
    def test_empty(self):
        for s in ['asdf', '; hi', '  #rr', '[sec]', 'opt=val']:
            self.assertEqual(line_types.empty_line.parse(s), None)
        for s in ['', '  ', '\t  \t']:
            self.assertEqual(str(line_types.empty_line.parse(s)), s)

    def test_continuation(self):
        pass

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_section_line, 'test'),
                unittest.makeSuite(test_option_line, 'test'),
                unittest.makeSuite(test_comment_line, 'test'),
                unittest.makeSuite(test_other_lines, 'test'),
        ])
