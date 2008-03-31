import unittest
from StringIO import StringIO
from iniparse import compat, ini

class test_unicode(unittest.TestCase):
    s1 = u"""\
[foo]
bar = fish
    """

    s2 = u"""\
\ufeff[dolphin]
whale = mammal
    """

    def test_unicode(self):
        f = StringIO(self.s1)
        i = ini.INIConfig(f)
        self.assertEqual(i.foo.bar, "fish")

    def test_unicode_with_bom(self):
        f = StringIO(self.s2)
        i = ini.INIConfig(f)
        self.assertEqual(i.dolphin.whale, "mammal")


class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_unicode, 'test'),
    ])