import unittest
from iniparse import compat

class CaseSensitiveConfigParser(compat.ConfigParser):
    """Case Sensitive version of ConfigParser"""
    def optionxform(self, option):
        """Use str()"""
        return str(option)

class test_optionxform_override(unittest.TestCase):
    def test_case_sensitive(self):
        c = CaseSensitiveConfigParser()
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        self.assertEqual(c.get('foo', 'bar'), 'a')
        self.assertEqual(c.get('foo', 'Bar'), 'b')
    
class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                unittest.makeSuite(test_optionxform_override, 'test'),
    ])