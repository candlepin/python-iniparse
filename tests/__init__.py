import unittest, doctest

import test_iniparser
from cfgparse import config

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                doctest.DocTestSuite(config),
                test_iniparser.suite(),
        ])
