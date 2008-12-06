import unittest, doctest

import test_ini
import test_misc
import test_compat
import test_unicode
from iniparse import config
from iniparse import ini

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                doctest.DocTestSuite(config),
                doctest.DocTestSuite(ini),
                test_ini.suite(),
                test_misc.suite(),
                test_compat.suite(),
                test_unicode.suite(),
        ])
