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
from textwrap import dedent
from io import StringIO

from iniparse import tidy, INIConfig
from iniparse.compat import ConfigParser


class TestTidy(unittest.TestCase):
    def setUp(self):
        self.cfg = INIConfig()

    def test_empty_file(self):
        """
        :id: 8b72c86e-f1a0-4e1e-acc3-548c17d1a489
        :title: Tidy leaves empty INIConfig unchanged
        :description:
            Verifies that running tidy on an empty INIConfig does not
            introduce any content or whitespace.
        :tags: Tier 2
        :steps:
            1. Create an empty INIConfig object.
            2. Convert it to a string and verify it is empty.
            3. Apply the tidy() function to the config.
            4. Convert the config to a string again.
        :expectedresults:
            1. The config is initialized successfully and is empty.
            2. Initial string output is an empty string.
            3. tidy() runs without errors.
            4. Final string output remains an empty string.
        """
        self.assertEqual(str(self.cfg), '')
        tidy(self.cfg)
        self.assertEqual(str(self.cfg), '')

    def test_last_line(self):
        """
        :id: 6a573735-b8ea-4f84-86cc-3c70f90dc248
        :title: Tidy appends newline to end of file if missing
        :description:
            Ensures that tidy adds a trailing newline to the end of a config
            file if one is not present.
        :tags: Tier 2
        :steps:
            1. Create a config with one section and one option.
            2. Convert it to a string and verify it ends without a newline.
            3. Apply tidy() to the config.
            4. Verify that the final string output ends with a newline.
        :expectedresults:
            1. Config is created and contains valid content.
            2. Initial output string does not end with a newline.
            3. tidy() appends a newline during cleanup.
            4. Final output ends with a single newline.
        """
        self.cfg.newsection.newproperty = "Ok"
        self.assertEqual(str(self.cfg), dedent("""\
            [newsection]
            newproperty = Ok"""))
        tidy(self.cfg)
        self.assertEqual(str(self.cfg), dedent("""\
            [newsection]
            newproperty = Ok
            """))

    def test_first_line(self):
        """
        :id: 40b08735-5bc6-489b-a3b8-84d61f30cf4f
        :title: Tidy removes empty lines before the first section
        :description:
            Verifies that tidy removes leading blank lines from the beginning
            of the config.
        :tags: Tier 2
        :steps:
            1. Create a config string with blank lines before the first section.
            2. Load the config into an INIConfig object.
            3. Apply tidy() to clean the config.
            4. Convert the config to a string and verify that it starts with
                the section header.
        :expectedresults:
            1. Config string is successfully created
            2. Config string with leading whitespace is loaded successfully.
            3. tidy() removes the initial blank lines.
            4. Final output starts directly with the section header.
        """
        s = dedent("""\

                [newsection]
                newproperty = Ok
                """)
        self.cfg._readfp(StringIO(s))
        tidy(self.cfg)
        self.assertEqual(str(self.cfg), dedent("""\
                [newsection]
                newproperty = Ok
                """))

    def test_remove_newlines(self):
        """
        :id: d1a9b12d-f6ec-4e4c-bf1e-d97b3f47ab0c
        :title: Tidy removes unnecessary blank lines but preserves continuation lines
        :description:
            Verifies that tidy removes excessive blank lines between sections and options,
            while preserving properly indented continuation lines.
        :tags: Tier 1
        :steps:
            1. Create a config string with excessive blank lines and continuation lines.
            2. Load the config into an INIConfig object.
            3. Apply tidy() to clean the formatting.
            4. Convert the config to a string and compare to expected cleaned format.
        :expectedresults:
            1. Config is parsed with both extra blank lines and continuation lines.
            2. tidy() removes blank lines that do not serve a formatting purpose.
            3. Continuation lines are preserved without changes.
            4. Final output has a clean and compact structure without affecting data.
        """
        s = dedent("""\


                [newsection]
                newproperty = Ok




                [newsection2]

                newproperty2 = Ok


                newproperty3 = yup


                [newsection4]


                # remove blank lines, but leave continuation lines unharmed

                a = 1

                b = l1
                 l2


                # asdf
                 l5

                c = 2


                """)
        self.cfg._readfp(StringIO(s))
        tidy(self.cfg)
        self.assertEqual(str(self.cfg), dedent("""\
                [newsection]
                newproperty = Ok

                [newsection2]
                newproperty2 = Ok

                newproperty3 = yup

                [newsection4]
                # remove blank lines, but leave continuation lines unharmed

                a = 1

                b = l1
                 l2


                # asdf
                 l5

                c = 2
                """))

    def test_compat(self):
        """
        :id: 5040a7c7-61de-466a-abe1-4c15ef12bfcf
        :title: Tidy cleans config created via ConfigParser and preserves structure
        :description:
            Verifies that tidy can be used with a config object from
            `iniparse.compat.ConfigParser` and correctly removes unnecessary newlines
            between sections and options.
        :tags: Tier 2
        :steps:
            1. Define a multi-section INI string with excessive blank lines.
            2. Parse the config using ConfigParser and `.readfp()`.
            3. Apply the tidy() function to the ConfigParser object.
            4. Convert the cleaned config to string using `str(cfg.data)`.
            5. Compare the output string with the expected tidy format.
        :expectedresults:
            1. The config string is successfully defined for testing.
            2. ConfigParser loads the config and parses it correctly.
            3. tidy() removes the excessive newlines without affecting data structure.
            4. The config is successfully converted back to a string.
            5. The final output matches the expected tidy version in both structure and content.
        """
        s = dedent("""
            [sec1]
            a=1


            [sec2]

            b=2

            c=3


            """)
        cfg = ConfigParser()
        cfg.readfp(StringIO(s))
        tidy(cfg)
        self.assertEqual(str(cfg.data), dedent("""\
            [sec1]
            a=1

            [sec2]
            b=2

            c=3
            """))
