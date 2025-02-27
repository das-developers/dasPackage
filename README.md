# Das Package

This is a utility repository containing downstream packaging recipies for das libraries 
and related dependencies. Language dependend packaging such as [dub](https://code.dlang.org/) 
for D or [wheels](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) 
for Python are outside the scope of this repository.

## Anaconda Packages
Example command lines.  First activate your version of anaconda or miniconda.
For example
```batchfile
rem Windows
cd %userprofile%\miniconda\condabin\activate 
```
```bash
# Linux, MacOS
eval "$(${HOME}/miniconda/bin/conda shell.bash hook)"
```

Then:
```bash
cd conda
conda install conda-build
conda install conda-verify
conda install ananconda-client

conda build pthread4w           # Windows only
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT #Windows only

conda build -c dasdevelopers das2c
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT

conda build -c dasdevelopers das2py
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT
```

## DEB Packages
At placeholder stage, nothing here yet

## RPM Packages
Spec file for das2C is in progress



