## AWSS3 Cloudmesh Integration

AWS S3 file storage has been integrated with cloudmesh library and is available 
for use via commandline. As a first step we need to modify `cloudmesh.yaml` 
config file.  Under 'storage' section, we need to add the aws section to specify
the parameters used to store files in AWS S3. 

In the credentials section under aws, specify the access key id and secret 
access key which will be available in the AWS console under 
`AWS IAM service` -> `Users` -> `Security Credentials`. 

Container is the default bucket which will be used to store the files in AWS S3.
Region is the geographic area like `us-east-1` which contains the bucket. Region 
is required to get a connection handle on the S3 Client or resource for 
that geographic area.

Here is a sample.

```bash
cloudmesh:
  ...
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

The Cloudmesh command line library offers six functions under storage command: 
get, put, search, list, create directory, and delete. 
Once you have installed Cloudmesh, type `cms` into the command line to start the
cms shell. 

```bash
$ cms
+-------------------------------------------------------+
|   ____ _                 _                     _      |
|  / ___| | ___  _   _  __| |_ __ ___   ___  ___| |__   |
| | |   | |/ _ \| | | |/ _` | '_ ` _ \ / _ \/ __| '_ \  |
| | |___| | (_) | |_| | (_| | | | | | |  __/\__ \ | | | |
|  \____|_|\___/ \__,_|\__,_|_| |_| |_|\___||___/_| |_| |
+-------------------------------------------------------+
|                  Cloudmesh CMD5 Shell                 |
+-------------------------------------------------------+

cms>
```

To view the docopt for storage command, type in 

```bash
cms> help storage 
```

Help command gives a detail level understanding of what each command does and 
how to use the command line to interact with different storage providers and 
different parameters / options available in a particular command. 
For eg to invoke AWS S3 service, we need to pass awss3 as parameter to storage 
and suffix with the function call with the function parameters.

```bash
cms> storage --storage='aws' list ''
```

Alternatively, storage command can also be called directly without starting the 
cms shell.

```bash
$ cms storage --storage='aws' list ''
```

### Storage functions overview


### Create dir

This command helps to create a new directory on AWS S3. You must specify the 
full path of the new directory you would like to create. 

```bash
$ cms storage --storage='aws' create dir /base_path/targetdir
```

### Put

The put command uploads files from your local host to the S3. 

```bash
$ cms storage --storage='aws' put ~/.cloudmesh/storage/sourcedir /base_path/targetdir --recursive
```

Source for this command could be either a file or directory.

If you specify a file as the source, the file will be uploaded if no such file 
exists on the cloud or updated if a copy already exists on the cloud. 

If the source is a directory, you can choose to specify the recursive option to 
upload the files in the sub-directories in the source as well to the target 
directory in S3.
If the recursive option is not specified, only the files in the source 
directory will be uploaded to the target directory and the sub-directories will 
be ignored.


### Get

The get command downloads files from S3 to your local host.

```bash
$ cms storage --storage='aws' get /base_container/sourcedir ~/.cloudmesh/storage/targetdir --recursive
```

Source for this command could be either a file or directory.

If you specify a file as the source, you need to speccify the full path of file
including the file name where you want the file to be downloaded. In case you 
do not specify the file name and only give the target directory, then the file 
will be downloaded with the same name as present on S3.

If the source is a directory, you can choose to specify the recursive option to 
download files in the sub-directories in the source as well to the target 
directory in your local host.
If the recursive option is not specified, only the files in the source 
directory will be downloaded to the target directory and the sub-directories 
will be ignored.


### Search

The search command helps to search for a particular file within a directory.

If recursive options is specified, Cloudmesh will search for the file in all 
sub-directories of the original directory as well.

To search for a file at the root, pass an empty string or / as the target dir.

```bash
$ cms storage --storage='aws' search /base_path/targetdir testfile.txt --recursive
```

### List

The list command lists all the contents of a cloud directory. If the recursive 
option is specified, it will list the contents of all sub-directories as well. 

```bash
$ cms storage --storage='aws' list /base_path/targetdir --recursive
```


### Delete

The delete command can delete files or folders from your cloud file storage. 
Deleting a folder will delete its contents as well (including the 
sub-directories).

```bash
$ cms storage --storage='aws' delete /base_path/targetdir --recursive
```
