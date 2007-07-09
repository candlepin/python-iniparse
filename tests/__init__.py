# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

import unittest, doctest

import test_iniparser
import test_compat
from cfgparse import config
from cfgparse import iniparser

class suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                doctest.DocTestSuite(config),
                doctest.DocTestSuite(iniparser),
                test_iniparser.suite(),
                test_compat.suite(),
        ])
