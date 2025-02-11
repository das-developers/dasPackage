:: set PYVER=%PY_VER%
set N_ARCH=\

set DAS2C_LIBDIR=%LIBRARY_LIB%
set DAS2C_INCDIR=%LIBRARY_INC%

%PYTHON% setup.py build -v
%PYTHON% setup.py install
