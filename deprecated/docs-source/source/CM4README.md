# CM4 Details (outdated)


In cloudmesh, we are using the **Python** tool to implement a
program that could remotely control cloud nodes provided by different
organizations and run experiments in parallel.

The goal of *`cloudmesh`* is to provide a platform that users could directly
control the nodes they have, like AWS, Azure, and OPENSTACK
instances. Users could decide to start, stop, destroy, create, resume,
and suspend different nodes without accessing the **Console**
interfaces of providers. Then users could install experiment
environment, software, and other required tools in these running
nodes. Finally, an experiment could be executed in running nodes by
sending the commands from *`cloudmesh`* platform. Meanwhile, we embed the
NoSQL database **MongoDB** into cloudmesh for managing the nodes and
experiments.


### Extra: Vargrant

TODO: update the link

Please refer to [here](https://github.com/cloudmesh/cloudmesh-cloud/tree/master/cloudmesh-cloud/vagrant/README.md) to see how to setup 
Vagrant with cloudmesh.

## What we have implemented 

* the function to install `cms` and its required packages
* the function to manage the virtual machines from cloud service providers (Azure, AWS, and Openstack)
* the function to use *MongoDB* for saving data


### The Preparation for installing cloudmesh (David)

* requriements.txt : the required packages
* setup.py
* cloudmesh-cloud/command/command.py : the python class defines the interface for the command-line `cms` 

``` commandline
$ cms
Usage:
      cms admin mongo install [--brew] [--download=PATH]
      cms admin mongo status
      cms admin mongo start
      cms admin mongo stop
      cms admin mongo backup FILENAME
      ...
```

### The Configuration files and some relative function classes (Sachith)

The cloudmesh.yaml file contains all the configurations required for CM4 to run. 
By default it's located in the Cloudmesh home directory (~/.cloudmesh/cloudmesh.yaml).

#### Use the Configurations file

To use the configurations in CM4, you need to import the Config class and use the config
object provided by that class to access and manipulate the configuration file. 

##### Getting the config object

```python
from cloudmesh.cloud.configuration.config import Config
config = Config().data["cloudmesh"]
```

##### Getting values
To get values from the configurations, you can call level by level from top-down config.
```python
MONGO_HOST = config["data"]["mongo"]["MONGO_HOST"]
```

### Using the Counter file
CM4 keeps track of all the VMs running using counters for each VM. 
The counter file is located at 
```bash
~/.cloudmesh/counter.yaml
```

#### Using the counter

```python
from cloudmesh.cloud.configuration.counter import Counter
counter = Counter()
```

##### Incrementing and Decrementing the counter values
```python
# to update a specific VM counter
counter.incr("<VM_NAME>")
counter.decr("<VM_NAME>")

# to update the total vm counter
counter.incr()
counter.decr()
```

##### Getting and Setting the counter values
```python
# to update a specific VM counter
counter.get("<VM_NAME>")
counter.set("<VM_NAME>", "value")
```


### The MongoDB Database in `cloudmesh` (Yu)

We add the database into `cloudmesh` with two reasons:

* provide the information of nodes in different providers.
* record the experiment executed through cloudmesh, easy for next re-execution.


Every time the user use the cloudmesh platform, the server would access the running MongoDB database, querying the nodes'
information, showing relative metadata, and then updating all necessary data.

The *MongoDB* would finish below tasks:

* saving all information:

  1. the nodes' information queried from cloud service, like name, id, status, and other metadata about this node.
  2. saving the executing or executed experiment information, like which node we run the experiment, the input, the 
  command, and the output.
  3. saving the group information users defined.

* updating any changes:
  
  1. the changes updated on the nodes, like stop running node, or start stopped node.
  2. the changes updated on the `cloudmesh.yaml`, like add new nodes.
  3. when the experiment is done, output and experiment status would be updated.
  4. new group is created while using `cms` will be updated

* return required information:
	
  1. return the node information, group information, and experiment information when `cms` queries them.

#### Data Scheme in MongoDB

There are three types of documents in MongoDB:

* Node information in `cloud` collection.
  Different cloud service providers would return different schemas of node information. It is hard to manipulate 
  different nodes' information into same schema, so we decide to dump the return mesaage into MongoDB without 
  any changes.
  
* Node's experiment status in `status` collection.
  The document in `status` collection is going to save the information of experiments executed in a node.
 
  ```text
  {'_id': node_id,
  'status': status,
  'currentJob': job_id,
  'history' : the history of executed experiments in this node}
   ```

* Experiment information in `job` collection.

  ```text
  {'_id': experiment_id
  'name': name,
  'status': status,
  'input': input_info,
  'output': output_info,
  'description': description,
  'commands': commands}
  ```

* Group information in `group` collection.

  ```text
  {'cloud': cloud,
  'name': name,
  'size': size,
  'vms': list_vms}
  ```

#### Security in MongoDB

For data security purpose, we enable the MongoDB security functionality in `cms`.

When users first time start the *MongoDB*, they have to add an account and open an port to access all database in MongoDB. Because we save all nodes' information into MongoDB inclduing the *Authorization* information. If your MongoDB is open to everyone, it is easy for hacker to steal your information. So you are requried to set the *username* and *password* for the security purpose. 

If you want to learn more about the *Security* in MongoDB, you can visit this [page](https://docs.mongodb.com/manual/security/) or visit the brief introduction about the MongoDB

Here is a quick reference about how to
 [enable MongoDB Security](https://medium.com/@raj_adroit/mongodb-enable-authentication-enable-access-control-e8a75a26d332) option. 



#### Install MongoDB Into Local

If you want to know how to install MongoDB into local, you can review [Install MongoDB](https://docs.mongodb.com/manual/installation/)

And if you want to use `cms` to help you install MongoDB, you have to update the information required for installing 
MongoDB into the `cloudmesh.yaml` file.

The `cloudmesh-cloud/cmmongo/MongoDBController.py` has the functions to install MongoDB for Linux and Darwin system. 

The logic of installing MongoDB is:

```text
1. install prepared tools
2. download the MonoDB .tgz tarball
3. extract file from tarball
4. update the PATH environment 
5. create data and log directories
6. create the mongodb configuration file
```

When we finish installing MongoDB to local, we have to: 

```text
7. run the MongoDB
8. add new role for user to access the database
9. stop MongoDB
10. enable the security setting in configuration file
```

#### Insert and Update Documents in MongoDB

We have different documents in different collections. The operations in `cloudmesh-cloud/vm/Vm.py` will call `mongoDB.py` to accomplish
inserting and updating the document.

```text
insert_cloud_document(document) : insert the document into 'cloud' collection
insert_status_document(document) : insert the document into 'status' collection
insert_job_document(document) : insert the document into 'job' collection
insert_group_document(document) : insert the document into 'group' collection
update_document(collection_name, key, value, info) : update the new information into the
                                                     the document queried by 'key : value' 
                                                     in collection_name' collection
find_document(collection_name, key, value) : get a document by 'key : value' from 
                                             'collection_name' collection
find(collection_name, key, value) : get documents satisfied with 'key : value' from 
                               'collection_name' collection
delete_document(collection_name, key, value) : delete the document satisfied with 'key : value'
                                               from 'collection_name' collection
``` 


### The Virtual Machine Provider

#### Execute Command in  MongoDB

To grant users more power in manipulating their local MongoDB database, we also
add functions for users to execute their customized mongoDB command as if they can 
use mongoDB client throught terminal by db_command(command) function. 
And in order to handle the various exceptions and errors which might occur when 
executing the command, we also add the db_connection() function to help contain those
unexpected results.

```text
db_command(command): issue a command string to virtual mongoDB shell
db_connection: test connection to local mongoDB host
```


### 4. The Virtual Machine Provider


In `cloudmesh`, we developed the `cloudmesh-cloud/vm/Vm.py` class to implement the operations for different virtual machines from AWS, 
Azure, and Chameleon by using the python library [*Apache Libcloud*](https://libcloud.apache.org) to interact with 
cloud service providers. 

The basic functions are:
```text
1. start(vm_name) : start the virtual machine with specified name
2. stop(vm_name, deallocate) : stop the virtual machine with specified name
3. resume(vm_name) : resume the suspended virtual machine with specified name
4. suspend(vm_name) : suspend the running virtual machine with specified name
5. destroy(vm_name) : destroy the virtual machine with specified name
6. list() : list all virtual machine in your cloud service account
7. status(vm_name) : show the working status of virtual machine with specified name
8. info(vm_name) : show all information about the virtual machine with specified name
9. get_public_ips(vm_name) : return the public ip of the virtual machine with specified name
10. set_public_ip(vm_name, public_ip): set the public ip for the virtual machine with specified name
11. remove_public_ip(vm_name) : remove the public ip from virtual machine with specified name
```


Below we list some sample of running these functions for virtual machines in  AWS, Azure and Openstack.

### AWS VM Operations (Yu)

Before using the AWS Vm code, user has to update their AWS information into the `cloudmesh.yaml` file in *etc* folder.

The *Libcloud* library has enough methods to support the operations for managing virtual machines in AWS. We use a 
`cloudmesh-cloud/vm/Aws.py` to create the driver based on the configuration to connect to AWS.  

Inherit the *Libcloud* library, we did some modifications on `AWSDriver` to extend the operation. The `create_node`
method would create a virtual machine in AWS based on the configuration of `cloudmesh.yaml` file  

Here are some samples for running these operations by using `cloudmesh-cloud`:

First, user would create the virtual machine in AWS.
```commandline
$ cms vm create
Collection(Database(MongoClient(host=['127.0.0.1:27017'], document_class=dict, tz_aware=False, connect=True), 'cloudmesh'), 'cloud')
Thread: updating the status of node
Created base-cloudmesh-yuluo-4
PING 52.39.13.229 (52.39.13.229): 56 data bytes

--- 52.39.13.229 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
```

then **MongoDB** will have below record in `cloud` collection.

```text
{ "_id" : ObjectId("5c09c65f56c5a939942a9911"), 
"id" : "i-01ca62f33728f4931", 
"name" : "base-cloudmesh-yuluo-4", 
"state" : "running", 
"public_ips" : [ "52.39.13.229" ], 
...}
```

If user want to stop the virtual machine, then he has to type below command with virtual machine name. The code will return 
you the virtual machine from MongoDB record with a thread updating the new information. When the thread is done, you can use
`status` method to check the status of the virtual machine.

```commandline
$ cms vm stop --vms=base-cloudmesh-yuluo-4
Thread: updating the status of node
{'_id': ObjectId('5c09c65f56c5a939942a9911'), 
'id': 'i-01ca62f33728f4931', 
'name': 'base-cloudmesh-yuluo-4', 
'state': 'running', 
'public_ips': ['52.39.13.229'],
...}
$ cms vm status --vms=base-cloudmesh-yuluo-4
stopped
```

When user wants to start the stopped virtual machine, he has to type the command of below sample.

```commandline
$ cms vm start --vms=base-cloudmesh-yuluo-4
Thread: updating the status of node
{'_id': ObjectId('5c09c65f56c5a939942a9911'), 
'id': 'i-01ca62f33728f4931', 
'name': 'base-cloudmesh-yuluo-4', 
'state': 'stopped', 
'public_ips': [],
...}
PING 54.191.109.54 (54.191.109.54): 56 data bytes

--- 54.191.109.54 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss

$ cms vm status --vms=base-cloudmesh-yuluo-4
running
```

There is a way for users to get the public ip of a virtual machine.

```commandline
$ cms vm publicip --vms=base-cloudmesh-yuluo-4
{'base-cloudmesh-yuluo-4': ['54.191.109.54']}
```

Also, if user wants to know the information of virtual machines under his AWS account, he could do this.

```commandline
$ cms vm list
<Node: uuid=9b46e75095f586471e2cfe8ebc6b1021ead0e86b, name=a-b-luoyu-0, state=STOPPED, public_ips=[], 
private_ips=['172.31.28.147'], provider=Amazon EC2 ...>, 
<Node: uuid=da309c8acbbc7bc1f21295600323d073afffb04a, name=base-cloudmesh-yuluo-1, state=TERMINATED, 
public_ips=[], private_ips=[], provider=Amazon EC2 ...>
<Node: uuid=cb62a083081350da9e6f229aace4b697358a987b, name=base-cloudmesh-yuluo-4, state=RUNNING, 
public_ips=['54.191.109.54'], private_ips=['172.31.41.197'], provider=Amazon EC2 ...>,
```

Finally, if user wants to delete the virtual machine, he could do this.

```commandline
$ cms vm destroy --vms=base-cloudmesh-yuluo-4
True
```

 ### Azure VM Operation (David)
 
 
 ### Chameleon VM Operation (Rui and Kimball)

 Same as above, before using the VM Openstack functionalities, 
 user has to update their Openstack information into the `cloudmesh.yaml` file (~/.cloudmesh/cloudmesh.yaml by macOS convention). 
It is also important to notice that openstack has various providers.
 And it is important to specify each of them with correspondent log-in credentials.

Many of the funtions are supported by the *Libcloud* library. By specifying the config parameters to `openstack` and `chameleaon`, 
VM Provider will automatically attach futher operations to openstack primitives.

In order to overcome some issues with service provider (mostly delays in operations like spawing, ip-assignments, refactoring and etc), 
we implement timeout mechanism to syncronize status between our local machines and remote providers. 
Blocking strategy is used to prevent un-deterministic running result.

Since providers of openstack like Chameleon and Jetstream allow users to 
associate customized float ip to their instances, we also develop such functions
to support tasks like this and give more power to users when runing their jobs.

Please refer to AWS VM Operation for examples. 
Chameleon Openstack expose same 
operations as AWS to users. Notice that before running your command,
you need to make sure the global default cloud parameter has been set
to 'Chameleon' by:

```commandline
$ cms vm set cloud chameleon
Setting env parameter cloud to: chameleon
Writing updata to cloudmesh.yaml
Config has been updated.
```

 
 ### VM Refactor (Rui)
 In addition, in order to offer more flexibilities to our users, we also developed vmrefactor (`cloudmesh-cloud/vm/VmRefactor.py`)
to allow users to customize the flavors of their running instances and services in different providers.

```text
1. resize(vm_name, size) : resize the virtual machine with specified size object
2. confirm_resize(vm_name) : some providers requires confirmation message to complete resize() operation
3. revert(vm_name) : revert a resize operation. Revert the virtual machine to previous status
4. rename(vm_name, newname) : rename the virtual machine 
5. rebuild(vm_name, image) : rebuild the virtual machine to another image/OS with image object.
```

Currently, major providers usually charge users according to their usage. It might be 
finacially wise sometimes to shift between different service size to reduce unnecessary cost.
VmRefactor is designed based on this idea to help users to achieve higher cost efficiency. VmRefactor can also help users navigate 
thier management tasks especially when they have many different tasks on the run=.
 

 
 ## Flask Rest API (Sachith)
 
 
The cloudmesh REST Api is built using flask and provides the cloud information retrieval functionality through HTTP calls.

#### Pre-requisites

Use pip install to install the following packages.

- Flask
- Flask-PyMongo

#### How to run the REST API

```bash
$ cms admin rest status
$ cms admin rest start
$ cms admin rest stop
```

- Navigate to the cm directory. example:

```bash
cd ~/git/cloudmesh/cm
```

- Configure cloudmesh

```bash
pip install .
```

- Add the MongoDB information in the cloudmesh configuration file

```bash
emacs ~/.cloudmesh/cloudmesh.yaml
```

- Run the REST API

```bash
python cm4/flask_rest_api/rest_api.py
```

#### API

- `/vms/` : Provides information on all the VMs.
- `/vms/stopped`  : Provides information on all the stopped VMs.
- `/vms/<id>` : Provides information on the VM identified by the <id>

#### Examples

- Retrieve information about a VM

  ```bash 
  curl localhost:5000/vms/i-0fad7e92ffea8b345
  ```

#### Dev - restricting certain ips for certain rest calls

```python
from flask import abort, request
from cm4.flask_rest_api.app import app


@app.before_request
def limit_remote_addr():
    if request.remote_addr != '10.20.30.40':
        abort(403)  # Forbidden
```
 
 ## Extra: Run Command/Script in AWS 
 
The `cloudmesh-cloud/aws/CommandAWS.py` contains some methods to run commands/scripts from local to remote AWS virtual machines.
Any command/script operations executed by `CommandAWS.py` would be saved into MongoDB.
 
In `cloudmesh-cloud`, we use python running *ssh* client to connect the AWS virtual machines. Before running the commands 
or scripts remotely, the `CommandAWS.py` would create the job document in MongoDB for saving the experiment information.
This job document contains the information of virtual machine name, the running command or script, and job status, input, 
output and description. Meanwhile, the job document_id would be added into status document of the `status` collection for 
describing the job history of each virtual machine.
 
For example, user wants to run `pwd` command to `base-cloudmesh-yulou-5` machine in AWS.

```commandline
$ cms aws run command pwd --vm=base-cloudmesh-yuluo-5
Running command pwdin Instance base-cloudmesh-yuluo-5:
/home/ubuntu
```

The `job` collection and `status` collection in MongoDB will have below document:

```commandline
> db.job.find()
{ "_id" : ObjectId("5c09ff9b284fa4515ee9e204"), "name" : "base-cloudmesh-yuluo-5", "status" : "done", 
"input" : "Null", "output" : "/home/ubuntu\n", "description" : "single job", "commands" : "pwd" }
> db.status.find()
{ "_id" : ObjectId("5c09ff9b284fa4515ee9e205"), "id" : "base-cloudmesh-yuluo-5", "status" : "No Job", 
"currentJob" : "Null", "history" : [ "5c09ff9b284fa4515ee9e204" ] }
``` 

If user run script file containing '#!/bin/sh\npwd' in `base-cloudmesh-yulou-5` machine:

```commandline
$ cms aws run script /Users/yuluo/Desktop/cm.sh --vm=base-cloudmesh-yuluo-5
Running command /Users/yuluo/Desktop/cm.shin Instance base-cloudmesh-yuluo-5:
/home/ubuntu
```

The `job` collection and `status` collection in MongoDB will have below document:

```commandline
> db.job.find()
{ "_id" : ObjectId("5c09ff9b284fa4515ee9e204"), "name" : "base-cloudmesh-yuluo-5", "status" : "done", 
"input" : "Null", "output" : "/home/ubuntu\n", "description" : "single job", "commands" : "pwd" }
{ "_id" : ObjectId("5c0a00a8284fa451d0ab427d"), "name" : "base-cloudmesh-yuluo-5", "status" : "done", 
"input" : "#!/bin/sh\npwd", "output" : "/home/ubuntu\n", "description" : "single job", "commands" : "Null" }
```

```commandline
> db.status.find()
{ "_id" : ObjectId("5c09ff9b284fa4515ee9e205"), "id" : "base-cloudmesh-yuluo-5", "status" : "No Job", 
"currentJob" : "Null", "history" : [ "5c09ff9b284fa4515ee9e204", "5c0a00a8284fa451d0ab427d" ] }
```

