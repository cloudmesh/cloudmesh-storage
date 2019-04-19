# Batch

The purpose of this sub-command is to facilitate job submission on
clusters that use SLURM as their workload manager. Note that this
tools assumes that the SLURM file is properly prepared by the user and
does not modify the SLURM script in any way. Similar to other
sub-commands `batch` has several sub-commands itself:

    cms batch create-job JOB_NAME --slurm-script=SLURM_SCRIPT_PATH --input-type=INPUT_TYPE --slurm-cluster=SLURM_CLUSTER_NAME --job-script-path=SCRIPT_PATH --remote-path=REMOTE_PATH --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
    cms batch run-job JOB_NAME
    cms batch fetch JOB_NAME
    cms batch test-connection SLURM_CLUSTER_NAME
    cms batch set-param slurm-cluster CLUSTER_NAME PARAMETER VALUE
    cms batch set-param job-metadata JOB_NAME PARAMETER VALUE
    cms batch list slurm-clusters [DEPTH [default:1]]
    cms batch list jobs [DEPTH [default:1]]
    cms batch remove slurm-cluster CLUSTER_NAME
    cms batch remove job JOB_NAME
    cms batch clean-remote JOB_NAME

The main options are: 

* `create-job`: used for creating a job configuration (this does not
   run the job automatically)
* `run-job`: used for running a job configuration that is previously created. 
* `test-connection`: used for testing the connection to a SLURM cluster
* `set-param`: used for setting a parameter in any configuration key
* `list `: used for listing possible instances of an entity 
* `remove `: used for removing a cluster or job 
* `clean-remote`: used for cleaning the files of a job from a cluster 

Each of these sub-commands are reviewed in the following sections with
examples.



## Creating a job configuration

As can be seen, this sub-command has the most number of arguments and
is the vital part of the `batch` tool. The parameters are all
self-explanatory, but we will review the important ones here:

* `--slurm-script`:  defines the path to the SLURM script that is going to be submitted to the SLURM cluster. 
* `--input-type`: defines the type of input for the application that is going to be run on the cluster. This is important because if the program takes a file name as an argument, that file has to be transfered to the cluster as well. Possible values for this parameter is either `params` or `params+file`. Note that if you pass `params+file` then you have to specify the `--argfile-path` as well where you define the path to the argument file. 
* `--slurm-cluster`: defines the name of the cluster that is previously defined in cloudmesh yaml file. 
* `--job-script-path`: defines the path to the file that is going to be run on the SLURM cluster
* `--remote-path`: defines the path on SLURM cluster on which the job files are going to be copied, run and collected. 
* `--local-path`: defines the local path for saving the results. 

Consider the following example :

```
$ cms batch create-job SlurmTest1 --slurm-script=./1_argsin_stdout.slurm --input-type=params --slurm-cluster=slurm-taito --job-script-path=./1_argsin_stdout_script.sh --remote-path=~/tmp --local-path=../batch/sample_scripts/out --overwrite
```

This will create a job that looks like this in the `slurm_batch` configuration file placed in the workspace directory: 

```
slurm_cluster:
  slurm-taito:
    name: taito
    credentials:
      sshconfigpath: ~/vms/sshconfig_slurm
job-metadata:
  SlurmTest1:
    suffix: _20181206_19275141
    slurm_cluster_name: slurm-taito
    input_type: params+file
    raw_remote_path: ~/tmp
    slurm_script_path: ./4_filein_fileout.slurm
    job_script_path: ./4_filein_fileout_script.sh
    argfile_path: ./test-script-argument
    argfile_name: test-script-argument
    script_name: 4_filein_fileout_script.sh
    slurm_script_name: 4_filein_fileout.slurm
    remote_path: ~/tmp/job_20181206_19275141/
    remote_script_path: ~/tmp/job_20181206_19275141/4_filein_fileout_script.sh
    remote_slurm_script_path: ~/tmp/job_20181206_19275141/4_filein_fileout.slurm
    local_path: ../batch/sample_scripts/out

```



## Testing the connection

Note that the cluster information is already extracted and added to
this file. Therefore unlike `vcluster`, there is no need to add the
cluster manually. So far, we have just added and updated the
configuration and the job is neither submitted nor run in the cluster.
Before doing that, let's try to test our connection to the cluster:

```
$ cms batch test-connection slurm-taito
Slurm Cluster taito is accessible.
```



## Running the Job

 Now that we are sure that the ssh connection works fine, let's try to
 run the job:

```
$ cms batch run-job SlurmTest1
Remote job ID: 32846209
```

Despite the short output, this command does a lot of work behind the
seen including:

* Creating the proper folder structure in the remote 
* Copying the SLURM script, as well as the job script and the argument
  files if any.
* Submitting the job 
* Keeping the job ID and save it in the configuration file so that the
  results can be fetched later

Just for the demonstration purpose, let's check the remote folder in
the cluster and you will see that all of the files as well as the
results will be available there:

```
@taito-login3:~/tmp/job_20181206_19301175$ ll
total 28
drwxr-xr-x 2  4096 Dec  7 02:36 ./
drwx------ 3  4096 Dec  7 02:35 ../
-rwxr-xr-x 1   238 Dec  7 02:35 4_filein_fileout.slurm*
-rw-r--r-- 1     0 Dec  7 02:36 4_filein_fileout.slurm.e32846209
-rw-r--r-- 1   117 Dec  7 02:36 4_filein_fileout.slurm.o32846209
-rwxr-xr-x 1    48 Dec  7 02:35 4_filein_fileout_script.sh*
-rw-r--r-- 1    35 Dec  7 02:35 test-script-argument
-rw------- 1    35 Dec  7 02:36 test-script-output
```



## Downloading the Results

Now that the results are ready we can fetch the results using the following command: 

```
$ cms batch fetch SlurmTest1
collecting results
Results collected from taito for jobID 32846209
waiting for other results if any...
All of the remote results collected.
```

Using this, the results will be downloaded in the local path specified
in the configuration file:

```
out$ ll job_20181206_19301175/
total 1M
drwxr-xr-x 2 corriel 1M Dec  6 19:40 ./
drwxr-xr-x 3 corriel 1M Dec  6 19:40 ../
-rw-r--r-- 1 corriel 0M Dec  6 19:40 4_filein_fileout.slurm.e32846209
-rw-r--r-- 1 corriel 1M Dec  6 19:40 4_filein_fileout.slurm.o32846209
-rw------- 1 corriel 1M Dec  6 19:40 test-script-output
```



## Cleaning the remote

Now that you are done, you can easily clean the remote using:

```
$ cms batch clean-remote SlurmTest1
Job SlurmTest1 cleaned successfully.
```



## Get the list of the jobs and clusters

Naturally after working with the `batch` for a while, several jobs and clusters will be accumulated in the configuration file. You can get the list of current jobs and clusters using the following commands: 

```
$ cms batch list slurm-clusters
 slurm-taito:
	 name
	 credentials
$ cms batch list jobs
 SlurmTest1:
	 suffix
	 slurm_cluster_name
	 input_type
	 raw_remote_path
	 slurm_script_path
	 job_script_path
	 argfile_path
	 argfile_name
	 script_name
	 slurm_script_name
	 remote_path
	 remote_script_path
	 remote_slurm_script_path
	 local_path
	 jobIDs
```

It is also possible to increase the depth of the information by adding the desired depth as the next parameter: 

```
$ cms batch list slurm-clusters 2
 slurm-taito:
	 name:
		 taito
	 credentials:
		 sshconfigpath:
			 ~/vms/sshconfig_slurm
```



## Modifying the Configuration by Setting Parameters

In case you want to modify or add a configuration parameter, there is no need to directly modify the file. Indeed you can use the `set-param` command to set a key for both jobs and slurm-clusters. In the next example we will add a test-key and test-value parameter to the `slurm-taito` cluster: 

```
$ cms batch set-param slurm-cluster slurm-taito test-key test-value
slurm-cluster parameter test-key set to test-value successfully.

$ cms batch list slurm-clusters 2
 slurm-taito:
	 name:
		 taito
	 credentials:
		 sshconfigpath:
			 ~/vms/sshconfig_slurm
	 test-key:
		 test-value
```



## Removing jobs and clusters

Finally, when you are done with a job, or when a cluster is not accessible anymore, you can easily remove them from the `batch` configuration file using the following: 

```
$ cms baremove slurm-cluster slurm-taito
Slurm-cluster slurm-taito removeed successfully.
```

similarly, you can remove a obsolete job using the following command: 

```
$ cms batch remove job SlurmTest1
Job SlurmTest1 removeed successfully.
```
