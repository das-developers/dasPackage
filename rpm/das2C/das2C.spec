# das2C RPM spec, written against Rocky/RHEL 9 (rpm 4.16).
#
# Upstream's makefile curls CSPICE and CDF during the build.  Here both are
# declared Sources and pre-staged into the makefile's deps directory in %%prep
# so the build never touches the network (required under mock).  CSPICE is
# NoSource (see Source1), so the source package is a .nosrc.rpm.

# Upstream version string exactly as tagged, minus the leading "v".  For a
# pre-release set e.g. 3.0-pre8; Version gets 3.0~pre8 so that it sorts
# before the final 3.0 (rpm forbids '-' in Version anyway).
%global upver 3.0.4

# Both are on: das3_spice, das3_cdf, das3_from_cdf and das2_from_cdf are
# part of the package, not extras.  --without exists for local test builds.
%bcond_without spice
%bcond_without cdf

# Must equal LOC_CDF_DIST in upstream buildfiles/Linux.mak.  If they drift,
# the makefile does not find the staged copy and silently downloads its own
# version mid-build (or fails, under mock).
%global cdf_dist cdf39_1-dist

# Upstream names its build and download dirs build.$(N_ARCH), deps.$(N_ARCH);
# N_ARCH=/ (flat install layout) gives these.
%global deps_dir deps.

Name:           das2C
Version:        %{lua:print((string.gsub(rpm.expand("%{upver}"), "-", "~")))}
Release:        1%{?dist}
Summary:        das2 and das3 stream utilities and catalog client in C

# LGPL-2.1-only: das2C itself.  The rest is bundled code, see THIRD-PARTY.txt:
# tomlc17 (MIT), json.h (Unlicense), Bezanson utf8 (public domain), and the
# TT2000 code from NASA CDF, which is in the library whether or not CDF=yes.
%global lic_base LGPL-2.1-only AND MIT AND Unlicense AND LicenseRef-Fedora-Public-Domain AND LicenseRef-NASA-CDF
%if %{with spice}
License:        %{lic_base} AND LicenseRef-NAIF-CSPICE
%else
License:        %{lic_base}
%endif
URL:            https://github.com/das-developers/%{name}

# NAIF publishes a prebuilt CSPICE for x86_64 Linux only, and vets each
# platform before supporting it.  Building it ourselves for other arches
# would ship an unvetted CSPICE, so no package there rather than one
# without das3_spice.
ExclusiveArch:  x86_64

# Distro packagers must not fetch sources at build time; for our own repo
# letting rpmbuild download them is a convenience worth having.
%undefine _disable_source_fetch

# The release asset, not GitHub's /archive/ tarball: same contents, but the
# asset is a fixed file with a published .sha256, while /archive/ tarballs
# are regenerated on demand and their checksums have changed before.
Source0:        %{url}/releases/download/v%{upver}/%{name}-%{upver}.tar.gz
%if %{with spice}
# Unversioned upstream URL: NAIF replaces this file in place on each toolkit
# release (N0067 at time of writing).  Check bundled(cspice) below when it
# changes.
Source1:        https://naif.jpl.nasa.gov/pub/naif/toolkit/C/PC_Linux_GCC_64bit/packages/cspice.tar.Z
# NAIF forbids redistributing the unmodified Toolkit without written
# clearance (naif.jpl.nasa.gov/naif/rules.html), and a verbatim cspice.tar.Z
# inside the source package is exactly that.  Linking it into das3_spice is
# explicitly allowed, so only the source package is affected: it leaves this
# file out, and rebuilders fetch it from NAIF themselves.
NoSource:       1
%endif
%if %{with cdf}
Source2:        https://spdf.gsfc.nasa.gov/pub/software/cdf/dist/cdf39_1/linux/%{cdf_dist}-cdf.tar.gz
%endif

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  gzip
BuildRequires:  expat-devel
BuildRequires:  fftw-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
# For the %%check golden-file scripts
BuildRequires:  bash
BuildRequires:  diffutils

# Runtime library Requires (expat, fftw-libs, ...) are generated from the
# ELF sonames, no need to list them.

Provides:       bundled(tomlc17)
Provides:       bundled(json.h)
%if %{with spice}
Provides:       bundled(cspice) = N0067
%endif
%if %{with cdf}
Provides:       bundled(cdf) = 3.9.1
%endif

%description
The das2C package supports generation and processing of das2 and das3 data
streams.  It is also a das catalog client and handles dynamic source ID to URL
mapping.  This package contains the command line programs and stream schemas.

%package        devel
Summary:        Static library and headers for developing with %{name}
# Upstream ships only libdas3.a, no shared object: a .so would mean supporting
# its ABI.  Per packaging convention a static-only -devel provides -static.
# Nothing here needs the programs, so no Requires on the base package.
Provides:       %{name}-static = %{version}-%{release}
# A static link of libdas3.a needs these on the link line.
Requires:       expat-devel
Requires:       fftw-devel
Requires:       openssl-devel
Requires:       zlib-devel

%description    devel
The %{name}-devel package contains the libdas3 static library and header
files for developing applications that use %{name}.  Link with
-ldas3 -lfftw3 -lexpat -lssl -lcrypto -lz -lm -lpthread.  Programs that
include das3/spice.h must also supply their own CSPICE.


# Everything the makefile needs on every invocation.  build, install and test
# must all see the same values, or make decides things are out of date.
%global das_make \\\
	PREFIX=%{_prefix} N_ARCH=/ \\\
	INST_NAT_BIN=%{_bindir} INST_NAT_LIB=%{_libdir} \\\
	INST_INC=%{_includedir} INST_SHARE=%{_datadir} \\\
	SPICE=%{?with_spice:yes}%{!?with_spice:no} \\\
	CDF=%{?with_cdf:yes}%{!?with_cdf:no} \\\
	OPTFLAGS="%{optflags}"

# LDFLAGS goes in through the environment, not the command line.  Command
# line variables ride MAKEFLAGS into the CDF sub-make and replace CDF's own
# LDFLAGS (which carries -shared, so libcdf.so fails to link).  An env value
# loses to CDF's assignment but is seen by das2C, which never assigns it.
%global das_env LDFLAGS="%{build_ldflags}"


%prep
%autosetup -p1 -n %{name}-%{upver}

# Stage the dependency sources where the makefile's own download rules would
# leave them, so those rules see their targets present and do nothing.
mkdir -p %{deps_dir}
%if %{with spice}
# gzip reads compress(1) .Z files, saves a BuildRequires on ncompress.
gzip -dc %{SOURCE1} > %{deps_dir}/cspice.tar
%endif
%if %{with cdf}
tar -xzf %{SOURCE2} -C %{deps_dir}
%endif


%build
%{das_env} %make_build %{das_make}


%install
# dev_install, not install: plain install omits the library and headers
%{das_env} make dev_install DESTDIR=%{buildroot} %{das_make}

# Upstream installs group writable (664/775) for its shared-tree use; that
# is wrong for system files.
find %{buildroot} -type f -perm /022 -exec chmod go-w {} +


%check
%{das_env} make test %{das_make}


%files
# Directory modes spelled out: a build under a setgid home (shared group
# trees do this) would otherwise package every directory as 2755.
%defattr(-,root,root,0755)
%license LICENSE THIRD-PARTY.txt LICENSES
%doc README.md
%{_bindir}/das1_*
%{_bindir}/das2_*
%{_bindir}/das3_*
%{_bindir}/das_fetch
%{_datadir}/%{name}/

%files devel
%defattr(-,root,root,0755)
%{_includedir}/das3/
%{_libdir}/libdas3.a


%changelog
* Wed Nov 11 2026 Chris Piker <chris-piker@uiowa.edu> - 3.0.4-1
- das2C 3.0.4, the first v3.0 release.  The library is now libdas3, headers
  move to /usr/include/das3
- Static library only, libdas2.3.so is gone, nothing replaces it
- CSPICE and CDF are built in from declared Sources, adding das3_spice,
  das3_cdf, das3_from_cdf and das2_from_cdf
- CSPICE is NoSource, so the source package is a nosrc.rpm: NAIF forbids
  redistributing the unmodified Toolkit
- Stream schemas installed under /usr/share/das2C
- Drop the DESTDIR patch, upstream supports staged installs now
- Run the upstream test suite in check
- x86_64 only, the one Linux arch NAIF publishes CSPICE for

* Wed Feb 12 2025 Chris Piker <chris-piker@uiowa.edu> - 3.0~pre5-1
- Update to v3.0-pre5

* Mon Nov 06 2023 Chris Piker <chris-piker@uiowa.edu> - 2.3.0-1
- Update to v2.3.0

* Sun Nov 28 2021 Chris Piker <chris-piker@uiowa.edu> - 2.3~pre4-1
- First das2C package
