%global _vpath_srcdir .
%global _vpath_builddir %{_target_platform}
%global __global_cflags  %{optflags}
%global __global_cxxflags  %{optflags}
%global __global_fflags  %{optflags} -I%_fmoddir
%global __global_fcflags %{optflags} -I%_fmoddir
%global __global_ldflags -Wl,-z,relro

Name:           dbus-broker
Version:        21
Release:        1%{?dist}
Summary:        Linux D-Bus Message Broker
License:        ASL 2.0
Vendor:         VMware, Inc.
Distribution:   Photon
Group:          System Environment/Security

URL:            https://github.com/bus1/dbus-broker
Source0:        https://github.com/bus1/dbus-broker/releases/download/v%{version}/dbus-broker-%{version}.tar.xz

Provides:       bundled(c-dvar) = 1
Provides:       bundled(c-ini) = 1
Provides:       bundled(c-list) = 3
Provides:       bundled(c-rbtree) = 3
Provides:       bundled(c-shquote) = 1

%{?systemd_requires}
BuildRequires:  pkgconfig(audit)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(libcap-ng)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  gcc
BuildRequires:  glibc-devel
BuildRequires:  meson
BuildRequires:  python3-docutils

Requires(post): /usr/bin/systemctl

# for triggerpostun
Requires:       /usr/bin/systemctl

%description
dbus-broker is an implementation of a message bus as defined by the D-Bus
specification. Its aim is to provide high performance and reliability, while
keeping compatibility to the D-Bus reference implementation. It is exclusively
written for Linux systems, and makes use of many modern features provided by
recent Linux kernel releases.

%prep
%setup -n %{name}-%{version}

%build
%meson -Daudit=true
%meson_build

%install
%meson_install

%check
%meson_test

%post
if [ $1 -eq 1 ] ; then
        if systemctl is-enabled -q dbus.service; then
                mkdir -p /run/systemd/system-generators/
                cat >>/run/systemd/system-generators/dbus-symlink-generator <<EOF
#!/bin/sh
ln -s /usr/lib/systemd/system/dbus.service \$2/dbus.service
EOF
                chmod +x /run/systemd/system-generators/dbus-symlink-generator
        fi

        if systemctl is-enabled -q --global dbus.service; then
                mkdir -p /run/systemd/user-generators/
                cat >>/run/systemd/user-generators/dbus-symlink-generator <<EOF
#!/bin/sh
ln -s /usr/lib/systemd/user/dbus.service \$2/dbus.service
EOF
                chmod +x /run/systemd/user-generators/dbus-symlink-generator
        fi

        systemctl --no-reload -q          disable dbus.service || :
        systemctl --no-reload -q --global disable dbus.service || :
        systemctl --no-reload -q          enable dbus-broker.service || :
        systemctl --no-reload -q --global enable dbus-broker.service || :
fi

%journal_catalog_update
%preun
%systemd_preun dbus-broker.service
%systemd_user_preun dbus-broker.service

%postun
%systemd_postun dbus-broker.service
%systemd_user_postun dbus-broker.service

%files
%license AUTHORS
%license LICENSE
%{_bindir}/dbus-broker
%{_bindir}/dbus-broker-launch
%{_journalcatalogdir}/dbus-broker.catalog
%{_journalcatalogdir}/dbus-broker-launch.catalog
%{_unitdir}/dbus-broker.service
%{_userunitdir}/dbus-broker.service

%changelog
* Sun Sep 08 2019 Susant Sahani <ssahani@vmware.com> - 1-1
- Initial RPM release
