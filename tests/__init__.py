import unittest, doctest

from . import test_ini
from . import test_misc
from . import test_fuzz
from . import test_compat
from . import test_unicode
from . import test_tidy
from . import test_multiprocessing
from iniparse import config
from iniparse import ini


class Suite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, [
                doctest.DocTestSuite(config),
                doctest.DocTestSuite(ini),
                test_ini.Suite(),
                test_misc.Suite(),
                test_fuzz.Suite(),
                test_compat.Suite(),
                test_unicode.Suite(),
                test_tidy.Suite(),
                test_multiprocessing.Suite(),
        ])
