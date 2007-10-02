import unittest
from StringIO import StringIO
from iniparse import compat, ini

class CaseSensitiveConfigParser(compat.ConfigParser):
    """Case Sensitive version of ConfigParser"""
    def optionxform(self, option):
        """Use str()"""
        return str(option)

class test_optionxform_override(unittest.TestCase):
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

class test_readline(unittest.TestCase):
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
            c.readfp(fp)
            self.assertEqual(s, str(c))

    def test_readline_configparser(self):
        for s in self.test_strings:
            fp = OnlyReadline(s)
            c = compat.ConfigParser()
            c.readfp(fp)
            ss = StringIO()
            c.write(ss)
            self.assertEqual(s, ss.getvalue())


class test_multiline_with_comments(unittest.TestCase):
    """Test that multiline values are allowed to span comments."""

    s = """\
[sec]
opt = 1
 2

# comment
 3"""

    def test_read(self):
        c = ini.INIConfig()
        c.readfp(StringIO(self.s))
        self.assertEqual(c.sec.opt, '1\n2\n3')

    def test_write(self):
        c = ini.INIConfig()
        c.readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")

class test_empty_file(unittest.TestCase):
    """Test if it works with an blank file"""

    s = ""
    
    def test_read(self):
        c = ini.INIConfig()
        c.readfp(StringIO(self.s))
        self.assertEqual(str(c), '')

    def test_write(self):
        c = ini.INIConfig()
        c.readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")


class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_optionxform_override, 'test'),
                unittest.makeSuite(test_readline, 'test'),
                unittest.makeSuite(test_multiline_with_comments, 'test'),
                unittest.makeSuite(test_empty_file, 'test'),
    ])