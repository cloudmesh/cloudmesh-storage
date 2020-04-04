# Cloudmesh Storage Module

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

### Parallel Queue Implementation 

Parallel Cloud Provider: 

* parallelawss3
* parallelgdrive
* parallelazureblob
* parallelbox

Supported Parallel Commands: 

* get 

  The get command downloads files from provider in parallel to
 your local host.
 
 ```
 storage create dir DIRECTORY [--storage=SERVICE] [--parallel=N]
```

* put

  The put command uploads files from your local host to the provider in parallel
  
 ```
 storage put SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
 ```

* create_dir

This command helps to create a new directory on the provider in parallel. 
You must specify the full path of the new directory you would like to create.

```
storage create dir DIRECTORY [--storage=SERVICE] [--parallel=N]
```

* list

The list command lists all the contents of a cloud directory in parallel. If the
 recursive option is specified, it will list the contents of all sub-directories
 as well.

```
storage list [SOURCE] [--recursive] [--parallel=N] [--output=OUTPUT] [--dryrun]
```

* delete

The delete command can delete files or folders from your cloud file storage in 
parallel. Deleting a folder will delete its contents as well (including the 
sub-directories).

```
storage delete SOURCE [--parallel=N] [--dryrun]
```

* search

The search command helps to search for a particular file within a directory.
If recursive options is specified, Cloudmesh will search for the file in all 
sub-directories of the original directory as well.

To search for a file at the root, pass an empty string or / as the target dir.

```
storage search  DIRECTORY FILENAME [--recursive] [--storage=SERVICE] [--parallel=N] [--output=OUTPUT]
```

* copy

The copy command copies files from one provider to another in parallel. 

``` 
storage copy --source=SOURCE:SOURCE_FILE_DIR --target=TARGET:TARGET_FILE_DIR
```

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
