#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1'

setup(name ='cfgparse',
      version = VERSION,
      description = 'Accessing and Modifying Configuration Data',
      author = 'Paramjit Oberoi',
      author_email = 'param@cs.wisc.edu',
      url = 'http://code.google.com/p/iniparse/',
      license = 'MIT',
      long_description = '''
cfgparse is a Python module that provides mechanisms for managing
configuration information. It is backward compatible with ConfigParser,
preserves structure of INI files, and allows convenient access to data.
Compatibility with ConfigParser has been tested using the unit tests
included with Python-2.3.4.
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
      packages = ['iniparse'],
      data_files = [
        ('share/doc/iniparse-%s' % VERSION, ['README', 'LICENSE-PSF',
                                             'LICENSE', 'Changelog',
                                             'html/index.html',
                                             'html/style.css',
                                             'html/iniparse.html',
                                             'html/iniparse.compat.html',
                                             'html/iniparse.config.html',
                                             'html/iniparse.ini.html']),
      ],
)

