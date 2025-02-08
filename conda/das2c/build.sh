#!/usr/bin/env bash


# Meta.yaml sets the top level folders
CDF_INC=../cdf/src/include
CDF_LIB=../cdf/src/lib/libcdf.a

SPICE_INC=../spice/include
SPICE_LIB=../spice/lib/cspice.a

# Don't differentiate output & install directories manually.  This does
# not affect which makefiles are selected only build and install directories.
N_ARCH=/

export N_ARCH

if [ "$(uname)" == "Linux" ] ; then
	echo "$(pwd): make CURSES=no SHARED=no OS=linux ENV=gnu all.build"
	cd cdf && make CURSES=no SHARED=no OS=linux ENV=gnu all.build
	cd ..
else
	echo "Update the build script for non-linux environments"
	exit 3
fi

cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB}
cd ..
cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB} test
cd ..
cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB} test_spice
cd ..
cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB} test_cdf
cd ..
cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB} install
cd ..
cd das2c && make SPICE=yes CDF=yes CDF_INC=${CDF_INC} CDF_LIB=${CDF_LIB} CSPICE_INC=${SPICE_INC} CSPICE_LIB=${SPICE_LIB} install_cdf
cd ..
