# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004-2008 Paramjit Oberoi <param.cs.wisc.edu>
# Copyright (c) 2007 Tim Lauridsen <tla@rasmil.dk>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

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
