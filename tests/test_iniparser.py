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
        self.assertEqual(p.get('section1').get('but'), 'also me')
        self.assertEqual(p.get('section1').get('help'), 'yourself')
        self.assertEqual(p.get('section2').get('just'), 'kidding')

        itr = p.finditer('section1')
        v = itr.next()
        self.assertEqual(v.get('help'), 'yourself')
        self.assertEqual(v.get('but'), 'also me')
        v = itr.next()
        self.assertEqual(v.get('help'), 'me')
        self.assertEqual(v.get('I\'m'), 'desperate')
        self.assertRaises(StopIteration, itr.next)

        self.assertRaises(KeyError, p.get, 'section')
        self.assertRaises(KeyError, p.get('section2').get, 'ahem')

        self.assertEqual(p.lookup('section1.help'), 'yourself')
        self.assertEqual(p.lookup('section1.but'), 'also me')
        self.assertEqual(p.lookup('section1.I\'m'), 'desperate')
        self.assertEqual(p.lookup('section2.just'), 'kidding')

        self.assertRaises(KeyError, p.lookup, 'section1.just')
        self.assertRaises(KeyError, p.lookup, 'section2.help')

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
