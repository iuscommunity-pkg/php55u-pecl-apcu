# spec file for php-pecl-apcu
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?php_inidir:  %{expand: %%global php_inidir  %{_sysconfdir}/php.d}}
%{!?php_incldir: %{expand: %%global php_incldir %{_includedir}/php}}
%{!?__pecl:      %{expand: %%global __pecl      %{_bindir}/pecl}}
%global pecl_name apcu
%global with_zts  0%{?__ztsphp:1}
%define php_base php55u

Name:           %{php_base}-pecl-apcu
Summary:        APC User Cache
Version:        4.0.6
Release:        1.ius%{?dist}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source1:        %{pecl_name}.ini
Source2:        %{pecl_name}-panel.conf
Source3:        %{pecl_name}.conf.php

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/APCu

BuildRequires:  %{php_base}-devel
BuildRequires:  %{php_base}-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       %{php_base}(zend-abi) = %{php_zend_api}
Requires:       %{php_base}(api) = %{php_core_api}

Obsoletes:      %{php_base}-apcu < 4.0.0-1
Conflicts:      %{php_base}-pecl-apc %{php_base}-xcache
Conflicts:      %{php_base}-mmcache %{php_base}-eaccelerator

Provides:       php-apcu = %{version}
Provides:       %{php_base}-apcu = %{version}
Provides:       php-apcu%{?_isa} = %{version}
Provides:       %{php_base}-apcu%{?_isa} = %{version}
Provides:       php-pecl(apcu) = %{version}
Provides:       %{php_base}-pecl(apcu) = %{version}
Provides:       php-pecl(apcu)%{?_isa} = %{version}
Provides:       %{php_base}-pecl(apcu)%{?_isa} = %{version}

# Same provides than APC, this is a drop in replacement
Provides:       php-apc = %{version}
Provides:       %{php_base}-apc = %{version}
Provides:       php-apc%{?_isa} = %{version}
Provides:       %{php_base}-apc%{?_isa} = %{version}
Provides:       php-pecl-apc = %{version}
Provides:       %{php_base}-pecl-apc = %{version}
Provides:       php-pecl-apc%{?_isa} = %{version}
Provides:       %{php_base}-pecl-apc%{?_isa} = %{version}
Provides:       php-pecl(APC) = %{version}
Provides:       %{php_base}-pecl(APC) = %{version}
Provides:       php-pecl(APC)%{?_isa} = %{version}
Provides:       %{php_base}-pecl(APC)%{?_isa} = %{version}

# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}


%description
APCu is userland caching: APC stripped of opcode caching in preparation
for the deployment of Zend OPcache as the primary solution to opcode
caching in future versions of PHP.

APCu has a revised and simplified codebase, by the time the PECL release
is available, every part of APCu being used will have received review and
where necessary or appropriate, changes.

Simplifying and documenting the API of APCu completely removes the barrier
to maintenance and development of APCu in the future, and additionally allows
us to make optimizations not possible previously because of APC's inherent
complexity.

APCu only supports userland caching (and dumping) of variables, providing an
upgrade path for the future. When O+ takes over, many will be tempted to use
3rd party solutions to userland caching, possibly even distributed solutions;
this would be a grave error. The tried and tested APC codebase provides far
superior support for local storage of PHP variables.


%package devel
Summary:       APCu developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{php_base}-devel%{?_isa}
Obsoletes:      php-pecl-apc-devel < 4
Provides:       php-pecl-apc-devel = %{version}-%{release}
Provides:       php-pecl-apc-devel%{?_isa} = %{version}-%{release}

%description devel
These are the files needed to compile programs using APCu.


%package -n apcu-panel55u
Summary:       APCu control panel
Group:         Applications/Internet
BuildArch:     noarch
Requires:      %{name} = %{version}-%{release}
Requires:      mod_php55u, httpd, %{php_base}-gd
Obsoletes:      apc-panel < 4
Provides:       apc-devel = %{version}-%{release}

%description  -n apcu-panel55u
This package provides the APCu control panel, with Apache
configuration, available on http://localhost/apcu-panel/


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_APCU_VERSION/{s/.* "//;s/".*$//;p}' php_apc.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi
cd ..

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{SOURCE1} %{buildroot}%{php_inidir}/%{pecl_name}.ini

# Install the ZTS stuff
%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Install the Control Panel
# Pages
install -d -m 755 %{buildroot}%{_datadir}/apcu-panel
sed -e s:apc.conf.php:%{_sysconfdir}/apcu-panel/conf.php:g \
    NTS/apc.php >%{buildroot}%{_datadir}/apcu-panel/index.php
# Apache config
install -D -m 644 -p %{SOURCE2} \
        %{buildroot}%{_sysconfdir}/httpd/conf.d/apcu-panel.conf
# Panel config
install -D -m 644 -p %{SOURCE3} \
        %{buildroot}%{_sysconfdir}/apcu-panel/conf.php


%check
cd NTS

# Check than both extensions are reported (BC mode)
%{_bindir}/php -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apcu'
%{_bindir}/php -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apc$'

# Upstream test suite
TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php

%if %{with_zts}
cd ../ZTS

%{__ztsphp}    -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apcu'
%{__ztsphp}    -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apc$'

TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc NTS/{NOTICE,LICENSE,README.md}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}.so
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%endif

%files devel
%{php_incldir}/ext/%{pecl_name}
%if %{with_zts}
%{php_ztsincldir}/ext/%{pecl_name}
%endif

%files -n apcu-panel55u
%defattr(-,root,root,-)
# Need to restrict access, as it contains a clear password
%attr(750,apache,root) %dir %{_sysconfdir}/apcu-panel
%config(noreplace) %{_sysconfdir}/apcu-panel/conf.php
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcu-panel.conf
%{_datadir}/apcu-panel


%changelog
* Mon Jun 16 2014 Carl George <carl.george@rackspace.com> - 4.0.6-1.ius
- Latest upstream

* Wed Jun 11 2014 Carl George <carl.george@rackspace.com> - 4.0.5-1.ius
- Latest upstream

* Thu Apr 03 2014 Ben Harper <ben.harper@rackspace.com> - 4.0.4-2.ius
- updated requires from php-gd to %{php_base}-gd and mod_php to mod_php55u

* Wed Apr 02 2014 Ben Harper <ben.harper@rackspace.com> - 4.0.4-1.ius
- Latest sources from upstream
- update Sanity check in prep

* Mon Dec 16 2013 Ben Harper <ben.harper@rackspace.com> - 4.0.2-1.ius
- porting to IUS

* Tue Apr 30 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-1
- Update to 4.0.1
- add missing scriptlet
- fix Conflicts

* Thu Apr 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-2
- fix segfault when used from command line

* Wed Mar 27 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-1
- first pecl release
- rename from php-apcu to php-pecl-apcu

* Tue Mar 26 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.4.git4322fad
- new snapshot (test before release)

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.3.git647cb2b
- new snapshot with our pull request
- allow to run test suite simultaneously on 32/64 arch
- build warning free

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.2.git6d20302
- new snapshot with full APC compatibility

* Sat Mar 23 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.1.git44e8dd4
- initial package, version 4.0.0
