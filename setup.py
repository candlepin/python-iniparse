#!/usr/bin/env python

from setuptools import setup

VERSION = "0.5"

setup(
    name="iniparse",
    version=VERSION,
    description="Accessing and Modifying INI files",
    author="Paramjit Oberoi",
    author_email="chainsaw@redhat.com",
    url="https://github.com/candlepin/python-iniparse",
    license="MIT",
    long_description="""\
iniparse is an INI parser for Python which is API compatible
with the standard library's ConfigParser, preserves structure of INI
files (order of sections & options, indentation, comments, and blank
lines are preserved when data is updated), and is more convenient to
use.""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=["iniparse"],
    data_files=[
        (
            "share/doc/iniparse-%s" % VERSION,
            [
                "README.md",
                "LICENSE-PSF",
                "LICENSE",
                "Changelog",
                "html/index.html",
                "html/style.css",
            ],
        ),
    ],
)
