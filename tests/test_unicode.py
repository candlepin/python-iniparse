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
from iniparse import ini


class TestUnicode(unittest.TestCase):
    """Test files read in unicode-mode."""

    s1 = u"""\
[foo]
bar = fish
    """

    s2 = u"""\
\ufeff[foo]
bar = mammal
baz = Marc-Andr\202
    """

    def basic_tests(self, s, strable):
        f = StringIO(s)
        i = ini.INIConfig(f)
        self.assertEqual(str(i), s)
        self.assertEqual(type(i.foo.bar), str)
        if strable:
            self.assertEqual(str(i), str(s))
        else:
            self.assertRaises(UnicodeEncodeError, lambda: str(i).encode('ascii'))
        return i

    def test_ascii(self):
        """
        :id: 3d55663a-6c1d-4cf9-920e-875b183be39f
        :title: ASCII input is parsed and serialized correctly
        :description:
            Verifies that standard ASCII INI strings are parsed successfully
            and that all values are retrievable and printable using `str()`
            without encoding issues.
        :tags: Tier 1
        :steps:
            1. Create an INI string containing only ASCII characters.
            2. Parse the string using `INIConfig`.
            3. Retrieve a known value from the config.
            4. Convert the config back to a string using `str()`.
        :expectedresults:
            1. The INI string is parsed without errors.
            2. The expected value is retrieved correctly.
            3. Serialization works with `str()` and returns valid ASCII.
        """
        i = self.basic_tests(self.s1, strable=True)
        self.assertEqual(i.foo.bar, 'fish')

    def test_unicode_without_bom(self):
        """
        :id: 963a6e17-262e-4c85-9baf-7e2d9a88f92d
        :title: Unicode INI input without BOM is parsed correctly
        :description:
            Verifies that Unicode input without a Byte Order Mark (BOM) is parsed
            correctly and values with special characters are accessible, even if
            not ASCII-encodable.
        :tags: Tier 2
        :steps:
            1. Create a Unicode INI string with non-ASCII characters, excluding BOM.
            2. Parse the string using `INIConfig`.
            3. Retrieve both values, including one with a non-ASCII byte (`\202`).
            4. Attempt to serialize the config with `str().encode("ascii")` and
                expect failure.
        :expectedresults:
            1. Input string is parsed successfully.
            2. All values are retrievable.
            3. Non-ASCII characters are preserved.
            4. Encoding to ASCII raises `UnicodeEncodeError`.
        """
        i = self.basic_tests(self.s2[1:], strable=False)
        self.assertEqual(i.foo.bar, 'mammal')
        self.assertEqual(i.foo.baz, u'Marc-Andr\202')

    def test_unicode_with_bom(self):
        """
        :id: b0eabc52-bb35-41c7-bb7c-cc7c5479c964
        :title: Unicode INI input with BOM is parsed correctly
        :description:
            Ensures that Unicode strings containing a BOM (`\ufeff`) are parsed
            without error and values with extended characters are preserved
            in the configuration object.
        :tags: Tier 2
        :steps:
            1. Create a Unicode INI string that includes a BOM and non-ASCII
                characters.
            2. Parse the string using `INIConfig`.
            3. Retrieve both options and verify values.
            4. Attempt to serialize with `str().encode("ascii")` and expect
                a `UnicodeEncodeError`.
        :expectedresults:
            1. Input with BOM is parsed successfully.
            2. Both values are correctly accessible from the config.
            3. Unicode characters are preserved.
            4. ASCII encoding fails with `UnicodeEncodeError`.
        """
        i = self.basic_tests(self.s2, strable=False)
        self.assertEqual(i.foo.bar, 'mammal')
        self.assertEqual(i.foo.baz, u'Marc-Andr\202')
