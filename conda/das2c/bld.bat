set N_ARCH=\

set CSPICE_INC=..\spice\include
set CSPICE_LIB=..\spice\lib\cspice.lib
set CDF_INC=..\cdf\include
set CDF_LIB=..\cdf\lib\libcdf.lib

cd das2c

nmake.exe /nologo /f buildfiles\Windows.mak clean

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 1
)

nmake.exe /nologo /f buildfiles\Windows.mak SPICE=yes CDF=yes build

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 2
)

nmake.exe /nologo /f buildfiles\Windows.mak SPICE=yes CDF=yes run_test

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 3
)

nmake.exe /nologo /f buildfiles\Windows.mak SPICE=yes CDF=yes test_spice

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 3
)

nmake.exe /nologo /f buildfiles\Windows.mak SPICE=yes CDF=yes test_cdf

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 3
)

nmake.exe /nologo /f buildfiles\Windows.mak SPICE=yes CDF=yes install

if %ERRORLEVEL% NEQ 0 (
	EXIT /B 4
)
