import unittest

import test_lines
import test_iniparser

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                test_lines.suite(),
                test_iniparser.suite(),
        ])
