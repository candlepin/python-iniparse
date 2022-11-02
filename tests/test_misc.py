import re
import unittest
import pickle
import configparser
from io import StringIO
from textwrap import dedent
from iniparse import compat, ini


class CaseSensitiveConfigParser(compat.ConfigParser):
    """Case Sensitive version of ConfigParser"""
    def optionxform(self, option):
        """Use str()"""
        return str(option)


class TestOptionxFormOverride(unittest.TestCase):
    def test_derivedclass(self):
        c = CaseSensitiveConfigParser()
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        self.assertEqual(c.get('foo', 'bar'), 'a')
        self.assertEqual(c.get('foo', 'Bar'), 'b')

    def test_assignment(self):
        c = compat.ConfigParser()
        c.optionxform = str
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        self.assertEqual(c.get('foo', 'bar'), 'a')
        self.assertEqual(c.get('foo', 'Bar'), 'b')

    def test_dyanamic(self):
        c = compat.ConfigParser()
        c.optionxform = str
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        c.set('foo', 'BAR', 'c')
        c.optionxform = str.upper
        self.assertEqual(c.get('foo', 'Bar'), 'c')
        c.optionxform = str.lower
        self.assertEqual(c.get('foo', 'Bar'), 'a')
        c.optionxform = str
        self.assertEqual(c.get('foo', 'Bar'), 'b')


class OnlyReadline:
    def __init__(self, s):
        self.sio = StringIO(s)

    def readline(self):
        return self.sio.readline()


class TestReadline(unittest.TestCase):
    """Test that the file object passed to readfp only needs to
    support the .readline() method.  As of Python-2.4.4, this is
    true of the standard librariy's ConfigParser, and so other
    code uses that to guide what is sufficiently file-like."""

    test_strings = [
"""\
[foo]
bar=7
baz=8""",
"""\
[foo]
bar=7
baz=8
""",
"""\
[foo]
bar=7
baz=8
    """]

    def test_readline_iniconfig(self):
        for s in self.test_strings:
            fp = OnlyReadline(s)
            c = ini.INIConfig()
            c._readfp(fp)
            self.assertEqual(s, str(c))

    def test_readline_configparser(self):
        for s in self.test_strings:
            fp = OnlyReadline(s)
            c = compat.ConfigParser()
            c.readfp(fp)
            ss = StringIO()
            c.write(ss)
            self.assertEqual(s, ss.getvalue())


class TestMultilineWithComments(unittest.TestCase):
    """Test that multiline values are allowed to span comments."""

    s = """\
[sec]
opt = 1
 2

# comment
 3"""

    def test_read(self):
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.assertEqual(c.sec.opt, '1\n2\n\n3')

    def test_write(self):
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")


class TestEmptyFile(unittest.TestCase):
    """Test if it works with an blank file"""

    s = ""

    def test_read(self):
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.assertEqual(str(c), '')

    def test_write(self):
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")


class TestCustomDict(unittest.TestCase):
    def test_custom_dict_not_supported(self):
        self.assertRaises(ValueError, compat.RawConfigParser, None, 'foo')


class TestCompat(unittest.TestCase):
    """Miscellaneous compatibility tests."""

    s = dedent("""\
        [DEFAULT]
        pi = 3.1415
        three = 3
        poet = e e

             cummings
        NH =
         live free

         or die

        [sec]
        opt = 6
        three = 3.0
        no-three = one
         two

         four
        longopt = foo
         bar

        # empty line should not be part of value
         baz

         bat

        """)

    def do_test(self, c):
        # default section is not acknowledged
        self.assertEqual(c.sections(), ['sec'])
        # options in the default section are merged with other sections
        self.assertEqual(sorted(c.options('sec')),
                         ['longopt', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])

        # empty lines are stripped from multi-line values
        self.assertEqual(c.get('sec', 'poet').split('\n'),
                         ['e e', 'cummings'])
        self.assertEqual(c.get('DEFAULT', 'poet').split('\n'),
                         ['e e', 'cummings'])
        self.assertEqual(c.get('sec', 'longopt').split('\n'),
                         ['foo', 'bar', 'baz', 'bat'])
        self.assertEqual(c.get('sec', 'NH').split('\n'),
                         ['', 'live free', 'or die'])

        # check that empy-line stripping happens on all access paths
        # defaults()
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        # items()
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('longopt', 'foo\nbar\nbaz\nbat'),
            ('nh', '\nlive free\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])

        # empty lines are preserved on explicitly set values
        c.set('sec', 'longopt', '\n'.join(['a', 'b', '', 'c', '', '', 'd']))
        c.set('DEFAULT', 'NH', '\nlive free\n\nor die')
        self.assertEqual(c.get('sec', 'longopt').split('\n'),
                         ['a', 'b', '', 'c', '', '', 'd'])
        self.assertEqual(c.get('sec', 'NH').split('\n'),
                         ['', 'live free', '', 'or die'])
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\n\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        # items()
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('longopt', 'a\nb\n\nc\n\n\nd'),
            ('nh', '\nlive free\n\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])

        # empty line special magic goes away after remove_option()
        self.assertEqual(c.get('sec', 'no-three').split('\n'),
                         ['one', 'two','four'])
        c.remove_option('sec', 'no-three')
        c.set('sec', 'no-three', 'q\n\nw')
        self.assertEqual(c.get('sec', 'no-three'), 'q\n\nw')
        c.remove_option('sec', 'no-three')

    def do_configparser_test(self, cfg_class):
        c = cfg_class()
        c.readfp(StringIO(self.s))
        self.do_test(c)
        o = StringIO()
        c.write(o)
        self.assertEqual(o.getvalue().split('\n'), [
            '[DEFAULT]',
            'poet = e e',
            '\tcummings',
            'nh = ',
            '\tlive free',
            '\t',
            '\tor die',
            'pi = 3.1415',
            'three = 3',
            '',
            '[sec]',
            'opt = 6',
            'longopt = a',
            '\tb',
            '\t',
            '\tc',
            '\t',
            '\t',
            '\td',
            'three = 3.0',
            '',
            ''])

    def test_py_rawcfg(self):
        self.do_configparser_test(configparser.RawConfigParser)

    def test_py_cfg(self):
        self.do_configparser_test(configparser.ConfigParser)

    def test_py_safecfg(self):
        self.do_configparser_test(configparser.SafeConfigParser)

    def do_compat_test(self, cfg_class):
        c = cfg_class()
        c.readfp(StringIO(self.s))
        self.do_test(c)
        o = StringIO()
        c.write(o)
        self.assertEqual(o.getvalue().split('\n'), [
            '[DEFAULT]',
            'pi = 3.1415',
            'three = 3',
            'poet = e e',
            '',
            '     cummings',
            'NH =',
            ' live free',
            '',
            ' or die',
            '',
            '[sec]',
            'opt = 6',
            'three = 3.0',
            'longopt = a',
            ' b',
            '',
            ' c',
            '',
            '',
            ' d',
            '',
            ''])

    def test_py_rawcfg(self):
        self.do_compat_test(compat.RawConfigParser)

    def test_py_cfg(self):
        self.do_compat_test(compat.ConfigParser)

    def test_py_safecfg(self):
        self.do_compat_test(compat.SafeConfigParser)


class TestPickle(unittest.TestCase):
    s = dedent("""\
        [DEFAULT]
        pi = 3.1415
        three = 3
        poet = e e

             cummings
        NH =
         live free

         or die

        [sec]
        opt = 6
        three = 3.0
        no-three = one
         two

         four

        james = bond
        """)

    def do_compat_checks(self, c):
        self.assertEqual(c.sections(), ['sec'])
        self.assertEqual(sorted(c.options('sec')),
                         ['james', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('james', 'bond'),
            ('nh', '\nlive free\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])
        self.do_ini_checks(c.data)

    def do_ini_checks(self, c):
        self.assertEqual(list(c), ['sec'])
        self.assertEqual(sorted(c['sec']), ['james', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])
        self.assertEqual(c._defaults['pi'], '3.1415')
        self.assertEqual(c.sec.opt, '6')
        self.assertEqual(c.sec.three, '3.0')
        self.assertEqual(c.sec['no-three'], 'one\ntwo\n\nfour')
        self.assertEqual(c.sec.james, 'bond')
        self.assertEqual(c.sec.pi, '3.1415')
        self.assertEqual(c.sec.poet, 'e e\n\ncummings')
        self.assertEqual(c.sec.NH, '\nlive free\n\nor die')
        self.assertEqual(str(c), self.s)

    def test_compat(self):
        for cfg_class in (compat.ConfigParser, compat.RawConfigParser, compat.SafeConfigParser):
            c = cfg_class()
            c.readfp(StringIO(self.s))
            self.do_compat_checks(c)
            for i in range(0, pickle.HIGHEST_PROTOCOL+1):
                p = pickle.dumps(c, protocol=i)
                c2 = pickle.loads(p)
                self.do_compat_checks(c2)

    def test_ini(self):
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.do_ini_checks(c)
        for i in range(0, pickle.HIGHEST_PROTOCOL+1):
            p = pickle.dumps(c, protocol=i)
            c2 = pickle.loads(p)
            self.do_ini_checks(c2)


class TestCommentSyntax(unittest.TestCase):
    """Test changing comment syntax with change_comment_syntax"""

    def test_regex(self):
        # original regular expression
        org_regex = re.compile(r'^(?P<csep>[;#]|[rR][eE][mM])(?P<comment>.*)$')
        ini.change_comment_syntax(';#', True)
        self.assertEqual(ini.CommentLine.regex, org_regex)
        
        # mercurial-safe comment line regex, as given by Steve Borho & Paul Lambert
        # bitbucket.org/tortoisehg/stable/src/tip/tortoisehg/hgtk/thgconfig.py#cl-1084
        # http://groups.google.com/group/iniparse-discuss/msg/b41a54aa185a9b7c
        hg_regex = re.compile(r'^(?P<csep>[%;#])(?P<comment>.*)$')
        ini.change_comment_syntax('%;#', False)
        self.assertEqual(ini.CommentLine.regex, hg_regex)

        # change_comment_syntax() defaults to hg regex
        ini.change_comment_syntax()
        self.assertEqual(ini.CommentLine.regex, hg_regex)

        # test escaping of special chars in pattern
        regex = re.compile(r'^(?P<csep>[;#\-\^[\]])(?P<comment>.*)$')
        ini.change_comment_syntax(';#-^[]')
        self.assertEqual(ini.CommentLine.regex, regex)

    def test_ignore_includes(self):
        ini.change_comment_syntax()
        cfg = ini.INIConfig(StringIO(dedent("""
            # This is a mercurial-style config
            % include foobar

            [ui]
            username = Firstname Lastname <a@b.c>
            """)))
        self.assertEqual(cfg.ui.username, 'Firstname Lastname <a@b.c>')
        self.assertEqual(str(cfg), dedent("""
            # This is a mercurial-style config
            % include foobar

            [ui]
            username = Firstname Lastname <a@b.c>
            """))

    def tearDown(self):
        ini.change_comment_syntax(';#', True)


class Suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(TestOptionxFormOverride, 'test'),
                unittest.makeSuite(TestReadline, 'test'),
                unittest.makeSuite(TestMultilineWithComments, 'test'),
                unittest.makeSuite(TestEmptyFile, 'test'),
                unittest.makeSuite(TestCustomDict, 'test'),
                unittest.makeSuite(TestCompat, 'test'),
                unittest.makeSuite(TestPickle, 'test'),
                unittest.makeSuite(TestCommentSyntax, 'test'),
    ])
