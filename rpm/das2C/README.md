# das2C RPMs

Spec written against Rocky/RHEL 9 (rpm 4.16).  Produces:

* `das2C` -- the programs (`das1_*`, `das2_*`, `das3_*`, `das_fetch`) and the
  stream schemas in `/usr/share/das2C`
* `das2C-devel` -- `libdas3.a` and `/usr/include/das3`.  Static only, upstream
  does not ship a shared library.  Also provides `das2C-static`.
* `das2C-debuginfo`, `das2C-debugsource`

CSPICE and CDF are declared Sources and pre-staged in `%prep`, so the build
itself never downloads anything.  The SPICE and CDF programs are part of
the package; `--without spice` / `--without cdf` exist only for local test
builds.

The source package is `das2C-*.nosrc.rpm`, not `.src.rpm`.  NAIF forbids
redistributing the unmodified SPICE Toolkit without written clearance, so
`cspice.tar.Z` is marked `NoSource` and left out; anyone rebuilding gets it
from NAIF.  The binary RPMs are unaffected: NAIF explicitly allows linking
Toolkit code into a SPICE-based tool.  The CDF tarball's terms allow
redistribution, so it stays in.

The spec is `ExclusiveArch: x86_64`.  NAIF publishes a prebuilt CSPICE for
no other Linux architecture, and it vets each platform before supporting
it, so a CSPICE we built ourselves for aarch64 would be unvetted.  No
package for other arches beats one without `das3_spice`.

There are no patches.  das2C's `buildfiles/Linux.mak` takes `LDFLAGS` on the
native link line and builds its one `-O0` object with `-Wno-error`, so the
RHEL hardening flags work unpatched.  Releases before v3.0.4 needed both.

## Building

One time setup:
```bash
sudo dnf install gcc make rpm-build rpmdevtools rpmlint \
     expat-devel fftw-devel openssl-devel zlib-devel
```

Builds stay inside the dasPackage checkout, neither directory is in git:

* `tmp/rpmbuild` -- rpm's `_topdir`: downloaded tarballs (SOURCES) and the
  BUILD/BUILDROOT scratch trees.  Safe to delete.
* `dist/rpm` -- finished packages only, `RPMS/<arch>/` and `SRPMS/`, shared
  by every spec in this repo so one `createrepo_c dist/rpm` makes a local
  repo for packages that build against each other.

From the top of the dasPackage checkout:
```bash
T=$PWD/tmp/rpmbuild
D=$PWD/dist/rpm
mkdir -p $T/SOURCES
spectool -g -C $T/SOURCES rpm/das2C/das2C.spec    # das2C and CDF tarballs
curl -fL -o $T/SOURCES/cspice.tar.Z \
     https://naif.jpl.nasa.gov/pub/naif/toolkit/C/PC_Linux_GCC_64bit/packages/cspice.tar.Z
rpmbuild -ba --define "_topdir $T" \
     --define "_rpmdir $D/RPMS" --define "_srcrpmdir $D/SRPMS" \
     rpm/das2C/das2C.spec                          # nosrc + binary RPMs, runs make test
```

spectool (1.1.0 on Rocky 9) does not see `NoSource` entries, hence the curl.
A plain rpmbuild would download the missing file itself, since the spec
allows source fetching, but mock builds offline and needs it present.  Skip
the test suite with `--nocheck`.

To rebuild from the nosrc.rpm, `rpm -i --define "_topdir $T" das2C-*.nosrc.rpm`
(the spec lands in `$T/SPECS`, das2C and CDF tarballs in `$T/SOURCES`), do the
curl above, then run the rpmbuild above on `$T/SPECS/das2C.spec`.

For a clean-room build use mock with the spec and a SOURCES dir that has all
three tarballs (`mock --rebuild` on the nosrc.rpm alone would be missing
CSPICE).  Its result dir mixes logs in with the RPMs, so it goes under tmp:
```bash
mock -r rocky+epel-9-x86_64 --resultdir=$PWD/tmp/mock \
     --spec rpm/das2C/das2C.spec --sources $T/SOURCES
```

### Before a tag exists

To try the spec against an untagged commit, make the tarball GitHub would
produce and drop it in SOURCES under the name the spec expects:
```bash
git -C ../das2C archive --format=tar.gz --prefix=das2C-3.0.4/ HEAD \
    > $T/SOURCES/das2C-3.0.4.tar.gz
```
`git archive` also fills in `das3/ver_p.h` (export-subst), so the programs
report the commit they were built from.

## New releases

1. Set `upver` to the tag minus its `v` (`3.0.1`, or `3.1-pre1` for a
   pre-release: Version becomes `3.1~pre1`, which sorts before `3.1`)
2. Reset `Release` to 1, add a `%changelog` entry.  After `spectool -g`,
   compare `sha256sum` of the das2C tarball with the release's `.sha256` asset
   (Source0 is the release asset, not GitHub's regenerated `/archive/` tarball)
3. If upstream changed `LOC_CDF_DIST` in `buildfiles/Linux.mak`, update
   `cdf_dist` and the Source2 URL to match
4. NAIF replaces `cspice.tar.Z` in place on each toolkit release; if it has
   moved past N0067, update the `bundled(cspice)` version

## Spot check

```bash
sudo dnf install dist/rpm/RPMS/x86_64/das2C-3.0.4-1*.rpm
das2_psd -h
das3_info -h
```

Then from a das2C checkout or unpacked release tarball (`examples/` is not
installed):
```bash
cat examples/ex07_cassini_rpws_wbr.d2s | das2_psd 512 1 | das2_bin_avgsec 1 | das2_ascii -s 3 -r 3
```
Since the input file is only a second's worth of data, this should produce a
UTF-8 stream with only a single record with 257 items (i.e. 512/2 + 1).
