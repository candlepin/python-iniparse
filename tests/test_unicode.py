import unittest
from io import StringIO
from iniparse import ini


class TestUnicode(unittest.TestCase):
    """Test files read in unicode-mode."""

    s1 = u"""\
[foo]
bar = fish
    """

    s2 = u"""\
\ufeff[foo]
bar = mammal
baz = Marc-Andr\202
    """

    def basic_tests(self, s, strable):
        f = StringIO(s)
        i = ini.INIConfig(f)
        self.assertEqual(str(i), s)
        self.assertEqual(type(i.foo.bar), str)
        if strable:
            self.assertEqual(str(i), str(s))
        else:
            self.assertRaises(UnicodeEncodeError, lambda: str(i).encode('ascii'))
        return i

    def test_ascii(self):
        i = self.basic_tests(self.s1, strable=True)
        self.assertEqual(i.foo.bar, 'fish')

    def test_unicode_without_bom(self):
        i = self.basic_tests(self.s2[1:], strable=False)
        self.assertEqual(i.foo.bar, 'mammal')
        self.assertEqual(i.foo.baz, u'Marc-Andr\202')

    def test_unicode_with_bom(self):
        i = self.basic_tests(self.s2, strable=False)
        self.assertEqual(i.foo.bar, 'mammal')
        self.assertEqual(i.foo.baz, u'Marc-Andr\202')
