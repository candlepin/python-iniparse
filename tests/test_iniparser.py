import unittest
from StringIO import StringIO
from cfgparse.iniparser import inifile

class test_iniparser(unittest.TestCase):
    s1 = """
[section1]
help = me
I'm  = desperate     ; really!

[section2]
just = what?
just = kidding

[section1]
help = yourself
but = also me
"""

    def test_basic(self):
        sio = StringIO(self.s1)
        p = inifile(sio)
        self.assertEqual(str(p), self.s1)
        self.assertEqual(p.get('section2').get('just'), 'kidding')
        self.assertEqual(p.get('section1').get('help'), 'yourself')
        self.assertEqual(p.get('section1').get('I\'m'), 'desperate')
        self.assertEqual(p.get('section2').get('just'), 'kidding')

        self.assertRaises(KeyError, p.get, 'section')
        self.assertRaises(KeyError, p.get('section2').get, 'ahem')

        #self.assertEqual(p.options.section2.just, 'kidding')

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

#    yuiop
op3 = qwert
# yup
#    yuiop

[another section]
#    hmmm
"""))

    def test_invalid(self):
        for (org, mod) in self.inv:
            self.assertEqual(str(inifile(StringIO(org))), mod)

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_iniparser, 'test'),
        ])
