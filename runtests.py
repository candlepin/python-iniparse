#!/usr/bin/env python

import doctest
import os
import unittest

from iniparse import config
from iniparse import ini


def load_tests(loader, tests, pattern):
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")
    package_tests = loader.discover(start_dir=tests_dir)
    tests.addTests(package_tests)
    tests.addTests((doctest.DocTestSuite(config), doctest.DocTestSuite(ini)))
    return tests


if __name__ == '__main__':
    unittest.main()
