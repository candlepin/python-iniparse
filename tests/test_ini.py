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
from iniparse import compat
from iniparse import config


class TestSectionLine(unittest.TestCase):
    invalid_lines = [
        '# this is a comment',
        '; this is a comment',
        '  [sections must start on column1]',
        '[incomplete',
        '[ no closing ]brackets]',
        'ice-cream = mmmm',
        'ic[e-c]ream = mmmm',
        '[ice-cream] = mmmm',
        '-$%^',
    ]

    def test_invalid(self):
        """
        :id: b04b3e76-0c9e-4eb4-a9cd-6a1f4d527e88
        :title: SectionLine rejects invalid lines
        :description:
            Verifies that lines which are not valid section headers
            return None when parsed by SectionLine.
        :tags: Tier 2
        :steps:
            1. Define a list of malformed or non-section strings.
            2. Attempt to parse each string using SectionLine.parse().
        :expectedresults:
            1. Each invalid line returns None when parsed.
            2. No exception is raised during parsing
        """
        for l in self.invalid_lines:
            p = ini.SectionLine.parse(l)
            self.assertEqual(p, None)

    lines = [
        ('[section]',          ('section', None, None, -1)),
        (r'[se\ct%[ion\t]',     (r'se\ct%[ion\t', None, None, -1)),
        ('[sec tion]  ; hi',   ('sec tion', ' hi', ';', 12)),
        ('[section]  #oops!',  ('section', 'oops!', '#', 11)),
        ('[section]   ;  ',    ('section', '', ';', 12)),
        ('[section]      ',    ('section', None, None, -1)),
    ]

    def test_parsing(self):
        """
        :id: 62aa28db-f730-4b67-85b9-cd1ee4fa2186
        :title: SectionLine parses valid lines with comments
        :description:
            Verifies that SectionLine correctly extracts the section
            name and optional comment details.
        :tags: Tier 2
        :steps:
            1. Create a list of valid comment lines starting with
                '#', ';', or 'Rem'.
            2. Parse each comment line using CommentLine.parse().
            3. Convert each parsed line to a string using `str()`.
            4. Convert each parsed line using `to_string()`.
        :expectedresults:
            1. All input lines are valid comment lines.
            2. Parsing returns a valid CommentLine object for each line.
            3. `str()` returns the original unmodified comment line.
            4. `to_string()` returns the line stripped of trailing whitespace.
        """
        for l in self.lines:
            p = ini.SectionLine.parse(l[0])
            self.assertNotEqual(p, None)
            self.assertEqual(p.name, l[1][0])
            self.assertEqual(p.comment, l[1][1])
            self.assertEqual(p.comment_separator, l[1][2])
            self.assertEqual(p.comment_offset, l[1][3])

    def test_printing(self):
        """
        :id: fcb270b2-65c0-4485-9151-9791ae35cbe4
        :title: SectionLine preserves formatting on output
        :description:
            Ensures that calling `str()` or `to_string()` on a SectionLine returns
            the original or stripped line.
        :tags: Tier 2
        :steps:
            1. Parse a list of valid section lines.
            2. Call `str()` and `to_string()` on the result.
        :expectedresults:
            1. `str()` returns the exact original line.
            2. `to_string()` returns the line with trailing spaces removed.
        """
        for l in self.lines:
            p = ini.SectionLine.parse(l[0])
            self.assertEqual(str(p), l[0])
            self.assertEqual(p.to_string(), l[0].strip())

    indent_test_lines = [
        ('[oldname]             ; comment', 'long new name',
         '[long new name]       ; comment'),
        ('[oldname]             ; comment', 'short',
         '[short]               ; comment'),
        ('[oldname]             ; comment', 'really long new name',
         '[really long new name] ; comment'),
    ]

    def test_preserve_indentation(self):
        """
        :id: 2ebeff23-b508-4307-8164-16a1e405708c
        :title: SectionLine preserves spacing when name changes
        :description:
            Verifies that changing a section name maintains the original
            alignment and indentation of the line.
        :tags: Tier 2
        :steps:
            1. Parse a section line with a specific alignment and comment.
            2. Change the section name to something longer or shorter.
            3. Convert the object back to a string.
        :expectedresults:
            1. Section line with a specific alignment and comment is parsed
            2. Name changes are applied correctly.
            3. Output preserves spacing and comment alignment.
        """
        for l in self.indent_test_lines:
            p = ini.SectionLine.parse(l[0])
            p.name = l[1]
            self.assertEqual(str(p), l[2])


class TestOptionLine(unittest.TestCase):
    lines = [
        ('option = value', 'option', ' = ', 'value', None, None, -1),
        ('option:   value', 'option', ':   ', 'value', None, None, -1),
        ('option=value', 'option', '=', 'value', None, None, -1),
        ('op[ti]on=value', 'op[ti]on', '=', 'value', None, None, -1),

        ('option = value # no comment', 'option', ' = ', 'value # no comment',
                                         None, None, -1),
        ('option = value     ;', 'option', ' = ', 'value',
                                         ';', '', 19),
        ('option = value     ; comment', 'option', ' = ', 'value',
                                         ';', ' comment', 19),
        ('option = value;1   ; comment', 'option', ' = ', 'value;1   ; comment',
                                         None, None, -1),
        ('op;ti on = value      ;; comm;ent', 'op;ti on', ' = ', 'value',
                                         ';', '; comm;ent', 22),
    ]
    def test_parsing(self):
        """
        :id: 4d2a847f-65f6-49ff-9637-2a6b1b6a7e65
        :title: OptionLine parses valid lines and extracts components correctly
        :description:
            Verifies that OptionLine correctly parses option name, separator, value
            and optional comment fields from a variety of valid formats.
        :tags: Tier 2
        :steps:
            1. Define multiple valid option lines using different separators and
                comment placements.
            2. Parse each line using OptionLine.parse().
            3. Extract the name, separator, and value from each parsed line.
            4. Extract optional comment separator, comment text, and comment offset.
        :expectedresults:
            1. Each line is accepted as valid input.
            2. Parsing returns a valid OptionLine object.
            3. The name, separator, and value match expected values.
            4. Comment-related fields are either correctly populated or None,
                depending on input.
        """
        for l in self.lines:
            p = ini.OptionLine.parse(l[0])
            self.assertEqual(p.name, l[1])
            self.assertEqual(p.separator, l[2])
            self.assertEqual(p.value, l[3])
            self.assertEqual(p.comment_separator, l[4])
            self.assertEqual(p.comment, l[5])
            self.assertEqual(p.comment_offset, l[6])

    invalid_lines = [
        '  option = value',
        '# comment',
        '; comment',
        '[section 7]',
        '[section=option]',
        'option',
    ]

    def test_invalid(self):
        """
        :id: b56e1536-3270-4dd1-b5d1-d6e1a93b982a
        :title: OptionLine rejects invalid or misformatted lines
        :description:
            Ensures that lines which do not match valid option syntax are
            rejected and return None when parsed.
        :tags: Tier 2
        :steps:
            1. Define lines that resemble options but are either misaligned,
                incomplete, or structurally invalid.
            2. Attempt to parse each line using OptionLine.parse().
        :expectedresults:
            1. Each invalid line is correctly identified as malformed.
            2. Parsing returns None for each of them.
        """
        for l in self.invalid_lines:
            p = ini.OptionLine.parse(l)
            self.assertEqual(p, None)

    print_lines = [
        'option = value',
        'option= value',
        'option : value',
        'option: value  ',
        'option   =    value  ',
        'option = value   ;',
        'option = value;2    ;; 4 5',
        'option = value     ; hi!',
    ]

    def test_printing(self):
        """
        :id: 17d9d243-fabe-4f83-976b-1b1e10f39c2a
        :title: OptionLine preserves formatting during string conversion
        :description:
            Verifies that the string representation of OptionLine objects matches
            the original input formatting and spacing.
        :tags: Tier 2
        :steps:
            1. Define a list of option lines with varying formats (spacing,
                separators, and comments).
            2. Parse each line using OptionLine.parse().
            3. Call `str()` on the parsed object and compare with the original line.
            4. Call `to_string()` and compare it with the stripped version
                of the original line.
        :expectedresults:
            1. All lines are parsed successfully.
            2. `str()` returns the exact original input including spacing.
            3. `to_string()` returns the same line but without trailing whitespace.
        """
        for l in self.print_lines:
            p = ini.OptionLine.parse(l)
            self.assertEqual(str(p), l)
            self.assertEqual(p.to_string(), l.rstrip())

    indent_test_lines = [
        ('option = value   ;comment', 'newoption', 'newval',
         'newoption = newval ;comment'),
        ('option = value       ;comment', 'newoption', 'newval',
         'newoption = newval   ;comment'),
    ]

    def test_preserve_indentation(self):
        """
        :id: 31275c63-cda1-4726-bc9b-08fd9b2cf8e4
        :title: OptionLine preserves spacing and alignment when modified
        :description:
            Ensures that after modifying the option name and value, the output string
            retains the original alignment and spacing of the comment.
        :tags: Tier 2
        :steps:
            1. Parse an option line that contains an aligned comment.
            2. Change the option name and value.
            3. Convert the modified OptionLine to a string.
            4. Compare it to the expected output with correct alignment.
        :expectedresults:
            1. The line is parsed successfully and the comment position is captured.
            2. New name and value are assigned without breaking structure.
            3. `str()` returns a correctly formatted line with updated values.
            4. Alignment between value and comment remains consistent.
        """
        for l in self.indent_test_lines:
            p = ini.OptionLine.parse(l[0])
            p.name = l[1]
            p.value = l[2]
            self.assertEqual(str(p), l[3])


class TestCommentLine(unittest.TestCase):
    invalid_lines = [
        '[section]',
        'option = value ;comment',
        '  # must start on first column',
    ]

    def test_invalid(self):
        """
        :id: e492f9f0-0b70-466f-94d8-33ad716aa5a6
        :title: CommentLine rejects lines that are not valid comments
        :description:
            Verifies that lines which do not start with a valid comment prefix in
            column 0 are not parsed as CommentLine objects.
        :tags: Tier 2
        :steps:
            1. Define a list of lines that resemble options, sections
                or indented comments.
            2. Attempt to parse each line using CommentLine.parse().
        :expectedresults:
            1. Each input line is valid for testing (e.g., starts with
                `[`, contains `=`, or is indented).
            2. Parsing returns None for each line, confirming they are not recognized
                as valid comments.
        """
        for l in self.invalid_lines:
            p = ini.CommentLine.parse(l)
            self.assertEqual(p, None)

    lines = [
        '#this is a comment',
        ';; this is also a comment',
        '; so is this   ',
        'Rem and this'
    ]

    def test_parsing(self):
        """
        :id: d14f3d15-4c04-4718-9e79-06661b84b514
        :title: CommentLine correctly parses and preserves formatting
        :description:
            Ensures that valid comment lines starting with `#`, `;`, or `Rem` are
            parsed as CommentLine objects and retain their exact original formatting.
        :tags: Tier 2
        :steps:
            1. Define a list of valid comment lines with various prefixes and spacing.
            2. Parse each line using CommentLine.parse().
            3. Convert the parsed object back to a string using `str()`.
            4. Convert the parsed object using `to_string()`.
        :expectedresults:
            1. Each line is recognized as a valid comment format.
            2. Parsing returns a valid CommentLine object.
            3. `str()` returns the exact original line including spacing.
            4. `to_string()` returns the line without trailing whitespace.
        """
        for l in self.lines:
            p = ini.CommentLine.parse(l)
            self.assertEqual(str(p), l)
            self.assertEqual(p.to_string(), l.rstrip())


class TestOtherLines(unittest.TestCase):
    def test_empty(self):
        """
        :id: c5e24b8c-fb0d-4bd1-970a-fc979e6493c7
        :title: EmptyLine identifies only blank or whitespace-only lines
        :description:
            Ensures that only lines which contain no visible characters (or just whitespace)
            are recognized as EmptyLine, and all other lines return None.
        :tags: Tier 2
        :steps:
            1. Create a list of lines that contain text, options, or section headers.
            2. Parse each of those lines using EmptyLine.parse().
            3. Create a list of lines that are completely empty or contain only whitespace.
            4. Parse each of those lines using EmptyLine.parse().
            5. Convert each valid EmptyLine to string using `str()`.
        :expectedresults:
            1. Lines with text are correctly identified as invalid for EmptyLine.
            2. Parsing returns None for each non-empty line.
            3. Whitespace-only lines are accepted as valid EmptyLine instances.
            4. Parsing returns a valid object for empty/whitespace lines.
            5. String conversion of EmptyLine objects returns the original whitespace line.
        """
        for s in ['asdf', '; hi', '  #rr', '[sec]', 'opt=val']:
            self.assertEqual(ini.EmptyLine.parse(s), None)
        for s in ['', '  ', '\t  \t']:
            self.assertEqual(str(ini.EmptyLine.parse(s)), s)

    def test_continuation(self):
        """
        :id: 01a2f7ec-6b43-4c69-8776-05a2c999ea6f
        :title: ContinuationLine identifies and preserves indented lines
        :description:
            Verifies that lines with leading whitespace are recognized as continuation lines,
            and that their value and formatting are preserved correctly.
        :tags: Tier 2
        :steps:
            1. Create a list of lines that are clearly not continuation lines
                (e.g. section headers, options, comments).
            2. Parse each of these using ContinuationLine.parse().
            3. Create a list of indented lines containing values.
            4. Parse each using ContinuationLine.parse() and access `.value`.
            5. Convert the parsed objects using `to_string()`.
        :expectedresults:
            1. Lines not intended as continuations are rejected.
            2. Parsing returns None for those lines.
            3. Indented lines are accepted as continuation lines.
            4. The `.value` returns the stripped value of the line.
            5. The `to_string()` returns the line without trailing whitespace
                and with tabs replaced by spaces.
        """
        for s in ['asdf', '; hi', '[sec]', 'a=3']:
            self.assertEqual(ini.ContinuationLine.parse(s), None)
        for s in [' asdfasd ', '\t mmmm']:
            self.assertEqual(ini.ContinuationLine.parse(s).value,
                             s.strip())
            self.assertEqual(ini.ContinuationLine.parse(s).to_string(),
                             s.rstrip().replace('\t',' '))


class TestIni(unittest.TestCase):
    s1 = """
[section1]
help = me
I'm  = desperate     ; really!

[section2]
# comment and empty line before the first option

just = what?
just = kidding

[section1]
help = yourself
but = also me
"""

    def test_basic(self):
        """
        :id: 7d6fd4eb-374f-4b17-9783-318d9d3fdde4
        :title: INIConfig parses repeated sections and preserves line numbers
        :description:
            Verifies that INIConfig correctly handles multiple repeated sections, resolves
            values based on last occurrence, and tracks the correct line numbers for options.
        :tags: Tier 1
        :steps:
            1. Load a configuration string with two '[section1]' blocks and one '[section2]'.
            2. Use internal `.find()` method to retrieve specific options from
                the parsed config.
            3. Assert that each option contains the correct final value.
            4. Assert that each option has the correct original line number.
            5. Create an iterator for all '[section1]' blocks using '.finditer()'.
            6. Iterate through values and validate correct content from both blocks.
            7. Assert that the iterator raises StopIteration at the end.
            8. Attempt to access a missing section and option to ensure correct
                exception handling.
        :expectedresults:
            1. Config is parsed without error and recognizes both section1 and section2.
            2. `.find()` correctly locates each option.
            3. Final values reflect the last assigned value in repeated sections.
            4. Each option has the expected line number from the input string.
            5. Iterator over '[section1]' entries yields both blocks in correct order.
            6. Values from each block match expected keys and values.
            7. StopIteration is correctly raised after the last section.
            8. Missing sections/options raise KeyError as expected.
        """
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        section1_but = p._data.find('section1').find('but')
        self.assertEqual(section1_but.value, 'also me')
        self.assertEqual(section1_but.line_number, 14)
        section1_help = p._data.find('section1').find('help')
        self.assertEqual(section1_help.value, 'yourself')
        self.assertEqual(section1_help.line_number, 13)
        section2_just = p._data.find('section2').find('just')
        self.assertEqual(section2_just.value, 'kidding')
        self.assertEqual(section2_just.line_number, 10)

        itr = p._data.finditer('section1')
        v = next(itr)
        self.assertEqual(v.find('help').value, 'yourself')
        self.assertEqual(v.find('but').value, 'also me')
        v = next(itr)
        self.assertEqual(v.find('help').value, 'me')
        self.assertEqual(v.find('I\'m').value, 'desperate')
        self.assertRaises(StopIteration, next, itr)

        self.assertRaises(KeyError, p._data.find, 'section')
        self.assertRaises(KeyError, p._data.find('section2').find, 'ahem')

    def test_lookup(self):
        """
        :id: 1b264c55-82f2-4c9a-a0a2-3f4f48f4c0ec
        :title: INIConfig attribute-style access returns correct values
        :description:
            Verifies that values can be accessed using attribute-style access
            (`config.section.option`) and that undefined options return an
            `Undefined` placeholder object.
        :tags: Tier 1
        :steps:
            1. Load a config string with multiple sections and options.
            2. Access defined options using dot notation (e.g., `p.section1.help`).
            3. Access a key with an apostrophe via `getattr()`.
            4. Access options that are not defined.
        :expectedresults:
            1. Configuration is parsed correctly.
            2. All defined keys return their correct values using attribute-style
                access.
            3. Special character keys (like `"I'm"`) are accessible via `getattr`.
            4. Accessing undefined options returns an `Undefined` instance.
        """
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        self.assertEqual(p.section1.help, 'yourself')
        self.assertEqual(p.section1.but, 'also me')
        self.assertEqual(getattr(p.section1, 'I\'m'), 'desperate')
        self.assertEqual(p.section2.just, 'kidding')

        self.assertEqual(p.section1.just.__class__, config.Undefined)
        self.assertEqual(p.section2.help.__class__, config.Undefined)

    def test_newsection(self):
        """
        :id: 19f37957-7ef1-4db3-b924-d60e32ccf038
        :title: New sections and options can be added using multiple access styles
        :description:
            Verifies that new sections and options can be added dynamically using various
            syntaxes including attribute-style, dictionary-style, and mixed forms.
        :tags: Tier 1
        :steps:
            1. Load the configuration string into an INIConfig object.
            2. Add a new section and key using dot notation (`p.new1.created = 1`).
            3. Add a new section and key using `getattr()` and `setattr()`.
            4. Add a new section and key using dictionary-style access '(`p.new3['created'] = 1`)'.
            5. Add a new section and key using bracket and attribute '(`p['new4'].created = 1`)'.
            6. Add a new section and key using double-bracket dictionary access.
            7. Retrieve all newly added values to confirm they were stored.
        :expectedresults:
            1. Configuration is parsed successfully.
            2. Section and key are added using dot notation.
            3. Section and key are added using dynamic attribute access.
            4. Section and key are added using dictionary access.
            5. Mixed syntax access adds key successfully.
            6. All key-value pairs are added correctly.
            7. Each key returns the expected value when accessed.
        """
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        p.new1.created = 1
        setattr(getattr(p, 'new2'), 'created', 1)
        p.new3['created'] = 1
        p['new4'].created = 1
        p['new5']['created'] = 1
        self.assertEqual(p.new1.created, 1)
        self.assertEqual(p.new2.created, 1)
        self.assertEqual(p.new3.created, 1)
        self.assertEqual(p.new4.created, 1)
        self.assertEqual(p.new5.created, 1)

    def test_order(self):
        """
        :id: a7e8cabc-3c29-4692-8b52-22570cdb2f46
        :title: INIConfig preserves the order of sections and options
        :description:
            Ensures that when iterating over sections and options, the original order
            in the config is maintained.
        :tags: Tier 1
        :steps:
            1. Load the configuration into an INIConfig object.
            2. Iterate over the top-level sections using `list(p)`.
            3. Iterate over the options in `section1` using `list(p.section1)`.
            4. Iterate over the options in `section2` using `list(p.section2)`.
        :expectedresults:
            1. The config is parsed correctly.
            2. The section order is preserved (`['section1', 'section2']`).
            3. The options in `section1` appear in the correct order.
            4. The options in `section2` appear in the correct order.
        """
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        self.assertEqual(list(p), ['section1','section2'])
        self.assertEqual(list(p.section1), ['help', "i'm", 'but'])
        self.assertEqual(list(p.section2), ['just'])

    def test_delete(self):
        """
        :id: 740aa7c4-6c2c-4e7d-bef4-5fd15a28b50d
        :title: Deleting sections and options updates the config structure and string output
        :description:
            Verifies that deleting options and sections removes them from the
            structure and updates the string representation accordingly, while
            preserving remaining content and formatting.
        :tags: Tier 1
        :steps:
            1. Load the config string into an INIConfig object.
            2. Delete the option `help` from `section1`.
            3. Convert the config to a string and verify the output.
            4. Delete the entire section `section2`.
            5. Convert the config again and verify the final output.
        :expectedresults:
            1. Config is parsed without error.
            2. The option `help` is removed from the first section1 block.
            3. String output reflects the removal and retains formatting
                and comments.
            4. Section2 is fully removed from the config.
            5. Final output string reflects both changes while preserving
                formatting of remaining content.
        """
        sio = StringIO(self.s1)
        p = ini.INIConfig(sio)
        del p.section1.help
        self.assertEqual(list(p.section1), ["i'm", 'but'])
        self.assertEqual(str(p), """
[section1]
I'm  = desperate     ; really!

[section2]
# comment and empty line before the first option

just = what?
just = kidding

[section1]
but = also me
""")
        del p.section2
        self.assertEqual(str(p), """
[section1]
I'm  = desperate     ; really!


[section1]
but = also me
""")

    def check_order(self, c):
        sio = StringIO(self.s1)
        c = c({'pi':'3.14153'})
        c.readfp(sio)
        self.assertEqual(c.sections(), ['section1','section2'])
        self.assertEqual(c.options('section1'), ['help', "i'm", 'but', 'pi'])
        self.assertEqual(c.items('section1'), [
            ('help', 'yourself'),
            ("i'm", 'desperate'),
            ('but', 'also me'),
            ('pi', '3.14153'),
        ])

    def test_compat_order(self):
        """
        :id: 2fd01fc8-d891-49c5-a7d7-1c8b5d501af0
        :title: ConfigParser compatibility preserves section and option order
        :description:
            Verifies that `RawConfigParser` and `ConfigParser` from the
            iniparse compatibility layer preserve the correct order of sections
            and options and correctly merge default values.
        :tags: Tier 1
        :steps:
            1. Initialize the parser with a default option using `{'pi': '3.14153'}`.
            2. Read the configuration string using `.readfp()`.
            3. List all section names and assert their order.
            4. List all option names in section1 and assert their order including defaults.
            5. List all items (key-value pairs) in section1 and assert the content and order.
        :expectedresults:
            1. The parser is initialized correctly with default values.
            2. Configuration is read without errors.
            3. Section order matches expected order from the config.
            4. All expected options are present and ordered as written.
            5. Default values appear last and are included in the item list with correct values.
        """
        self.check_order(compat.RawConfigParser)
        self.check_order(compat.ConfigParser)

    inv = (
("""
# values must be in a section
value = 5
""",
"""
# values must be in a section
#value = 5
"""),
("""
# continuation lines only allowed after options
[section]
op1 = qwert
    yuiop
op2 = qwert

    yuiop
op3 = qwert
# yup
    yuiop

[another section]
    hmmm
""",
"""
# continuation lines only allowed after options
[section]
op1 = qwert
    yuiop
op2 = qwert

    yuiop
op3 = qwert
# yup
    yuiop

[another section]
#    hmmm
"""))

    def test_invalid(self):
        """
        :id: e6d2ccfb-1b42-4cfd-81c4-e3cfa0e9f7be
        :title: INIConfig handles invalid input lines by converting them to comments
        :description:
            Verifies that invalid INI syntax such as values outside sections or
            misplaced continuation lines are preserved as commented lines when
            `parse_exc=False` is used.
        :tags: Tier 1
        :steps:
            1. Define two configuration strings with invalid syntax: A value outside
                any section and Continuation lines not following any option.
            2. Load each configuration using `INIConfig(StringIO(...), parse_exc=False)`.
            3. Convert each loaded configuration back to a string.
            4. Compare the string output to expected versions where invalid lines
                are commented out.
        :expectedresults:
            1. Input strings are created and contain intentional syntax errors.
            2. INIConfig loads the input without raising exceptions due to `parse_exc=False`.
            3. Output string conversion succeeds.
            4. Invalid lines are preserved and transformed into comments in the final output.
        """
        for (org, mod) in self.inv:
            ip = ini.INIConfig(StringIO(org), parse_exc=False)
            self.assertEqual(str(ip), mod)

    # test multi-line values
    s2 = (
"""
[section]
option =
  foo
  bar

  baz
  yam
"""
)

    s3 = (
"""
[section]
option =
  foo
  bar
  mum

  baz
  yam
"""
)

    def test_option_continuation(self):
        """
        :id: 3aa8a403-f129-44b9-b8b7-52c2b3cc0e4f
        :title: INIConfig preserves and updates multi-line option values
        :description:
            Verifies that multi-line option values are preserved during parsing and
            can be updated programmatically while maintaining formatting.
        :tags: Tier 1
        :steps:
            1. Load a configuration string with a single option value spread over multiple lines.
            2. Confirm that converting the config back to a string yields the same format.
            3. Parse the multi-line value using .split.
            4. Modify the value by inserting a new line.
            5. Update the config with the new value.
            6. Convert the config to a string and verify the updated format.
        :expectedresults:
            1. Configuration is parsed successfully and contains a multi-line value.
            2. The string representation of the config matches the original input.
            3. The value is correctly split into a list of lines.
            4. A new line is inserted into the correct position.
            5. The modified value is saved back to the config without error.
            6. The output string reflects the updated multi-line value and preserves formatting.
        """
        ip = ini.INIConfig(StringIO(self.s2))
        self.assertEqual(str(ip), self.s2)
        value = ip.section.option.split('\n')
        value.insert(3, 'mum')
        ip.section.option = '\n'.join(value)
        self.assertEqual(str(ip), self.s3)

    s5 = (
"""
[section]
option =
  foo
  bar
"""
)

    s6 = (
"""
[section]
option =


  foo



another = baz
"""
)

    def test_option_continuation_single(self):
        """
        :id: 52fa9d9a-4f7c-43a0-9b84-9c3f005f6632
        :title: INIConfig handles sparse multi-line values with empty lines
        :description:
            Verifies that an option value consisting of a multi-line string with
            blank lines is preserved correctly when parsed, modified, and serialized.
        :tags: Tier 1
        :steps:
            1. Load a configuration string where an option's value
                spans multiple lines.
            2. Confirm that converting the config back to a string matches
                the original input.
            3. Update the value with additional blank lines and content between them.
            4. Add another option to the section.
            5. Convert the updated config to a string.
            6. Verify that the final output preserves the new spacing and both options.
        :expectedresults:
            1. Configuration is parsed and multi-line value is detected.
            2. Output string matches the original formatting.
            3. Updated value with blank lines is assigned successfully.
            4. Additional option is added without error.
            5. Config is converted to string without formatting issues.
            6. Output includes both the updated multi-line value and the
                new option, with correct spacing.
        """
        ip = ini.INIConfig(StringIO(self.s5))
        self.assertEqual(str(ip), self.s5)
        ip.section.option = '\n'.join(['', '', '', 'foo', '', '', ''])
        ip.section.another = 'baz'
        self.assertEqual(str(ip), self.s6)
