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

import re
import unittest
import pickle
import configparser
from io import StringIO
from textwrap import dedent
from iniparse import compat, ini


class CaseSensitiveConfigParser(compat.ConfigParser):
    """
    :description: Case Sensitive version of ConfigParser
    """
    def optionxform(self, option):
        """Use str()"""
        return str(option)


class TestOptionxFormOverride(unittest.TestCase):
    def test_derivedclass(self):
        """
        :id: f1e4d841-d527-48bc-81c2-dcf7f4e5f7b6
        :title: Optionxform override in derived class respects case sensitivity
        :description:
            Verifies that subclassing ConfigParser and overriding optionxform
            preserves key casing and allows retrieval of similarly-named keys.
        :tags: Tier 2
        :steps:
            1. Create a subclass of ConfigParser with case-sensitive optionxform.
            2. Add section `foo` and set two options: `bar` and `Bar` with different values.
            3. Retrieve both keys and verify correct values are returned.
        :expectedresults:
            1. Parser preserves case-sensitive keys due to override.
            2. Keys `bar` and `Bar` are stored and retrieved independently.
            3. Values `'a'` and `'b'` are returned for `bar` and `Bar` respectively.
        """
        c = CaseSensitiveConfigParser()
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        self.assertEqual(c.get('foo', 'bar'), 'a')
        self.assertEqual(c.get('foo', 'Bar'), 'b')

    def test_assignment(self):
        """
        :id: 9b3226b0-2042-4fa1-a02a-34bb4f1a4a83
        :title: Direct assignment of optionxform preserves case-sensitive keys
        :description:
            Verifies that setting optionxform manually on a ConfigParser instance
            enables storing and retrieving multiple keys with differing cases.
        :tags: Tier 2
        :steps:
            1. Create a ConfigParser instance and assign `str` to `optionxform`.
            2. Add section `foo` and set keys `bar` and `Bar` with different values.
            3. Retrieve both keys and check values.
        :expectedresults:
            1. ConfigParser accepts manual override of optionxform.
            2. Keys `bar` and `Bar` are stored as distinct.
            3. Retrieved values match assigned ones.
        """
        c = compat.ConfigParser()
        c.optionxform = str
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        self.assertEqual(c.get('foo', 'bar'), 'a')
        self.assertEqual(c.get('foo', 'Bar'), 'b')

    def test_dyanamic(self):
        """
        :id: 30b18b29-2e11-43e1-9615-2739021c4910
        :title: Dynamically changing optionxform affects key resolution
        :description:
            Verifies that dynamically changing optionxform at runtime alters
            how keys are resolved, demonstrating case folding or preserving behavior.
        :tags: Tier 2
        :steps:
            1. Create ConfigParser and set `optionxform = str`, then insert keys
                with various cases.
            2. Change `optionxform` to `str.upper` and check lookup behavior.
            3. Change to `str.lower` and repeat the lookup.
            4. Restore `optionxform = str` and verify final resolution.
        :expectedresults:
            1. All keys are stored successfully with original casing.
            2. Uppercase transformation causes lookup to resolve to latest
                uppercase match.
            3. Lowercase transformation resolves to lowercase match.
            4. Resetting to `str` resolves the key to original mixed-case match.
        """
        c = compat.ConfigParser()
        c.optionxform = str
        c.add_section('foo')
        c.set('foo', 'bar', 'a')
        c.set('foo', 'Bar', 'b')
        c.set('foo', 'BAR', 'c')
        c.optionxform = str.upper
        self.assertEqual(c.get('foo', 'Bar'), 'c')
        c.optionxform = str.lower
        self.assertEqual(c.get('foo', 'Bar'), 'a')
        c.optionxform = str
        self.assertEqual(c.get('foo', 'Bar'), 'b')


class OnlyReadline:
    def __init__(self, s):
        self.sio = StringIO(s)

    def readline(self):
        return self.sio.readline()


class TestReadline(unittest.TestCase):
    """
    :description:
        Test that the file object passed to readfp only needs to
        support the .readline() method.  As of Python-2.4.4, this is
        true of the standard librariy's ConfigParser, and so other
        code uses that to guide what is sufficiently file-like.
    """
    test_strings = [
"""\
[foo]
bar=7
baz=8""",
"""\
[foo]
bar=7
baz=8
""",
"""\
[foo]
bar=7
baz=8
    """]

    def test_readline_iniconfig(self):
        """
        :id: 56ae3f56-b690-4a0f-85c7-fd57e4f874b6
        :title: INIConfig supports file-like input with only readline()
        :description:
            Verifies that INIConfig can read configuration from an object
            that only implements the `readline()` method.
        :tags: Tier 2
        :steps:
            1. Create a fake file-like object implementing only `readline()`
                with valid INI content.
            2. Pass it to `INIConfig._readfp()` for parsing.
            3. Convert the resulting config back to string.
            4. Compare it with the original input.
        :expectedresults:
            1. The file-like object is initialized correctly.
            2. INIConfig parses the input without error.
            3. The output string is generated successfully.
            4. The output exactly matches the original input.
        """
        for s in self.test_strings:
            fp = OnlyReadline(s)
            c = ini.INIConfig()
            c._readfp(fp)
            self.assertEqual(s, str(c))

    def test_readline_configparser(self):
        """
        :id: 7e0e278e-9e9f-4a1d-92b5-97cc244d287f
        :title: ConfigParser supports file-like input with only readline()
        :description:
            Verifies that the ConfigParser-compatible interface accepts file-like
            objects implementing only `readline()` and maintains content correctly.
        :tags: Tier 2
        :steps:
            1. Create a fake file-like object implementing only `readline()` with
                valid INI content.
            2. Pass it to `ConfigParser.readfp()` for parsing.
            3. Write the parsed config to a new string buffer.
            4. Compare the output with the original input.
        :expectedresults:
            1. The file-like object is created correctly.
            2. ConfigParser parses the input without error.
            3. The output is written to buffer successfully.
            4. The output matches the original configuration input.
        """
        for s in self.test_strings:
            fp = OnlyReadline(s)
            c = compat.ConfigParser()
            c.readfp(fp)
            ss = StringIO()
            c.write(ss)
            self.assertEqual(s, ss.getvalue())


class TestMultilineWithComments(unittest.TestCase):
    """
    :description: Test that multiline values are allowed to span comments.
    """
    s = """\
[sec]
opt = 1
 2

# comment
 3"""

    def test_read(self):
        """
        :id: 2c3b60a5-9e31-4411-a027-6e81c47b37a1
        :title: Multiline values span comments correctly on read
        :description:
            Verifies that `INIConfig` allows multi-line option values to continue
            even after blank lines or comments.
        :tags: Tier 2
        :steps:
            1. Create an INI string where a value spans multiple lines and includes
                an inline comment and blank line.
            2. Load the config into `INIConfig` using `_readfp`.
            3. Retrieve the multiline option value.
        :expectedresults:
            1. The config is loaded correctly without error.
            2. Multiline content is preserved across blank lines and comments.
            3. The value matches the expected multiline string.
        """
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.assertEqual(c.sec.opt, '1\n2\n\n3')

    def test_write(self):
        """
        :id: 7d8d14ec-8ac1-41fd-8035-e117800b3be4
        :title: Writing replaces multiline value with new single-line string
        :description:
            Verifies that assigning a new value to a previously multiline option
            replaces it with a single-line value in the output.
        :tags: Tier 2
        :steps:
            1. Load the multiline config into `INIConfig`.
            2. Assign a single-line value to the multiline option.
            3. Convert the updated config to a string.
        :expectedresults:
            1. The config is loaded correctly with the original multiline value.
            2. The new value replaces the old one without error.
            3. The output string contains the updated single-line option.
        """
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")


class TestEmptyFile(unittest.TestCase):
    """
    :description: Test if it works with a blank file.
    """
    s = ""

    def test_read(self):
        """
        :id: e31b9e0b-0c41-41fd-9a95-4e1e7cc4a298
        :title: Reading an empty file results in empty config
        :description:
            Verifies that reading an empty file using INIConfig results in an empty
            configuration object.
        :tags: Tier 2
        :steps:
            1. Initialize INIConfig and load an empty string using `_readfp`.
            2. Convert the config to a string.
        :expectedresults:
            1. The config is loaded successfully without errors.
            2. The output string is empty, confirming no content exists.
        """
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.assertEqual(str(c), '')

    def test_write(self):
        """
        :id: 4bfa2b67-9427-4c91-948e-f2961c83fc2b
        :title: Writing to empty config results in valid output
        :description:
            Verifies that assigning values to a previously empty config
            results in valid INI output.
        :tags: Tier 2
        :steps:
            1. Initialize INIConfig and load an empty string.
            2. Add a section and an option with a value.
            3. Convert the config to a string.
        :expectedresults:
            1. The config is initialized and remains empty after loading.
            2. Section and option are added successfully.
            3. Output string contains a valid section and key-value pair.
        """
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        c.sec.opt = 'xyz'
        self.assertEqual(str(c), """\
[sec]
opt = xyz""")


class TestCustomDict(unittest.TestCase):
    def test_custom_dict_not_supported(self):
        """
        :id: c9b615d3-4a56-4604-baad-41f588b3cb51
        :title: Custom dict type is not supported in RawConfigParser
        :description:
            Verifies that attempting to initialize RawConfigParser with
            an unsupported custom dictionary type raises a ValueError.
        :tags: Tier 2
        :steps:
            1. Attempt to create a RawConfigParser instance with `dict_type='foo'`.
        :expectedresults:
            1. A ValueError is raised, indicating that custom dictionary types are
                not supported.
        """
        self.assertRaises(ValueError, compat.RawConfigParser, None, 'foo')


class TestCompat(unittest.TestCase):
    """
    :description: Miscellaneous compatibility tests.
    """
    s = dedent("""\
        [DEFAULT]
        pi = 3.1415
        three = 3
        poet = e e

             cummings
        NH =
         live free

         or die

        [sec]
        opt = 6
        three = 3.0
        no-three = one
         two

         four
        longopt = foo
         bar

        # empty line should not be part of value
         baz

         bat

        """)

    def do_test(self, c):
        # default section is not acknowledged
        self.assertEqual(c.sections(), ['sec'])
        # options in the default section are merged with other sections
        self.assertEqual(sorted(c.options('sec')),
                         ['longopt', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])

        # empty lines are stripped from multi-line values
        self.assertEqual(c.get('sec', 'poet').split('\n'),
                         ['e e', 'cummings'])
        self.assertEqual(c.get('DEFAULT', 'poet').split('\n'),
                         ['e e', 'cummings'])
        self.assertEqual(c.get('sec', 'longopt').split('\n'),
                         ['foo', 'bar', 'baz', 'bat'])
        self.assertEqual(c.get('sec', 'NH').split('\n'),
                         ['', 'live free', 'or die'])

        # check that empy-line stripping happens on all access paths
        # defaults()
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        # items()
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('longopt', 'foo\nbar\nbaz\nbat'),
            ('nh', '\nlive free\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])

        # empty lines are preserved on explicitly set values
        c.set('sec', 'longopt', '\n'.join(['a', 'b', '', 'c', '', '', 'd']))
        c.set('DEFAULT', 'NH', '\nlive free\n\nor die')
        self.assertEqual(c.get('sec', 'longopt').split('\n'),
                         ['a', 'b', '', 'c', '', '', 'd'])
        self.assertEqual(c.get('sec', 'NH').split('\n'),
                         ['', 'live free', '', 'or die'])
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\n\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        # items()
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('longopt', 'a\nb\n\nc\n\n\nd'),
            ('nh', '\nlive free\n\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])

        # empty line special magic goes away after remove_option()
        self.assertEqual(c.get('sec', 'no-three').split('\n'),
                         ['one', 'two','four'])
        c.remove_option('sec', 'no-three')
        c.set('sec', 'no-three', 'q\n\nw')
        self.assertEqual(c.get('sec', 'no-three'), 'q\n\nw')
        c.remove_option('sec', 'no-three')

    def do_configparser_test(self, cfg_class):
        c = cfg_class()
        c.readfp(StringIO(self.s))
        self.do_test(c)
        o = StringIO()
        c.write(o)
        self.assertEqual(o.getvalue().split('\n'), [
            '[DEFAULT]',
            'poet = e e',
            '\tcummings',
            'nh = ',
            '\tlive free',
            '\t',
            '\tor die',
            'pi = 3.1415',
            'three = 3',
            '',
            '[sec]',
            'opt = 6',
            'longopt = a',
            '\tb',
            '\t',
            '\tc',
            '\t',
            '\t',
            '\td',
            'three = 3.0',
            '',
            ''])

    def test_py_rawcfg(self):
        """
        :id: 3eb8aa70-17f5-4a2e-bb97-0de0b8e90ba1
        :title: RawConfigParser preserves multiline values and defaults
        :description:
            Verifies that RawConfigParser correctly reads and writes multiline
            values, merges defaults, and removes empty lines from values.
        :tags: Tier 1
        :steps:
            1. Initialize a RawConfigParser instance and load multiline
                configuration string.
            2. Validate that options from DEFAULT section are merged into
                other sections.
            3. Confirm correct parsing and preservation of multiline values.
            4. Serialize the config using `write()` and verify output format.
        :expectedresults:
            1. RawConfigParser loads the config without error.
            2. Merged defaults are visible in other sections.
            3. Multiline values are parsed and cleaned correctly.
            4. Output format is consistent and matches expected tidy layout.
        """
        self.do_configparser_test(configparser.RawConfigParser)

    def test_py_cfg(self):
        """
        :id: e32431e0-61cf-486c-b215-1739e16f4029
        :title: ConfigParser handles multiline and default merging correctly
        :description:
            Verifies that ConfigParser reads a complex configuration with
            multiline values and default merging, and serializes it as expected.
        :tags: Tier 1
        :steps:
            1. Initialize ConfigParser and load config with DEFAULT and section values.
            2. Check merged keys and formatted output.
            3. Serialize config and compare lines to expected output.
        :expectedresults:
            1. ConfigParser loads and merges values correctly.
            2. Multiline options are processed and stripped of extra spacing.
            3. Output matches expected layout with correct indentation and order.
        """
        self.do_configparser_test(configparser.ConfigParser)

    def test_py_safecfg(self):
        """
        :id: 42f9fdc4-2dbe-4e91-88f7-2cd229582c97
        :title: SafeConfigParser handles multiline values and default inheritance
        :description:
            Ensures that SafeConfigParser handles complex default merging
            and multi-line value formatting properly and writes a clean config.
        :tags: Tier 1
        :steps:
            1. Initialize SafeConfigParser and load config string with
                mixed formatting.
            2. Verify section and default resolution.
            3. Confirm output serialization matches cleaned structure.
        :expectedresults:
            1. SafeConfigParser reads the input config without error.
            2. Merged values and options are resolved correctly.
            3. Output string reflects normalized config layout.
        """
        self.do_configparser_test(configparser.SafeConfigParser)

    def do_compat_test(self, cfg_class):
        c = cfg_class()
        c.readfp(StringIO(self.s))
        self.do_test(c)
        o = StringIO()
        c.write(o)
        self.assertEqual(o.getvalue().split('\n'), [
            '[DEFAULT]',
            'pi = 3.1415',
            'three = 3',
            'poet = e e',
            '',
            '     cummings',
            'NH =',
            ' live free',
            '',
            ' or die',
            '',
            '[sec]',
            'opt = 6',
            'three = 3.0',
            'longopt = a',
            ' b',
            '',
            ' c',
            '',
            '',
            ' d',
            '',
            ''])

    def test_py_rawcfg(self):
        """
        :id: 3eb8aa70-17f5-4a2e-bb97-0de0b8e90ba2
        :title: RawConfigParser preserves multiline values and defaults
        :description:
            Verifies that RawConfigParser correctly reads and writes multiline
            values, merges defaults, and removes empty lines from values.
        :tags: Tier 1
        :steps:
            1. Initialize a RawConfigParser instance and load multiline
                configuration string.
            2. Validate that options from DEFAULT section are merged into
                other sections.
            3. Confirm correct parsing and preservation of multiline values.
            4. Serialize the config using `write()` and verify output format.
        :expectedresults:
            1. RawConfigParser loads the config without error.
            2. Merged defaults are visible in other sections.
            3. Multiline values are parsed and cleaned correctly.
            4. Output format is consistent and matches expected tidy layout.
        """
        self.do_compat_test(compat.RawConfigParser)

    def test_py_cfg(self):
        """
        :id: e32431e0-61cf-486c-b215-1739e16f4030
        :title: ConfigParser handles multiline and default merging correctly
        :description:
            Verifies that ConfigParser reads a complex configuration with
            multiline values and default merging, and serializes it as expected.
        :tags: Tier 1
        :steps:
            1. Initialize ConfigParser and load config with DEFAULT and section values.
            2. Check merged keys and formatted output.
            3. Serialize config and compare lines to expected output.
        :expectedresults:
            1. ConfigParser loads and merges values correctly.
            2. Multiline options are processed and stripped of extra spacing.
            3. Output matches expected layout with correct indentation and order.
        """
        self.do_compat_test(compat.ConfigParser)

    def test_py_safecfg(self):
        """
        :id: 42f9fdc4-2dbe-4e91-88f7-2cd229582c98
        :title: SafeConfigParser handles multiline values and default inheritance
        :description:
            Ensures that SafeConfigParser handles complex default merging
            and multi-line value formatting properly and writes a clean config.
        :tags: Tier 1
        :steps:
            1. Initialize SafeConfigParser and load config string with
                mixed formatting.
            2. Verify section and default resolution.
            3. Confirm output serialization matches cleaned structure.
        :expectedresults:
            1. SafeConfigParser reads the input config without error.
            2. Merged values and options are resolved correctly.
            3. Output string reflects normalized config layout.
        """
        self.do_compat_test(compat.SafeConfigParser)


class TestPickle(unittest.TestCase):
    s = dedent("""\
        [DEFAULT]
        pi = 3.1415
        three = 3
        poet = e e

             cummings
        NH =
         live free

         or die

        [sec]
        opt = 6
        three = 3.0
        no-three = one
         two

         four

        james = bond
        """)

    def do_compat_checks(self, c):
        self.assertEqual(c.sections(), ['sec'])
        self.assertEqual(sorted(c.options('sec')),
                         ['james', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])
        self.assertEqual(c.defaults(), {
            'poet': 'e e\ncummings',
            'nh': '\nlive free\nor die',
            'pi': '3.1415',
            'three': '3',
        })
        l = c.items('sec')
        l.sort()
        self.assertEqual(l, [
            ('james', 'bond'),
            ('nh', '\nlive free\nor die'),
            ('no-three', 'one\ntwo\nfour'),
            ('opt', '6'),
            ('pi', '3.1415'),
            ('poet', 'e e\ncummings'),
            ('three', '3.0'),
        ])
        self.do_ini_checks(c.data)

    def do_ini_checks(self, c):
        self.assertEqual(list(c), ['sec'])
        self.assertEqual(sorted(c['sec']), ['james', 'nh', 'no-three', 'opt', 'pi', 'poet', 'three'])
        self.assertEqual(c._defaults['pi'], '3.1415')
        self.assertEqual(c.sec.opt, '6')
        self.assertEqual(c.sec.three, '3.0')
        self.assertEqual(c.sec['no-three'], 'one\ntwo\n\nfour')
        self.assertEqual(c.sec.james, 'bond')
        self.assertEqual(c.sec.pi, '3.1415')
        self.assertEqual(c.sec.poet, 'e e\n\ncummings')
        self.assertEqual(c.sec.NH, '\nlive free\n\nor die')
        self.assertEqual(str(c), self.s)

    def test_compat(self):
        """
        :id: 6dbdef0f-4291-4e78-91aa-0541f57b25bb
        :title: ConfigParser instances retain structure after pickling
        :description:
            Verifies that ConfigParser-compatible classes maintain structure
            and values after being serialized and deserialized via pickle.
        :tags: Tier 1
        :steps:
            1. Initialize multiple ConfigParser-compatible objects and load
                the test config.
            2. Serialize each object using pickle with all supported protocols.
            3. Deserialize the data and validate the structure and values.
        :expectedresults:
            1. Each config object is loaded correctly with expected data.
            2. Pickling and unpickling completes without error.
            3. Deserialized objects match the original in structure and content.
        """
        for cfg_class in (compat.ConfigParser, compat.RawConfigParser, compat.SafeConfigParser):
            c = cfg_class()
            c.readfp(StringIO(self.s))
            self.do_compat_checks(c)
            for i in range(0, pickle.HIGHEST_PROTOCOL+1):
                p = pickle.dumps(c, protocol=i)
                c2 = pickle.loads(p)
                self.do_compat_checks(c2)

    def test_ini(self):
        """
        :id: 2a2d48e6-2ff7-4ef5-b38e-84a39be29909
        :title: INIConfig retains structure after pickling
        :description:
            Verifies that INIConfig objects can be serialized and deserialized
            via pickle without losing data, formatting, or section layout.
        :tags: Tier 1
        :steps:
            1. Load a complex config into an INIConfig object.
            2. Serialize the object using pickle with all available protocols.
            3. Deserialize the result and check that structure and values
                are preserved.
        :expectedresults:
            1. INIConfig loads the input config and maintains section layout.
            2. Pickling with each protocol succeeds.
            3. Deserialized objects retain all original content and formatting.
        """
        c = ini.INIConfig()
        c._readfp(StringIO(self.s))
        self.do_ini_checks(c)
        for i in range(0, pickle.HIGHEST_PROTOCOL+1):
            p = pickle.dumps(c, protocol=i)
            c2 = pickle.loads(p)
            self.do_ini_checks(c2)


class TestCommentSyntax(unittest.TestCase):
    """
    :description: Test changing comment syntax with change_comment_syntax.
    """
    def test_regex(self):
        """
        :id: 5a646ff2-3488-4a7c-bcf3-820059b1f786
        :title: Changing comment syntax updates parsing regex
        :description:
            Verifies that the `change_comment_syntax()` method updates the regular
            expression used for parsing comment lines and properly escapes special
            characters.
        :tags: Tier 2
        :steps:
            1. Set the default regex via `change_comment_syntax(';#', True)`
                and verify result.
            2. Set Mercurial-compatible syntax using `%;#` and verify regex update.
            3. Call `change_comment_syntax()` with no arguments and confirm fallback
                to Mercurial-safe regex.
            4. Use special characters in the syntax string and ensure they are
                escaped properly.
        :expectedresults:
            1. The default regex matches the original pattern.
            2. Mercurial-safe regex is set correctly.
            3. Default call uses Mercurial-safe mode.
            4. Special characters are escaped and included in the regex.
        """
        # original regular expression
        org_regex = re.compile(r'^(?P<csep>[;#]|[rR][eE][mM])(?P<comment>.*)$')
        ini.change_comment_syntax(';#', True)
        self.assertEqual(ini.CommentLine.regex, org_regex)

        # mercurial-safe comment line regex, as given by Steve Borho & Paul Lambert
        # bitbucket.org/tortoisehg/stable/src/tip/tortoisehg/hgtk/thgconfig.py#cl-1084
        # http://groups.google.com/group/iniparse-discuss/msg/b41a54aa185a9b7c
        hg_regex = re.compile(r'^(?P<csep>[%;#])(?P<comment>.*)$')
        ini.change_comment_syntax('%;#', False)
        self.assertEqual(ini.CommentLine.regex, hg_regex)

        # change_comment_syntax() defaults to hg regex
        ini.change_comment_syntax()
        self.assertEqual(ini.CommentLine.regex, hg_regex)

        # test escaping of special chars in pattern
        regex = re.compile(r'^(?P<csep>[;#\-\^[\]])(?P<comment>.*)$')
        ini.change_comment_syntax(';#-^[]')
        self.assertEqual(ini.CommentLine.regex, regex)

    def test_ignore_includes(self):
        """
        :id: 8c3f45a3-1af0-4fd6-a345-73ce9cdaef35
        :title: Config with comment-style includes is parsed correctly
        :description:
            Verifies that comment lines using `% include` in Mercurial-style configs
            do not interfere with parsing and are preserved in output.
        :tags: Tier 2
        :steps:
            1. Set Mercurial-style comment syntax using `change_comment_syntax()`.
            2. Load a config containing `% include` using `INIConfig`.
            3. Access a known value to ensure parsing succeeded.
            4. Convert the config back to a string and confirm comment line is
                preserved.
        :expectedresults:
            1. Comment style is updated to match Mercurial syntax.
            2. Config is parsed correctly without ignoring or misinterpreting
                comment lines.
            3. The key `username` is accessible as expected.
            4. Output contains `% include` line unchanged.
        """
        ini.change_comment_syntax()
        cfg = ini.INIConfig(StringIO(dedent("""
            # This is a mercurial-style config
            % include foobar

            [ui]
            username = Firstname Lastname <a@b.c>
            """)))
        self.assertEqual(cfg.ui.username, 'Firstname Lastname <a@b.c>')
        self.assertEqual(str(cfg), dedent("""
            # This is a mercurial-style config
            % include foobar

            [ui]
            username = Firstname Lastname <a@b.c>
            """))

    def tearDown(self):
        ini.change_comment_syntax(';#', True)
