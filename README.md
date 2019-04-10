# Cloudmesh Storage Module

**Note: Do not modify the shield, once we release the storage module they will work**

[![Version](https://img.shields.io/pypi/v/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/cloudmesh-storage/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![Format](https://img.shields.io/pypi/format/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![Format](https://img.shields.io/pypi/status/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![Travis](https://travis-ci.com/cloudmesh/cloudmesh-storage.svg?branch=master)](https://travis-ci.com/cloudmesh/cloudmesh-storage)


## Requirements

Please note that several packages are available which are pointed to in the
instalation documentation.

|  | Links |
|---------------|-------|
| Documentation | <https://cloudmesh.github.io/cloudmesh-cloud> |
| Code | <https://github.com/cloudmesh/cloudmesh-cloud> |
| Instalation Instructions | <https://github.com/cloudmesh/get> |

An dynamically extensible CMD based command shell. For en extensive
documentation please see

* <https://github.com/cloudmesh-community/book/blob/master/vonLaszewski-cloud.epub?raw=true>

where we also document how to use pyenv virtualenv.


## Instalation and Documentation

For developers:

To install the storage module, you need to do an additional step. Please got to the directory
`cloudmesh.storage` and execute in it the command

```bash
$ pip install -e .
```

For users (NOT YET WORKING:

```bash
$ pip install cloudmesh.storage
```

## Nosetests

We have developed a number of simple nosetests tha can be called. To see the list of nosetests go to our directory

* <https://github.com/cloudmesh/cloudmesh-storage/tree/master/tests>

We also developed a general nosetest that works accross providers and can be invoked as follows

```bash
$ cms set storage=box
$ pytest -v --capture=no tests/test_storage.py
$ cms set storage=azure
$ pytest -v --capture=no tests/test_storage.py
$ cms set storage=gdrive
$ pytest -v --capture=no tests/test_storage.py
$ cms set storage=awss3
$ pytest -v --capture=no tests/test_storage.py
```

TODO: add other storage providers as they become ready 

## General features

How to set up the authentication to a specific service is discussed in later sections

TODO: Provide a simple programming example with the general provider

### Command Line Interface

TBD


```bash
$ cms set storage=azure
$ cms storage list
```

### Programming Interface

TBD

Cloudmehs Storage provides a simple programming API interface that you can use.
We highlight a simple exampple for storing and retrieving a file form a storage
provider.

We assume the files at the given path exist

```python
import cloudmesh.storage.provider.Provider as Provider
from cloudmesh.common.util import path_expand
from pprint import pprint

provider = Provider(service="azure")
src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
dst = "/"
result = provider.put(src, dst)
# The resut will be a dict of the information whih you can print with 

pprint(result)
```


## Box

TODO: Configuration: describe what you have to set in `cloudmesh4.yaml`

TODO: Describe how to use your specific nosetests

## Azure

TODO: Configuration: describe what you have to set in `cloudmesh4.yaml`

TODO: Describe how to use your specific nosetests


## AWS

TODO: Configuration: describe what you have to set in `cloudmesh4.yaml`

TODO: Describe how to use your specific nosetests


## Google drive

Due to bugs in the requirements of the google driver code, 
we have not yet included it in the Provider code. This needs to be fixed 
before we can do this.

TODO: Configuration: describe what you have to set in `cloudmesh4.yaml`

TODO: Describe how to use your specific nosetests

