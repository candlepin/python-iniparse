import unittest

import test_config
import test_lines
import test_iniparser

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                test_config.suite,
                test_lines.suite(),
                test_iniparser.suite(),
        ])
