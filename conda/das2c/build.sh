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
	echo "$(pwd)/cdf: make CURSES=no SHARED=no OS=linux ENV=gnu all.build"
	cd cdf && make CURSES=no SHARED=no OS=linux ENV=gnu all.build
	cd ..
elif [ "$(uname)" == "Darwin" ] ; then
	# Spice intel libraries are not compatable with some macs due to missing 
	# symbols. On mac we have to build the software manually
	echo "$(pwd)/spice: csh -c ./makeall.csh"
	cd spice && csh -c ./makeall.csh
	cd ..

	echo "$(pwd)/cdf: make CURSES=no SHARED=no OS=macosx ENV=x86_64 all.build"
	cd cdf && make CURSES=no SHARED=no OS=macosx ENV=x86_64 all.build
	cd ..

else
	echo "***************** Hi There *****************************"
	echo "*     Update the build script for this environment     *"
	echo "********************************************************"
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
