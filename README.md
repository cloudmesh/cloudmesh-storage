# Cloudmesh Storage Module


## Requirements

Please note that several packages are available which are pointed to
in the installation documentation.

|  | Links |
|---------------|-------|
| Documentation | <https://cloudmesh.github.io/cloudmesh-manual> |
| Code | <https://github.com/cloudmesh/cloudmesh-storage> |
| Instalation Instructions | <https://github.com/cloudmesh/cloudmesh-installer> |

An dynamically extensible CMD based command shell. For en extensive
documentation please see

* <https://github.com/cloudmesh-community/book/blob/master/vonLaszewski-cloud.epub?raw=true>

where we also document how to use pyenv.


## Installation

### Users

The user can install cloudmesh storage with

```bash
pip install cloudmesh-storage
```

### Developers

Developers want the source code and do the developement in the
directory. We use the `cloudmesh-installer` to do this. Make sure you
use a virtual environment such as ~/ENV3. We recommend using pythin
3.8.2

* See also: <https://github.com/cloudmesh/cloudmesh-installer>

```bash
mkdir cm
cd cm
pip install cloudmesh-installer -U
cloudmesh-installer get storage
```

In case you need to reinstall the venv you can use

cloudmesh-installer new ~/ENV3 storage --python=python3.8

PLease note to use the python program for your system. THis may be
different.

## Cloud Accounts

* [OpenStack Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/openstack.html)
* [AWS Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/aws.html)
* [Azure Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/azure.html)
* [Google Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/google/account.html)
* [Oracle Cloud Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/oracle/account.html)
* [Box Account](https://cloudmesh.github.io/cloudmesh-manual/accounts/box.html)

Some older Provider documentation is located at

* [VM Providers (outdated)](https://cloudmesh.github.io/cloudmesh-manual/accounts/accountcreation-old.html)

TODO: you will be responsible for merging needed documentation form the
old documentation and delete it if it is merged and no longer needed in
the old documentation.

## Architecture

### Cloudmesh Provider Concept

As we are developping multicloud environments we like to reuse and make
some of the functionallity similar between clouds. for this reason we
have implemented a provider concept that reads teh credentials for each
storage location from a cloudmesh yaml file.

Then based on the `cms.kind` of this storage location a Provider is
picked and we can interact with the system.

Thisis documented for the compute provider at

* [Provider concept](https://cloudmesh.github.io/cloudmesh-manual/concepts/providers.html)

### Temporary development in one directory

To simplify the task for storage we still define everything in one
directory. However in future we will break it up and move each provider
to its specific provider directory so that clouds are clearly seperated.
THis move is not conducted by you but by Gregor, so we preserve the git
history. He has a special git command that does this. So please for now
develop in thsi directory if not already given other instructions.

### Architecture

TODO: This document is missing

### New Architecture for Parallel Transfers

TODO: This document is missing


## Tests

The tests are included in the test directory. For the tests to work,  
you need to first set the storage provider with

```
$ cms set storage=awss3
```

you can select the following storage providers:

* awss3
* gdrive
* azureblob
* box

Recently we are working on several new storage providors that improve
the performance. This is based on using a parallel queue to organize the
transfers.

* oracle
* parallelawss3

These new providers will eventually replace the existing providers.

Please note that if you find more or different tests that need to be
added add them to the tests in the test/.  directory so they work
accross all storage providers. If special tests are needed for a
specific provider they ban be added to the specific sub directory.
Please add here a description why this specil test is needed. Please
remove all tests that are already covered by the tests in the main tets
directory form these special tests.
