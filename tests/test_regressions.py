"""
:component: python-iniparse
:requirement: RHSS-291606
:polarion-project-id: RHELSS
:polarion-include-skipped: false
:polarion-lookup-method: id
:poolteam: rhel-sst-csi-client-tools
:caseautomation: Automated
:upstream: No
"""

import unittest
from io import StringIO

from iniparse import compat


class TestCompatSkipEmptyLines(unittest.TestCase):
    def test_not_shared_between_instances(self):
        """
        :id: fce0ac15-8871-4af4-8017-5f37cbc905b0
        :title: Empty-line skipping state is not shared between parsers
        :description:
            Verifies that the per-option "skip empty lines" compatibility
            state of one parser is not modified by operations performed
            on another, unrelated parser.
        :tags: Tier 1
        :steps:
            1. Parse a multi-line value containing an empty line with parser A.
            2. Set an option with the same name in parser B.
            3. Set a multi-line value in parser C, then parse a file with
               parser D that has a same-named multi-line option.
        :expectedresults:
            1. Parser A returns the value without the empty line.
            2. Parser A still returns the value without the empty line.
            3. Parser C still returns its value with the empty line kept.
        """
        a = compat.RawConfigParser()
        a.readfp(StringIO('[a]\nfoo = line1\n\n  line2\n'))
        self.assertEqual(a.get('a', 'foo'), 'line1\nline2')

        b = compat.RawConfigParser()
        b.add_section('b')
        b.set('b', 'foo', 'x')
        self.assertEqual(a.get('a', 'foo'), 'line1\nline2')

        c = compat.RawConfigParser()
        c.add_section('c')
        c.set('c', 'bar', 'x\n\ny')
        d = compat.RawConfigParser()
        d.readfp(StringIO('[d]\nbar = 1\n\n  2\n'))
        self.assertEqual(c.get('c', 'bar'), 'x\n\ny')
        self.assertEqual(d.get('d', 'bar'), '1\n2')
