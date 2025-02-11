# Das Package

This is a utility repository containing packaging recipies for das libraries and dependencies.
Most packaging utilities assume that the source code is complete an the starting point is an
upstream tarball/zip file of sources.

## Anaconda builds
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

conda build pthread4w
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT

conda build -c dasdevelopers das2c
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT

conda build -c dasdevelopers das2py
anaconda upload -u dasdevelopers PACKAGE_FILE_FROM_OUTPUT
```

## PIP Builds
Todo

## RPM Builds
Todo

## DEB Builds
Todo


