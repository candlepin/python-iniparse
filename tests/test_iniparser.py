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
        self.assertEqual(p.find('section1').find('but').value(), 'also me')
        self.assertEqual(p.find('section1').find('help').value(), 'yourself')
        self.assertEqual(p.find('section2').find('just').value(), 'kidding')

        itr = p.finditer('section1')
        v = itr.next()
        self.assertEqual(v.find('help').value(), 'yourself')
        self.assertEqual(v.find('but').value(), 'also me')
        v = itr.next()
        self.assertEqual(v.find('help').value(), 'me')
        self.assertEqual(v.find('I\'m').value(), 'desperate')
        self.assertRaises(StopIteration, itr.next)

        self.assertRaises(KeyError, p.find, 'section')
        self.assertRaises(KeyError, p.find('section2').find, 'ahem')

    def test_lookup(self):
        sio = StringIO(self.s1)
        p = inifile(sio)
        self.assertEqual(p.lookup('section1.help').value(), 'yourself')
        self.assertEqual(p.lookup('section1.but').value(), 'also me')
        self.assertEqual(p.lookup('section1.I\'m').value(), 'desperate')
        self.assertEqual(p.lookup('section2.just').value(), 'kidding')

        self.assertRaises(KeyError, p.lookup, 'section1.just')
        self.assertRaises(KeyError, p.lookup, 'section2.help')

    def test_options(self):
        sio = StringIO(self.s1)
        p = inifile(sio)
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
