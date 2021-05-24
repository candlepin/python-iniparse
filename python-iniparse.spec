%global modname iniparse

# Use the same directory of the main package for subpackage licence and docs
%global _docdir_fmt %{name}

Name:           python-%{modname}
Version:        0.5
Release:        1%{?dist}
Summary:        Python Module for Accessing and Modifying Configuration Data in INI files
License:        MIT and Python
URL:            https://github.com/candlepin/python-iniparse
Source0:        python-%{modname}-%{version}.tar.gz

BuildArch: noarch

%global _description \
iniparse is an INI parser for Python which is API compatible\
with the standard library's ConfigParser, preserves structure of INI\
files (order of sections & options, indentation, comments, and blank\
lines are preserved when data is updated), and is more convenient to\
use.

%description %{_description}

%package -n python3-%{modname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{modname}}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
BuildRequires:  python3-test

%description -n python3-%{modname} %{_description}

Python 3 version.

%prep
%setup -q -n %{modname}-%{version}
chmod -c -x html/index.html

%build
%py3_build

%install
%py3_install
rm -vfr %{buildroot}%{_docdir}/*

%check
%{__python3} runtests.py

%files -n python3-%{modname}
%license LICENSE LICENSE-PSF
%doc README.md Changelog html/
%{python3_sitelib}/%{modname}/
%{python3_sitelib}/%{modname}-%{version}-*.egg-info/



%changelog
* Tue May 18 2021 Jiri Hnidek <jhnidek@redhat.com> - 0.5-1
- Release 0.5
- Moved project to https://github.com/candlepin/python-iniparse
- Added support for Python 3
* Sat Jun 12 2010 Paramjit Oberoi <param@cs.wisc.edu> - 0.4-1
- Release 0.4
* Sat Apr 17 2010 Paramjit Oberoi <param@cs.wisc.edu> - 0.3.2-1
- Release 0.3.2
* Mon Mar 2 2009 Paramjit Oberoi <param@cs.wisc.edu> - 0.3.1-1
- Release 0.3.1
* Fri Feb 27 2009 Paramjit Oberoi <param@cs.wisc.edu> - 0.3.0-1
- Release 0.3.0
* Tue Dec 6 2008 Paramjit Oberoi <param@cs.wisc.edu> - 0.2.4-1
- Release 0.2.4
- added egg-info file to %%files
* Tue Dec 11 2007 Paramjit Oberoi <param@cs.wisc.edu> - 0.2.3-1
- Release 0.2.3
* Tue Sep 24 2007 Paramjit Oberoi <param@cs.wisc.edu> - 0.2.2-1
- Release 0.2.2
* Tue Aug 7 2007 Paramjit Oberoi <param@cs.wisc.edu> - 0.2.1-1
- Release 0.2.1
* Fri Jul 27 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.2-3
- relocated doc to %{_docdir}/python-iniparse-%{version}
* Thu Jul 26 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.2-2
- changed name from iniparse to python-iniparse
* Tue Jul 17 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.2-1
- Release 0.2
- Added html/* to %%doc
* Fri Jul 13 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.1-1
- Initial build.
