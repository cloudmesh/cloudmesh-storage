# Cloudmesh Storage Module



> **Note:** The README.md page is outomatically generated, do not edit it.
> To modify  change the content in
> <https://github.com/cloudmesh/cloudmesh-storage/blob/master/README-source.md>
> Curley brackets must use two in README-source.md



[![image](https://img.shields.io/pypi/v/cloudmesh-storage.svg)](https://pypi.org/project/cloudmesh-storage/)
[![Python](https://img.shields.io/pypi/pyversions/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/cloudmesh-storage/blob/master/LICENSE)
[![Format](https://img.shields.io/pypi/format/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![Status](https://img.shields.io/pypi/status/cloudmesh-storage.svg)](https://pypi.python.org/pypi/cloudmesh-storage)
[![Travis](https://travis-ci.com/cloudmesh/cloudmesh-storage.svg?branch=master)](https://travis-ci.com/cloudmesh/cloudmesh-storage)


## Changelog

see: [Changelog](https://github.com/cloudmesh/cloudmesh-storage/blob/master/CHANGELOG.md)

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

## Manual Page

```bash
Usage:
  storage run
  storage monitor [--storage=SERVICES] [--status=all | --status=STATUS] [--output=output] [--clear]
  storage create dir DIRECTORY [--storage=SERVICE] [--parallel=N]
  storage get SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
  storage put SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
  storage list [SOURCE] [--recursive] [--parallel=N] [--output=OUTPUT] [--dryrun]
  storage delete SOURCE [--parallel=N] [--dryrun]
  storage search  DIRECTORY FILENAME [--recursive] [--storage=SERVICE] [--parallel=N] [--output=OUTPUT]
  storage sync SOURCE DESTINATION [--name=NAME] [--async] [--storage=SERVICE]
  storage sync status [--name=NAME] [--storage=SERVICE]
  storage config list [--output=OUTPUT]
  storage [--parallel=N] copy SOURCE DESTINATION [--recursive]
  storage copy --source=SOURCE:SOURCE_FILE_DIR --target=TARGET:TARGET_FILE_DIR

This command does some useful things.

Arguments:
  SOURCE        SOURCE can be a directory or file
  DESTINATION   DESTINATION can be a directory or file
  DIRECTORY     DIRECTORY refers to a folder on the cloud service
  SOURCE:SOURCE_FILE_DIR   source provider name: file or directory name
  TARGET:SOURCE_FILE_DIR   destination provider name

Options:
  --storage=SERVICE  specify the cloud service name like aws or
                     azure or box or google

Description:
  commands used to upload, download, list files on different
  cloud storage services.

  storage put [options..]
    Uploads the file specified in the filename to specified
    cloud from the SOURCEDIR.

  storage get [options..]
    Downloads the file specified in the filename from the
    specified cloud to the DESTDIR.

  storage delete [options..]
     Deletes the file specified in the filename from the
     specified cloud.

  storage list [options..]
    lists all the files from the container name specified on
    the specified cloud.

  storage create dir [options..]
    creates a folder with the directory name specified on the
    specified cloud.

  storage search [options..]
    searches for the source in all the folders on the specified
    cloud.

  sync SOURCE DESTINATION
    puts the content of source to the destination.
     If --recursive is specified this is done recursively from
        the source
     If --async is specified, this is done asynchronously
     If a name is specified, the process can also be monitored
        with the status command by name.
     If the name is not specified all date is monitored.

  sync status
    The status for the asynchronous sync can be seen with this
    command

  config list
    Lists the configures storage services in the yaml file

  storage copy SOURCE DESTINATION
    Copies files from source storage to destination storage.
    The syntax of SOURCE and DESTINATION is:
    SOURCE - awss3:source.txt
    DESTINATION - azure:target.txt

Description of the copy command:

     Command enables to Copy files between different cloud service
     providers, list and delete them. This command accepts `aws` ,
     `google` and `local` as the SOURCE and TARGET provider.

     cms storage copy --source=SERVICE:SOURCE --target=DEST:TARGET

         Command copies files or directories from Source provider to
         Target Provider.

     cms storage slist --source=SERVICE:SOURCE
         Command lists all the files present in SOURCE provider's in
         the given SOURCE_FILE_DIR location This command accepts
         `aws` or `google` as the SOURCE provider

     cms storage sdelete --source=SERVICE:SOURCE
         Command deletes the file or directory from the SOURCE
         provider's SOURCE_FILE_DIR location

Examples:
>     cms storage_service copy --source=local:test1.txt
>                              --target=aws:uploadtest1.txt
     cms storage_service list --source=google:test
     cms storage_service delete --source=aws:uploadtest1.txt


Example:
   set storage=azureblob
   storage put SOURCE DESTINATION --recursive

   is the same as
   storage --storage=azureblob put SOURCE DESTINATION --recursive

   storage copy azure:source.txt oracle:target.txt
```


## Design

### Cloudmesh Provider Concept

As we are developping multicloud environments we like to reuse and make
some of the functionallity similar between clouds. for this reason we
have implemented a provider concept that reads the credentials for each
storage location from a cloudmesh yaml file.

Then based on the `cms.kind` of this storage location a Provider is
picked and we can interact with the system.

This is documented for the compute provider at

* [Provider concept](https://cloudmesh.github.io/cloudmesh-manual/concepts/providers.html)

### Temporary development in one directory

To simplify the task for storage we still define everything in one
directory. However in future we will break it up and move each provider
to its specific provider directory so that clouds are clearly seperated.
THis move is not conducted by you but by Gregor, so we preserve the git
history. He has a special git command that does this. So please for now
develop in thsi directory if not already given other instructions.

### Arrchitecture

Current architecture concepts: [Cloudmesh Storage Concepts](https://cloudmesh.github.io/cloudmesh-manual/concepts/storage.html)

* TODO: Link to the document with the parallel architetcture is missing

* Parallel Queue

### Comamnds

See: [Storage Commands](https://cloudmesh.github.io/cloudmesh-manual/manual-storage.html)

* TODO: If a command is missing let Gregor know and we work on integrating it.

### API

See: [Storage API](https://cloudmesh.github.io/cloudmesh-manual/api/index.html#cloudmesh-api)

* TODO: If your docstrings are incomplete or incorrect please fix
* TODO: If your API is missing please contact Gregor

The API for storage will likely have cloudmesh.storage

HOwever if your API is in a provider specific directory, please add it
to the documentation here. In that case communicate with Gregor for
guidance.

In addition to the manual pages, they are also available as API so you can directly access the commands from teh API.

Please see:

* [cms storage](https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.storage.command.html)
* [cms vdir](https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.vdir.command.html)

### Jupyter Example

TODO: Please develop an example to showcase how your code can be used form JUpyter

see: [Jupyter example for compute](https://cloudmesh.github.io/cloudmesh-manual/jupyter/index.html)

for an example for using compute providers.

### API Example

TODO: Please also provde an example on hoe t use your provider directly.
This can be most likely copied from a pytset.

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
