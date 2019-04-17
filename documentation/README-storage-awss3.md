## Cloudmesh Integration

AWS S3 file storage has been integrated with cloudmesh library and is available for use via commandline. 
As a first step we need to modify `cloudmesh4.yaml` config file.  Under 'storage' section, we need to add the aws section 
to specify the parameters used to store files in AWS S3. 

In the credentials section under aws, specify the access key id and secret access key which will be available in the 
AWS console under AWS IAM service -> Users -> Security Credentials. 

Container is the default bucket which will be used to store the files in AWS S3. Region is the geographic area like 
us-east-1 which contains the bucket. Region is required to get a connection handle on the S3 Client or resource for 
that geographic area.

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
