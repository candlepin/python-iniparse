import unittest
from StringIO import StringIO
from cfgparse import iniparser

class test_iniparser(unittest.TestCase):
    s1 = """
[section1]
help = me
I'm  = desperate     ; really!

[section2]
just = kidding
"""

    def test_basic(self):
        sio = StringIO(self.s1)
        p = iniparser.iniparser(sio)
        self.assertEqual(str(p), self.s1)
        self.assertEqual(p.get('section2').get('just'), 'kidding')
        self.assertEqual(p.get('section1').get('help'), 'me')
        self.assertEqual(p.get('section1').get('I\'m'), 'desperate')
        self.assertEqual(p['section2']['just'], 'kidding')
        self.assertEqual(p.options.section2.just, 'kidding')

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_iniparser, 'test'),
        ])
