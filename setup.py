#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1'

setup(name ='cfgparse',
      version = VERSION,
      description = 'Accessing and Modifying Configuration Data',
      author = 'Paramjit Oberoi',
      author_email = 'param@cs.wisc.edu',
      url = 'http://www.cs.wisc.edu/~param/software/cfgparse/',
      license = 'MIT',
      long_description = '''
Configuration management module that is compatiable with ConfigParser
while preserving the structure of INI files (i.e. order of sections &
options, comments, blank lines) and allows convenient access to data.
      '''.strip(),
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      packages = ['cfgparse'],
      data_files = [
        ('share/doc/cfgparse-%s' % VERSION, ['README', 'LICENSE-PSF',
                                             'LICENSE', 'Changelog',
                                             'html/index.html',
                                             'html/style.css',
                                             'html/cfgparse.html',
                                             'html/cfgparse.compat.html',
                                             'html/cfgparse.config.html',
                                             'html/cfgparse.iniparser.html']),
      ],
)

