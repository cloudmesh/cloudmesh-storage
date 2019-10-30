# Cloudmesh Storage Provider for Virtual Directories - AWS to/from Google
 Pratibha Madharapakkam Pagadala
 
 fa19-516-152
 
<https://github.com/cloudmesh-community/fa19-516-152/blob/master/project/report.md>

## Introduction

This project is to develop API and rest services to manage and transfer files between different cloud service providers. A cloudmesh based command will be implemented to transfer files present in a storage queue from a source to target cloud provider. In this instance, the functionality will be implemented for AWS and Google Cloud. For performance evaluation py tests will be created. 

## Motivation
 Multiple cloud providers offer storage solutions to manage data in the form of files. The intention here is to build a command which can provide functionality to read the files from a queue and move them from a source to a target cloud provider's storage. In this method, users will be able to split or move the data across different cloud providers that provider cheaper solutions. 

## Requirements

* AWS, Google cloud accounts
* cloudmesh-storage API
* REST API
* cloudmesh-storage queue API
* Python API
TBD

## Architecture Diagram

![Architecture](images/architecture2.png)

Description

* Client intiates a cms storage_switch command with options such as
 
   1) Recursive file copy from source to target
  2) List the files
  3) Add the files
  4) delete the files
  
* Cloudmesh storage_switch command will run on the local server. According to the options and arguments, this would delegate the functions between AWS and Google Cloud.  
* Storage and Utility APIs on AWS and Google cloud.   

## Technology Used

* cloudmesh-storage
* Python
* REST
* AWS S3 Storage
* Google Storage
* OpenAPI

## Progress

* Update report.md with architecture and command details.
* Generated command using cloudmesh shell - cms storage_service command
* Create AWS account and Google Cloud accounts
* Access AWS account using cloudmesh commands

Next Steps
* Update provider classes for AWS and Google Cloud.
* Explore the Google's gsutil api and read on how to use it in project.
* Copy file from aws to google cloud
* Copy file from google cloud to aws. 


## References

* <https://github.com/googleapis/google-cloud-python#google-cloud-python-client>
* <https://aws.amazon.com/s3/>
* <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html>
* <https://github.com/cloudmesh/cloudmesh-storage/tree/master/cloudmesh/storage>





