import unittest
from iniparse import compat

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
        
class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_optionxform_override, 'test'),
    ])