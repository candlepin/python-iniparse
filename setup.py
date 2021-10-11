#!/usr/bin/env python

from setuptools import setup

VERSION = '0.5'

setup(
      version = VERSION,
      data_files = [
        ('share/doc/iniparse-%s' % VERSION, ['README.md', 'LICENSE-PSF',
                                             'LICENSE', 'Changelog',
                                             'html/index.html',
                                             'html/style.css',
                                             ]),
      ],
)
