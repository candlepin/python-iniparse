#!/usr/bin/env python

import sys, unittest, unittestgui
import tests

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-g':
        unittestgui.main('tests.suite')
    else:
        unittest.main(defaultTest='tests.suite')
