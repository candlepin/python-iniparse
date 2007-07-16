# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

import unittest, doctest

import test_ini
import test_misc
import test_compat
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
        ])
