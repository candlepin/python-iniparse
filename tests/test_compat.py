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

import os
from iniparse import compat as ConfigParser
from io import StringIO
try:
    import UserDict
except ImportError:
    import collections as UserDict
import unittest

from test import support as test_support


class SortedDict(UserDict.UserDict):
    def items(self):
        result = self.data.items()
        result.sort()
        return result

    def keys(self):
        result = self.data.keys()
        result.sort()
        return result

    def values(self):
        result = self.items()
        return [i[1] for i in result]

    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return iter(self.keys())

    __iter__ = iterkeys

    def itervalues(self):
        return iter(self.values())


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        if not hasattr(self, "config_class"):
            raise unittest.SkipTest("config_class not set")

    def newconfig(self, defaults=None):
        if defaults is None:
            self.cf = self.config_class()
        else:
            self.cf = self.config_class(defaults)
        return self.cf

    def fromstring(self, string, defaults=None):
        cf = self.newconfig(defaults)
        sio = StringIO(string)
        cf.readfp(sio)
        return cf

    def test_basic(self):
        """
        :id: 3c6e489a-8b8b-4f68-a799-fb4b4fe5a0a1
        :title: Basic INI parsing and retrieval
        :description:
            Tests parsing of multiple INI sections with various formatting styles,
            comments, spacing, and internationalized keys. Also tests option removal
            and error handling.
        :tags: Tier 1
        :steps:
            1. Load a configuration string containing multiple sections and options.
            2. Retrieve and sort the list of sections.
            3. Retrieve option values from multiple sections with various formatting.
            4. Remove an existing option and check that it no longer exists.
            5. Attempt to remove a non-existent option and expect a False return.
            6. Attempt to remove an option from a non-existent section and expect an exception.
        :expectedresults:
            1. Configuration is successfully loaded into a parser object.
            2. Section names match the expected list after sorting.
            3. All option values are correctly retrieved and match expected results.
            4. Existing option is successfully removed.
            5. Second removal attempt returns False, indicating option doesn't exist.
            6. Removing from a non-existent section raises NoSectionError.
        """
        cf = self.fromstring(
            "[Foo Bar]\n"
            "foo=bar\n"
            "[Spacey Bar]\n"
            "foo = bar\n"
            "[Commented Bar]\n"
            "foo: bar ; comment\n"
            "[Long Line]\n"
            "foo: this line is much, much longer than my editor\n"
            "   likes it.\n"
            "[Section\\with$weird%characters[\t]\n"
            "[Internationalized Stuff]\n"
            "foo[bg]: Bulgarian\n"
            "foo=Default\n"
            "foo[en]=English\n"
            "foo[de]=Deutsch\n"
            "[Spaces]\n"
            "key with spaces : value\n"
            "another with spaces = splat!\n"
            )
        L = cf.sections()
        L.sort()
        eq = self.assertEqual
        eq(L, [r'Commented Bar',
               r'Foo Bar',
               r'Internationalized Stuff',
               r'Long Line',
               r'Section\with$weird%characters[' '\t',
               r'Spaces',
               r'Spacey Bar',
               ])

        # The use of spaces in the section names serves as a
        # regression test for SourceForge bug #583248:
        # http://www.python.org/sf/583248
        eq(cf.get('Foo Bar', 'foo'), 'bar')
        eq(cf.get('Spacey Bar', 'foo'), 'bar')
        eq(cf.get('Commented Bar', 'foo'), 'bar')
        eq(cf.get('Spaces', 'key with spaces'), 'value')
        eq(cf.get('Spaces', 'another with spaces'), 'splat!')

        self.assertFalse('__name__' in cf.options("Foo Bar"),
                    '__name__ "option" should not be exposed by the API!')

        # Make sure the right things happen for remove_option();
        # added to include check for SourceForge bug #123324:
        self.assertTrue(cf.remove_option('Foo Bar', 'foo'),
                        "remove_option() failed to report existance of option")
        self.assertFalse(cf.has_option('Foo Bar', 'foo'),
                    "remove_option() failed to remove option")
        self.assertFalse(cf.remove_option('Foo Bar', 'foo'),
                    "remove_option() failed to report non-existance of option"
                    " that was removed")

        self.assertRaises(ConfigParser.NoSectionError,
                          cf.remove_option, 'No Such Section', 'foo')

        eq(cf.get('Long Line', 'foo'),
           'this line is much, much longer than my editor\nlikes it.')

    def test_case_sensitivity(self):
        """
        :id: e8ddc4a3-2c42-42fd-9436-27a64b1f7f5a
        :title: Test case sensitivity of section and option names
        :description:
            Verifies that section names are case-sensitive, while option names are
            case-insensitive.
        :tags: Tier 1
        :steps:
            1. Add two sections that differ only in case ("A" and "a").
            2. Set options using mixed-case keys.
            3. Retrieve the option using a different case than used during setting.
            4. Remove an option using a case-variant key.
            5. Parse a multiline option value and retrieve it.
            6. Load config with a default and verify it appears as a fallback.
        :expectedresults:
            1. Both sections are added and retained as separate entities.
            2. All mixed-case options are accepted without error.
            3. Options are retrieved correctly regardless of case.
            4. Option is removed successfully using case-insensitive key.
            5. The multiline value is parsed and retrieved correctly.
            6. Option fallback from DEFAULT section works as expected.
        """
        cf = self.newconfig()
        cf.add_section("A")
        cf.add_section("a")
        L = cf.sections()
        L.sort()
        eq = self.assertEqual
        eq(L, ["A", "a"])
        cf.set("a", "B", "value")
        eq(cf.options("a"), ["b"])
        eq(cf.get("a", "b"), "value",
           "could not locate option, expecting case-insensitive option names")
        self.assertTrue(cf.has_option("a", "b"))
        cf.set("A", "A-B", "A-B value")
        for opt in ("a-b", "A-b", "a-B", "A-B"):
            self.assertTrue(
                cf.has_option("A", opt),
                "has_option() returned false for option which should exist")
        eq(cf.options("A"), ["a-b"])
        eq(cf.options("a"), ["b"])
        cf.remove_option("a", "B")
        eq(cf.options("a"), [])

        # SF bug #432369:
        cf = self.fromstring(
            "[MySection]\nOption: first line\n\tsecond line\n")
        eq(cf.options("MySection"), ["option"])
        eq(cf.get("MySection", "Option"), "first line\nsecond line")

        # SF bug #561822:
        cf = self.fromstring("[section]\nnekey=nevalue\n",
                             defaults={"key":"value"})
        self.assertTrue(cf.has_option("section", "Key"))

    def test_default_case_sensitivity(self):
        """
        :id: 5f15e8f5-2ac3-4b1f-956c-d441d295e854
        :title: Test case-insensitivity in DEFAULT section
        :description:
            Ensures DEFAULT section option names are accessible in a case-insensitive
            manner.
        :tags: Tier 2
        :steps:
            1. Initialize config with default options using lowercase keys.
            2. Retrieve values using uppercase key.
            3. Initialize config with capitalized keys.
            4. Retrieve values using exact key.
        :expectedresults:
            1. DEFAULT section is created with lowercase options.
            2. Retrieval using uppercase key returns expected value.
            3. DEFAULT section is created with capitalized options.
            4. Retrieval using same case returns expected value.
        """
        cf = self.newconfig({"foo": "Bar"})
        self.assertEqual(
            cf.get("DEFAULT", "Foo"), "Bar",
            "could not locate option, expecting case-insensitive option names")
        cf = self.newconfig({"Foo": "Bar"})
        self.assertEqual(
            cf.get("DEFAULT", "Foo"), "Bar",
            "could not locate option, expecting case-insensitive defaults")

    def test_parse_errors(self):
        """
        :id: 9518b6cf-16b2-48f0-b95a-7c6ccf235981
        :title: Invalid INI parsing raises correct exceptions
        :description:
            Verifies that malformed INI input raises appropriate exceptions during parsing.
        :tags: Tier 2
        :steps:
            1. Attempt to parse a line with extra whitespace before the option.
            2. Attempt to parse a line with missing key but present value.
            3. Attempt to parse a line with missing section header.
        :expectedresults:
            1. ParsingError is raised due to bad spacing.
            2. ParsingError is raised due to malformed key-value syntax.
            3. MissingSectionHeaderError is raised due to absent section header.
        """
        self.newconfig()
        self.parse_error(ConfigParser.ParsingError,
                         "[Foo]\n  extra-spaces: splat\n")
        self.parse_error(ConfigParser.ParsingError,
                         "[Foo]\n  extra-spaces= splat\n")
        self.parse_error(ConfigParser.ParsingError,
                         "[Foo]\noption-without-value\n")
        self.parse_error(ConfigParser.ParsingError,
                         "[Foo]\n:value-without-option-name\n")
        self.parse_error(ConfigParser.ParsingError,
                         "[Foo]\n=value-without-option-name\n")
        self.parse_error(ConfigParser.MissingSectionHeaderError,
                         "No Section!\n")

    def parse_error(self, exc, src):
        sio = StringIO(src)
        self.assertRaises(exc, self.cf.readfp, sio)

    def test_query_errors(self):
        """
        :id: d10dbb38-9e33-420f-8d3f-6bcf07e0e6db
        :title: Exception handling for missing sections and options
        :description:
            Verifies correct exception types are raised when accessing or
            modifying missing sections/options.
        :tags: Tier 2
        :steps:
            1. Call `.sections()` and `.has_section()` on a new config object.
            2. Call `.options()` on a non-existent section.
            3. Attempt to `.set()` an option on a non-existent section.
            4. Attempt to `.get()` an option from a non-existent section.
            5. Add a section and attempt to `.get()` a non-existent option.
        :expectedresults:
            1. Empty list is returned; `has_section()` returns False.
            2. NoSectionError is raised.
            3. NoSectionError is raised.
            4. NoSectionError is raised.
            5. NoOptionError is raised.
        """
        cf = self.newconfig()
        self.assertEqual(cf.sections(), [],
                         "new ConfigParser should have no defined sections")
        self.assertFalse(cf.has_section("Foo"),
                    "new ConfigParser should have no acknowledged sections")
        self.assertRaises(ConfigParser.NoSectionError,
                          cf.options, "Foo")
        self.assertRaises(ConfigParser.NoSectionError,
                          cf.set, "foo", "bar", "value")
        self.get_error(ConfigParser.NoSectionError, "foo", "bar")
        cf.add_section("foo")
        self.get_error(ConfigParser.NoOptionError, "foo", "bar")

    def get_error(self, exc, section, option):
        try:
            self.cf.get(section, option)
        except exc as e:
            return e
        else:
            self.fail("expected exception type %s.%s"
                      % (exc.__module__, exc.__name__))

    def test_boolean(self):
        """
        :id: 46cf56c2-8ae9-4dc7-b760-401cd5f31633
        :title: Boolean value parsing
        :description:
            Verifies that common truthy and falsy values are parsed correctly
            by `getboolean` and invalid ones raise a ValueError.
        :tags: Tier 1
        :steps:
            1. Create a config section with values like '1', 'TRUE', 'yes', etc.
            2. Create another section with values like '0', 'False', 'nO', etc.
            3. Add invalid boolean values (e.g., "foo", "2").
            4. Use `getboolean()` to retrieve and assert truthy/falsy values.
            5. Use `getboolean()` on invalid values and expect exceptions.
        :expectedresults:
            1. All truthy values are parsed as True.
            2. All falsy values are parsed as False.
            3. Invalid values are present in the config.
            4. Calls to `getboolean()` return correct boolean results.
            5. Calls to `getboolean()` on invalid values raise ValueError.
        """
        cf = self.fromstring(
            "[BOOLTEST]\n"
            "T1=1\n"
            "T2=TRUE\n"
            "T3=True\n"
            "T4=oN\n"
            "T5=yes\n"
            "F1=0\n"
            "F2=FALSE\n"
            "F3=False\n"
            "F4=oFF\n"
            "F5=nO\n"
            "E1=2\n"
            "E2=foo\n"
            "E3=-1\n"
            "E4=0.1\n"
            "E5=FALSE AND MORE"
            )
        for x in range(1, 5):
            self.assertTrue(cf.getboolean('BOOLTEST', 't%d' % x))
            self.assertFalse(cf.getboolean('BOOLTEST', 'f%d' % x))
            self.assertRaises(ValueError,
                              cf.getboolean, 'BOOLTEST', 'e%d' % x)

    def test_weird_errors(self):
        """
        :id: 7240b6f5-63a0-4eaf-a4c5-ef488e59e118
        :title: Duplicate section creation raises exception
        :description:
            Ensures that adding a section that already exists raises
            DuplicateSectionError.
        :tags: Tier 2
        :steps:
            1. Create a new configuration object.
            2. Add a section named "Foo".
            3. Attempt to add the same section "Foo" again.
        :expectedresults:
            1. Configuration is initialized successfully.
            2. Section "Foo" is added without error.
            3. DuplicateSectionError is raised when trying to re-add
                the section.
        """
        cf = self.newconfig()
        cf.add_section("Foo")
        self.assertRaises(ConfigParser.DuplicateSectionError,
                          cf.add_section, "Foo")

    def test_write(self):
        """
        :id: 5796aef7-06ea-4fd6-b983-55902aa8d7d2
        :title: Config write operation preserves formatting
        :description:
            Verifies that configuration written to a buffer matches
            the input formatting exactly.
        :tags: Tier 1
        :steps:
            1. Load a multiline configuration string.
            2. Use the `.write()` method to write to a StringIO buffer.
            3. Compare the output string with the expected formatted result.
        :expectedresults:
            1. Configuration is parsed without error.
            2. Data is written to the buffer correctly.
            3. Output matches the expected string exactly, preserving line
                breaks and spacing.
        """
        cf = self.fromstring(
            "[Long Line]\n"
            "foo: this line is much, much longer than my editor\n"
            "   likes it.\n"
            "[DEFAULT]\n"
            "foo: another very\n"
            " long line"
            )
        output = StringIO()
        cf.write(output)
        self.assertEqual(
            output.getvalue(),
            "[Long Line]\n"
            "foo: this line is much, much longer than my editor\n"
            "   likes it.\n"
            "[DEFAULT]\n"
            "foo: another very\n"
            " long line"
            )

    def test_set_string_types(self):
        """
        :id: 5dc6ea85-6cb7-40db-bdb8-c0c82ea8f933
        :title: Setting options using string subclasses
        :description:
            Ensures that setting option values using subclasses of `str`
            works without error.
        :tags: Tier 2
        :steps:
            1. Create a configuration with an existing section.
            2. Set an option using a plain string.
            3. Set the same option using a custom string subclass.
            4. Add a new option using both plain string and subclass.
        :expectedresults:
            1. Section is created successfully.
            2. Plain string is accepted and set correctly.
            3. Subclass of string is accepted without error.
            4. New option is added successfully with both value types.
        """
        cf = self.fromstring("[sect]\n"
                             "option1=foo\n")
        # Check that we don't get an exception when setting values in
        # an existing section using strings:
        class mystr(str):
            pass
        cf.set("sect", "option1", "splat")
        cf.set("sect", "option1", mystr("splat"))
        cf.set("sect", "option2", "splat")
        cf.set("sect", "option2", mystr("splat"))

    def test_read_returns_file_list(self):
        """
        :id: a9b5a53c-bb35-4656-9673-df5e258b099a
        :title: Read method returns list of successfully read files
        :description:
            Verifies that the `.read()` method returns a list of files that were
            successfully parsed.
        :tags: Tier 1
        :steps:
            1. Attempt to read from a valid file and a non-existent file.
            2. Read from a valid file only.
            3. Read from a non-existent file only.
            4. Read from an empty list of files.
        :expectedresults:
            1. Only the valid file is returned in the list; the other is skipped.
            2. Valid file is returned and parsed correctly.
            3. Empty list is returned due to file not existing.
            4. Empty list is returned since no files were passed.
        """
        file1 = test_support.findfile("cfgparser.1")
        if not os.path.exists(file1):
            file1 = test_support.findfile("configdata/cfgparser.1")
        # check when we pass a mix of readable and non-readable files:
        cf = self.newconfig()
        parsed_files = cf.read([file1, "nonexistant-file"])
        self.assertEqual(parsed_files, [file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pass only a filename:
        cf = self.newconfig()
        parsed_files = cf.read(file1)
        self.assertEqual(parsed_files, [file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pass only missing files:
        cf = self.newconfig()
        parsed_files = cf.read(["nonexistant-file"])
        self.assertEqual(parsed_files, [])
        # check when we pass no files:
        cf = self.newconfig()
        parsed_files = cf.read([])
        self.assertEqual(parsed_files, [])

    # shared by subclasses
    def get_interpolation_config(self):
        return self.fromstring(
            "[Foo]\n"
            "bar=something %(with1)s interpolation (1 step)\n"
            "bar9=something %(with9)s lots of interpolation (9 steps)\n"
            "bar10=something %(with10)s lots of interpolation (10 steps)\n"
            "bar11=something %(with11)s lots of interpolation (11 steps)\n"
            "with11=%(with10)s\n"
            "with10=%(with9)s\n"
            "with9=%(with8)s\n"
            "with8=%(With7)s\n"
            "with7=%(WITH6)s\n"
            "with6=%(with5)s\n"
            "With5=%(with4)s\n"
            "WITH4=%(with3)s\n"
            "with3=%(with2)s\n"
            "with2=%(with1)s\n"
            "with1=with\n"
            "\n"
            "[Mutual Recursion]\n"
            "foo=%(bar)s\n"
            "bar=%(foo)s\n"
            "\n"
            "[Interpolation Error]\n"
            "name=%(reference)s\n",
            # no definition for 'reference'
            defaults={"getname": "%(__name__)s"})

    def check_items_config(self, expected):
        cf = self.fromstring(
            "[section]\n"
            "name = value\n"
            "key: |%(name)s| \n"
            "getdefault: |%(default)s|\n"
            "getname: |%(__name__)s|",
            defaults={"default": "<default>"})
        L = list(cf.items("section"))
        L.sort()
        self.assertEqual(L, expected)


class ConfigParserTestCase(TestCaseBase):
    config_class = ConfigParser.ConfigParser

    def test_interpolation(self):
        """
        :id: 9e6235d1-16d1-41b8-bd7d-b8d6c74601c4
        :title: Interpolation resolves nested and recursive values
        :description:
            Verifies that string interpolation works correctly for nested references
            and that exceeding the maximum depth raises the appropriate error.
        :tags: Tier 1
        :steps:
            1. Load a configuration with multiple levels of interpolation (1, 9, 10, 11 steps).
            2. Retrieve an interpolated value with 1 level of depth.
            3. Retrieve values with 9 and 10 levels of depth.
            4. Attempt to retrieve a value with 11 levels to trigger InterpolationDepthError.
        :expectedresults:
            1. Configuration is parsed successfully.
            2. Interpolation is resolved for 1-level reference.
            3. Interpolation works for deeper nesting up to the limit.
            4. InterpolationDepthError is raised when exceeding the limit.
        """
        cf = self.get_interpolation_config()
        eq = self.assertEqual
        eq(cf.get("Foo", "getname"), "Foo")
        eq(cf.get("Foo", "bar"), "something with interpolation (1 step)")
        eq(cf.get("Foo", "bar9"),
           "something with lots of interpolation (9 steps)")
        eq(cf.get("Foo", "bar10"),
           "something with lots of interpolation (10 steps)")
        self.get_error(ConfigParser.InterpolationDepthError, "Foo", "bar11")

    def test_interpolation_missing_value(self):
        """
        :id: b7383b3e-55f4-4e9c-b9c5-ef25f5a3f3f9
        :title: Interpolation fails with undefined reference
        :description:
            Ensures that referencing an undefined variable in interpolation
            raises InterpolationError with the correct metadata.
        :tags: Tier 2
        :steps:
            1. Load configuration with an option that references an undefined key.
            2. Attempt to retrieve the value of the option.
        :expectedresults:
            1. Configuration loads successfully with missing reference.
            2. InterpolationError is raised, containing section, option, and reference name.
        """
        cf = self.get_interpolation_config()
        e = self.get_error(ConfigParser.InterpolationError,
                           "Interpolation Error", "name")
        self.assertEqual(e.reference, "reference")
        self.assertEqual(e.section, "Interpolation Error")
        self.assertEqual(e.option, "name")

    def test_items(self):
        """
        :id: 9cdd38f1-7000-4032-b3e5-0289ac3c8d3e
        :title: Test resolution of interpolated items with defaults
        :description:
            Verifies that calling `.items()` returns the resolved values including
            defaults and interpolated strings.
        :tags: Tier 1
        :steps:
            1. Load configuration with default values and references using %(name)s and %(__name__)s.
            2. Call `.items()` on the target section.
            3. Sort the returned key-value pairs and verify correctness.
        :expectedresults:
            1. Configuration is parsed without error.
            2. Items are retrieved correctly.
            3. Interpolated values are resolved and included in the output.
        """
        self.check_items_config([('default', '<default>'),
                                 ('getdefault', '|<default>|'),
                                 ('getname', '|section|'),
                                 ('key', '|value|'),
                                 ('name', 'value')])

    def test_set_nonstring_types(self):
        """
        :id: 065ec0ab-d6ef-4c7c-8dc3-8e8fba187e6a
        :title: Setting non-string types raises TypeError unless raw is used
        :description:
            Ensures that non-string types (int, list, dict) can be stored in raw mode,
            but raise TypeError when accessed with interpolation.
        :tags: Tier 2
        :steps:
            1. Create a section and set options with int, list, and dict values.
            2. Retrieve each value using raw=True.
            3. Attempt to retrieve each value without raw (interpolation enabled).
        :expectedresults:
            1. Non-string types are accepted and stored.
            2. Raw retrieval returns the original type.
            3. Standard retrieval raises TypeError for incompatible types.
        """
        cf = self.newconfig()
        cf.add_section('non-string')
        cf.set('non-string', 'int', 1)
        cf.set('non-string', 'list', [0, 1, 1, 2, 3, 5, 8, 13, '%('])
        cf.set('non-string', 'dict', {'pi': 3.14159, '%(': 1,
                                      '%(list)': '%(list)'})
        cf.set('non-string', 'string_with_interpolation', '%(list)s')
        self.assertEqual(cf.get('non-string', 'int', raw=True), 1)
        self.assertRaises(TypeError, cf.get, 'non-string', 'int')
        self.assertEqual(cf.get('non-string', 'list', raw=True),
                         [0, 1, 1, 2, 3, 5, 8, 13, '%('])
        self.assertRaises(TypeError, cf.get, 'non-string', 'list')
        self.assertEqual(cf.get('non-string', 'dict', raw=True),
                         {'pi': 3.14159, '%(': 1, '%(list)': '%(list)'})
        self.assertRaises(TypeError, cf.get, 'non-string', 'dict')
        self.assertEqual(cf.get('non-string', 'string_with_interpolation',
                                raw=True), '%(list)s')
        self.assertRaises(ValueError, cf.get, 'non-string',
                          'string_with_interpolation', raw=False)


class RawConfigParserTestCase(TestCaseBase):
    config_class = ConfigParser.RawConfigParser

    def test_interpolation(self):
        """
        :id: 8fc89e68-1d4d-49ad-bb1c-3c66ec1a0730
        :title: RawConfigParser preserves interpolation placeholders
        :description:
            Ensures that when using RawConfigParser, interpolation references like
            %(foo)s are not resolved and are returned as-is.
        :tags: Tier 2
        :steps:
            1. Load a configuration with multiple levels of interpolation.
            2. Retrieve the value of each option that contains a placeholder.
        :expectedresults:
            1. Configuration loads successfully.
            2. Values are returned with interpolation placeholders untouched.
        """
        cf = self.get_interpolation_config()
        eq = self.assertEqual
        eq(cf.get("Foo", "getname"), "%(__name__)s")
        eq(cf.get("Foo", "bar"),
           "something %(with1)s interpolation (1 step)")
        eq(cf.get("Foo", "bar9"),
           "something %(with9)s lots of interpolation (9 steps)")
        eq(cf.get("Foo", "bar10"),
           "something %(with10)s lots of interpolation (10 steps)")
        eq(cf.get("Foo", "bar11"),
           "something %(with11)s lots of interpolation (11 steps)")

    def test_items(self):
        """
        :id: 2ed8ea5d-0a1e-47f4-b92f-1822b13a3ec8
        :title: RawConfigParser returns unresolved values in items
        :description:
            Verifies that `.items()` returns literal values including unresolved
            interpolation placeholders in RawConfigParser.
        :tags: Tier 2
        :steps:
            1. Load configuration with default values and interpolation references.
            2. Call `.items()` on the target section.
            3. Sort the result and verify that values include interpolation syntax.
        :expectedresults:
            1. Configuration is parsed successfully.
            2. Items are returned without resolving any interpolation.
            3. Output matches expected literal strings with placeholders.
        """
        self.check_items_config([('default', '<default>'),
                                 ('getdefault', '|%(default)s|'),
                                 ('getname', '|%(__name__)s|'),
                                 ('key', '|%(name)s|'),
                                 ('name', 'value')])

    def test_set_nonstring_types(self):
        """
        :id: 4d6bd9a0-6505-4628-96d3-362a3a055fb6
        :title: RawConfigParser allows non-string types
        :description:
            Ensures that RawConfigParser can accept and return non-string types
            without raising TypeError.
        :tags: Tier 2
        :steps:
            1. Create a new section in the config.
            2. Set options with int, list, and dict values.
            3. Retrieve each value using standard `.get()`.
        :expectedresults:
            1. Section is added without issues.
            2. Non-string values are stored successfully.
            3. Retrieval returns values of original type with no error.
        """
        cf = self.newconfig()
        cf.add_section('non-string')
        cf.set('non-string', 'int', 1)
        cf.set('non-string', 'list', [0, 1, 1, 2, 3, 5, 8, 13])
        cf.set('non-string', 'dict', {'pi': 3.14159})
        self.assertEqual(cf.get('non-string', 'int'), 1)
        self.assertEqual(cf.get('non-string', 'list'),
                         [0, 1, 1, 2, 3, 5, 8, 13])
        self.assertEqual(cf.get('non-string', 'dict'), {'pi': 3.14159})


class SafeConfigParserTestCase(ConfigParserTestCase):
    config_class = ConfigParser.SafeConfigParser

    def test_safe_interpolation(self):
        """
        :id: c9e5d19e-fb3c-456a-9f6c-97b9e758ec26
        :title: SafeConfigParser resolves safe interpolation syntax
        :description:
            Verifies that SafeConfigParser can correctly handle interpolation
            involving percent signs and preserves literal percent sequences.
        :tags: Tier 1
        :steps:
            1. Load configuration with interpolated values that include
                both placeholders and escaped percent signs.
            2. Retrieve an interpolated value using `%(option1)s`.
            3. Retrieve a value with a literal percent using `%%s`.
        :expectedresults:
            1. Configuration is parsed successfully.
            2. Placeholder interpolation is resolved.
            3. Escaped percent sequence is preserved in the final output.
        """
        # See http://www.python.org/sf/511737
        cf = self.fromstring("[section]\n"
                             "option1=xxx\n"
                             "option2=%(option1)s/xxx\n"
                             "ok=%(option1)s/%%s\n"
                             "not_ok=%(option2)s/%%s")
        self.assertEqual(cf.get("section", "ok"), "xxx/%s")
        self.assertEqual(cf.get("section", "not_ok"), "xxx/xxx/%s")

    def test_set_malformatted_interpolation(self):
        """
        :id: b4a5c7bc-8231-4416-99dc-84d6f42a0fcf
        :title: Malformed interpolation strings raise ValueError
        :description:
            Ensures that setting options with malformed interpolation syntax
            (e.g. single % without a key) raises a ValueError.
        :tags: Tier 2
        :steps:
            1. Create a section and set an initial valid string.
            2. Attempt to set a string with an unmatched % token (e.g. '%foo').
            3. Attempt to set another with trailing % (e.g. 'foo%').
            4. Attempt to set a mid-string malformed token (e.g. 'f%oo').
        :expectedresults:
            1. Initial string is set successfully.
            2. ValueError is raised when using '%foo'.
            3. ValueError is raised when using 'foo%'.
            4. ValueError is raised when using 'f%oo'.
        """
        cf = self.fromstring("[sect]\n"
                             "option1=foo\n")

        self.assertEqual(cf.get('sect', "option1"), "foo")

        self.assertRaises(ValueError, cf.set, "sect", "option1", "%foo")
        self.assertRaises(ValueError, cf.set, "sect", "option1", "foo%")
        self.assertRaises(ValueError, cf.set, "sect", "option1", "f%oo")

        self.assertEqual(cf.get('sect', "option1"), "foo")

    def test_set_nonstring_types(self):
        """
        :id: f2c70993-f539-4cb5-92a2-1ff97d3e4891
        :title: SafeConfigParser disallows non-string values
        :description:
            Ensures that SafeConfigParser enforces string-only values and
            raises TypeError otherwise.
        :tags: Tier 2
        :steps:
            1. Create a config section.
            2. Attempt to set int, float, and object as option values.
            3. Attempt to set a new option with each non-string type.
        :expectedresults:
            1. Section is created successfully.
            2. TypeError is raised for int, float, and object assignments.
            3. New options are not added if value is non-string.
        """
        cf = self.fromstring("[sect]\n"
                             "option1=foo\n")
        # Check that we get a TypeError when setting non-string values
        # in an existing section:
        self.assertRaises(TypeError, cf.set, "sect", "option1", 1)
        self.assertRaises(TypeError, cf.set, "sect", "option1", 1.0)
        self.assertRaises(TypeError, cf.set, "sect", "option1", object())
        self.assertRaises(TypeError, cf.set, "sect", "option2", 1)
        self.assertRaises(TypeError, cf.set, "sect", "option2", 1.0)
        self.assertRaises(TypeError, cf.set, "sect", "option2", object())

    def test_add_section_default_1(self):
        """
        :id: 95174993-fab5-4a3d-8dc2-d9449828b848
        :title: Adding section named 'default' is invalid
        :description:
            Verifies that attempting to add a section named "default"
            (lowercase) raises a ValueError.
        :tags: Tier 3
        :steps:
            1. Create a SafeConfigParser instance.
            2. Attempt to add a section named 'default'.
        :expectedresults:
            1. Parser is created successfully.
            2. ValueError is raised due to reserved section name.
        """
        cf = self.newconfig()
        self.assertRaises(ValueError, cf.add_section, "default")

    def test_add_section_default_2(self):
        """
        :id: 4a9a77a3-003c-4f6f-93cb-d63f45a76e4a
        :title: Adding section named 'DEFAULT' is invalid
        :description:
            Verifies that adding the reserved 'DEFAULT' section explicitly
            raises a ValueError.
        :tags: Tier 3
        :steps:
            1. Create a SafeConfigParser instance.
            2. Attempt to add a section named 'DEFAULT'.
        :expectedresults:
            1. Parser is initialized successfully.
            2. ValueError is raised when using the reserved name.
        """
        cf = self.newconfig()
        self.assertRaises(ValueError, cf.add_section, "DEFAULT")


@unittest.skip("Skipped for now")
class SortedTestCase(RawConfigParserTestCase):
    def newconfig(self, defaults=None):
        self.cf = self.config_class(defaults=defaults, dict_type=SortedDict)
        return self.cf

    def test_sorted(self):
        """
        :id: 64284591-981b-440b-8649-b0d8c8fbc7d6
        :title: Sorted dictionary preserves section and option order
        :description:
            Ensures that using a sorted dictionary for storage preserves
            the ordering of sections and keys when the config is written
            to a string.
        :tags: Tier 3
        :steps:
            1. Create a configuration with multiple sections and unordered keys.
            2. Write the configuration to a string.
            3. Compare the output against expected sorted section and option order.
        :expectedresults:
            1. Configuration is stored with unordered insertion.
            2. Output is written successfully.
            3. Output shows sections and options sorted alphabetically.
        """
        self.fromstring("[b]\n"
                        "o4=1\n"
                        "o3=2\n"
                        "o2=3\n"
                        "o1=4\n"
                        "[a]\n"
                        "k=v\n")
        output = StringIO()
        self.cf.write(output)
        self.assertEquals(output.getvalue(),
                          "[a]\n"
                          "k = v\n\n"
                          "[b]\n"
                          "o1 = 4\n"
                          "o2 = 3\n"
                          "o3 = 2\n"
                          "o4 = 1\n\n")
