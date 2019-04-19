# Installation

[![Downloads](https://img.shields.io/pypi/dm/cm.svg)](https://pypi.python.org/pypi/cloudmesh/cloudmesh-cloud/)

## Prerequisites

Before you install make sure that you have at minimum python 3.7.2
installed. We recommend that you use a python virtualenv such as `venv`
or `pyenv` to isolate the python installed packages as not to interfere
with the system installation.

### Installation via pip development

The installation via pip is not yet supported for cloudmesh cm. Thus
we recommend that you use the source installation instead.

In future cloudmesh version 4 will be installed with

```bash
pip install cloudmesh-cloud
```

Individual packages can be installed with

```
pip install cloudmesh-common
pip install cloudmesh-sys
pip install cloudmesh-cmd5
pip install cloudmesh-openapi
```

For the time being we recommend you conduct the source install.

### Source installation for development

For developers we recommend the source installation as all other installations
will not yet work


```bash
export SRC=`pwd`
git clone https://github.com/cloudmesh/cloudmesh-common.git
git clone https://github.com/cloudmesh/cloudmesh-cmd5.git
git clone https://github.com/cloudmesh/cloudmesh-sys.git
git clone https://github.com/cloudmesh/cloudmesh-openapi.git
git clone https://github.com/cloudmesh-community/cloudmesh-cloud.git


cd $SRC/cloudmesh-common
pip install -e .
cd $SRC/cloudmesh-cmd5
pip install -e .
cd $SRC/cloudmesh-sys
pip install -e .
cd $SRC/cloudmesh-openapi
pip install -e .
cd $SRC/cloudmesh-cloud
pip install -e .
```

## Updating cloudmesh from source

To update cloudmesh form source you will need yo update all source packages.
Make sure to place all your code in the current directory, or locate the
directory in your system where you prviously have git cloned it Now the update
is easy: 


```bash
export SRC=`pwd`

cd $SRC/cloudmesh-common
git pull
pip install -e .
cd $SRC/cloudmesh-cmd5
git pull
pip install -e .
cd $SRC/cloudmesh-sys
git pull
pip install -e .
cd $SRC/cloudmesh-openapi
git pull
pip install -e .
git pull
cd $SRC/cm
pip install -e .
```

However we also have a command called 

```bash
$ cms source install
```

assuming you use ssh as the protocoll to interface with git.
Please make sure your cloudmesh4.yaml file contains the location where 
you like to install cloudmesh in. An example is

```
cloudmesh:
  destination:
    cloudmesh-common: ~/Desktop/github/cloudmesh
    cloudmesh-cmd5: ~/Desktop/github/cloudmesh
    cloudmesh-openapi: ~/Desktop/github/cloudmesh
    cloudmesh-sys: ~/Desktop/github/cloudmesh
    cloudmesh-cloud: ~/Desktop/github/cloudmesh
      git: https://github.com/cloudmesh-community/cloudmesh-cloud
```


## Installation of mongod

First, you will need to install a `cloudmesh4.yaml` file, if you have
not done this before. The easieast way to do so is with the command

```bash
$ cms help
```
 
Now you will need to edit the file

`~/.cloudmesh/cloudmesh4.yaml`

and change the password of the mongo entry to something you like,
 e.g. change the TBD to a real strong password

```
      MONGO_PASSWORD: TBD
```

In case you do not have mongod installed, you can do so for macOS and Ubuntu 
18.xx by setting the following variable:

```
      MONGO_AUTOINSTALL: True
```


Now you can run the `admin mongo install` command. It will not only
install mongo, but also add the path to your `.bash_*` file. In case
of windows platform, you will have to set the PATH variable
manually. To install it simply say.

```bash
$ cms admin mongo install
```

To create a password protection you than run the command

```bash $ cms admin mongo create ``` In case of Windows platform, after
executing above command, open a new cms session and execute below
commands.

```bash
$ cms admin mongo start
```

Once the mongo db is created it can be started and stoped with 

```bash
$ cms admin mongo start
$ cms admin mongo stop
```

For cloudmesh to work properly, please start mongo.

## One Line installer (ok)

```bash
wget -qO - http://cloudmesh.github.io/get/ | sh 
```

## Anaconda and Conda (proposed)

At this time we do not yet support conda. But if you like to
contribute an instalation package, please do so.
 
It may just very well work with our pip installs, but we have not
tested it.  Please give us feedback.
