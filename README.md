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
installation documentation.

|  | Links |
|---------------|-------|
| Documentation | <https://cloudmesh.github.io/cloudmesh-cloud> |
| Code | <https://github.com/cloudmesh/cloudmesh-cloud> |
| Instalation Instructions | <https://github.com/cloudmesh/get> |

An dynamically extensible CMD based command shell. For en extensive
documentation please see

* <https://github.com/cloudmesh-community/book/blob/master/vonLaszewski-cloud.epub?raw=true>

where we also document how to use pyenv virtualenv.


## Installation and Documentation

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

## Pytests

We have developed a number of simple pytests that can be called. To see the list of Pytests go to our directory

* <https://github.com/cloudmesh/cloudmesh-storage/tree/master/tests>

We also developed a general pytest that works accross providers and can be invoked as follows

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

Cloudmesh Storage provides a simple programming API interface that you can use.
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

### Configuration

In the `cloudmesh4.yaml` file, find the 'box' section under 'storage'. Under credentials, set `config_path` to the path of the configuration file you created as described in the Box chapter:

```bash
   box:
      cm:
        heading: Box
        host: box.com
        label: Box
        kind: box
        version: TBD
      default:
        directory: /
      credentials:
        config_path: ******************************
```

### Pytests

Open a terminal and navigate to the cloudmesh-storage directory. Enter the following command to run pytests:

```bash
$ pytest -v --capture=no tests/test_box.py
```

## Azure

### Configuration

The `cloudmesh4.yaml` file needs to be set up as follows for the 'azure-blob' section under 'storage'.

```bash
  storage:
    azure-blob:
      cm:
        heading: Azure
        host: azure.com
        label: Azure
        kind: azureblob
        version: TBD
      default:
        directory: TBD
      credentials:
        account_name: 'XXXXXXXXXXXXXXXXX'
        account_key: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        container: 'Test container name'
```

Configuration settings for credentials in the yaml file can be obtained from Azure portal.

* `account_name` - This is the name of the Azure blob storage account.
* `account_key` - This can be found under 'Access Keys' after navigating to the storage account on the Azure portal.
* `container` - This can be set to a default container created under the Azure blob storage account.

### Pytests

Execute the following command for Azure Blob storage service pytest after navigating to the cloudmesh-storage directory.

```bash
$ pytest -v --capture=no tests/test_azure.py
```


## AWS S3

### Configuration

In the `cloudmesh4.yaml` file, the 'aws' section under 'storage' describes the parameters used to store files in AWS S3. 
In the credentials section under aws, specify the access key id and secret access key which will be available in the AWS console under AWS IAM service -> Users -> Security Credentials. 
Container is the default Bucket which will be used to store the files in AWS S3. 
Region is the geographic area like us-east-1 which contains the bucket. Region is required to get a connection handle on the S3 Client or resource for that geographic area.
Here is a sample.

```bash
storage:
    aws:
      cm:
        heading: aws
        host: amazon.aws.com
        label: aws
        kind: awsS3
        version: TBD
      default:
        directory: TBD
      credentials:
        access_key_id: *********
        secret_access_key: *******
        container: name of bucket that you want user to be contained in.
        region: Specfiy the default region eg us-east-1
```

### Pytests

Script to test the AWS S3 service can be accessed under tests folder using the following pytest command.

```bash
$ pytest -v --capture=no tests/test_storage_aws.py
```


## Google drive

Due to bugs in the requirements of the google driver code, 
we have not yet included it in the Provider code. This needs to be fixed 
before we can do this.

The `cloudmesh4.yaml` file needs to be set up as follows for the 'gdrive' section under 'storage'.

```bash
storge:
    gdrive: 
      cm: 
        heading: GDrive
        host: gdrive.google.com
        kind: gdrive
        label: GDrive
        version: TBD
      credentials: 
        auth_host_name: localhost
        auth_host_port: 
          - ****
          - ****
        auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
        auth_uri: "https://accounts.google.com/o/oauth2/auth"
        client_id: *******************
        client_secret: ************
        project_id: ************
        redirect_uris: 
          - "urn:ietf:wg:oauth:2.0:oob"
          - "http://localhost"
        token_uri: "https://oauth2.googleapis.com/token"
      default: 
        directory: TBD
```

### Pytests

Script to test the GDrive service can be accessed under tests folder using the following pytest command.

```bash
$ pytest -v --capture=no tests/test_gdrive.py
```

## Virtual Directory

The virtual directory has been developed to mirror the linux directory commands. File links in the virtual directory point to files on storage providers, which can be retrieved using the virtual directory. 

### Configuration

The credentials for the virtual directory are the same as for the admin mongo command. See the Mongo section for details. 

### Pytests

The vdir command can be tested as follows:

```bash
$ pytest -v --capture=no tests/test_vdir.py
```
