from betelgeuse import default_config

TESTCASE_CUSTOM_FIELDS = default_config.TESTCASE_CUSTOM_FIELDS + (
    "casecomponent",
    "subsystemteam",
    "polarionincludeskipped",
    "polarionlookupmethod",
    "polarionprojectid",
)

DEFAULT_CASECOMPONENT_VALUE = ""
DEFAULT_SUBSYSTEMTEAM_VALUE = ""
POLARION_INCLUDE_SKIPED = ""
POLARION_LOOKUP_METHOD = ""
POLARION_PROJECT_ID = ""
