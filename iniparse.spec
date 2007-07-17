%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           iniparse
Version:        0.2
Release:        1%{?dist}
Summary:        Python Module to Accessing and Modifying Configuration Data in ini files
Group:          Development/Libraries
License:        MIT
URL:            http://code.google.com/p/iniparse/
Source0:        http://iniparse.googlecode.com/files/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: python-setuptools  

BuildArch: noarch

%description
cfgparse is a Python module that provides mechanisms for managing
configuration information. It is backward compatible with ConfigParser,
preserves structure of INI files, and allows convenient access to data.
Compatibility with ConfigParser has been tested using the unit tests
included with Python-2.3.4

%prep
%setup -q


%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README LICENSE-PSF LICENSE Changelog html/*
%{python_sitelib}/%{name}



%changelog
* Tue Jul 17 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.2-1
- Release 0.2
- Added html/* to %%doc
* Fri Jul 13 2007 Tim Lauridsen <timlau@fedoraproject.org> - 0.1-1
- Initial build.
