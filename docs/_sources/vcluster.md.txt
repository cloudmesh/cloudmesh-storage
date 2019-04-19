# Virtual Cluster (in progress)

This is a tool used to submit jobs to remote hosts in parallel and contains the following subcommands: 

```console
cms vcluster create virtual-cluster VIRTUALCLUSTER_NAME --clusters=CLUSTERS_LIST [--computers=COMPUTERS_LIST] [--debug]
cms vcluster destroy virtual-cluster VIRTUALCLUSTER_NAME
cms vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
cms vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
cms vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]]  [--download-now [default=True]]  [--debug]
cms vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
cms vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout+file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
cms vcluster set-param runtime-config CONFIG_NAME PARAMETER VALUE
cms vcluster destroy runtime-config CONFIG_NAME
cms vcluster list virtual-clusters [DEPTH [default:1]]
cms vcluster list runtime-configs [DEPTH [default:1]]
cms vcluster run-script --script-path=SCRIPT_PATH --job-name=JOB_NAME --vcluster-name=VIRTUALCLUSTER_NAME --config-name=CONFIG_NAME --arguments=SET_OF_PARAMS --remote-path=REMOTE_PATH> --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
cms vcluster fetch JOB_NAME
cms vcluster clean-remote JOB_NAME PROCESS_NUM
cms vcluster test-connection VIRTUALCLUSTER_NAME PROCESS_NUM
```

As can be seen, the command `vcluster` can be called with XX possible
options:

* create 
  * virtual-cluster
  * runtime-config
* destroy
  * virtual-cluster
  * runtime-config
* list
  * virtual-clusters
  * runtime-configs
* set-param
  * virtual-cluster
  * runtime-config 
* run-script
* fetch
* clean-remote
* test-connection

The information needed to create a virtual cluster, are extracted from
the `yaml` file of the cloudmesh v4, aka `cms`, however, it does not
modify that file. Instead, it will create a new configuration file in
a folder called `vcluster_workspace`. This newly generate
configuration file contains all the information about the virtual
clusters, runtime configurations as well as submitted jobs and
therefore the file is crucial for fetching the result of the previous
runs. Although possible, it is highly recommended not to modify the
file directly but instead use the `set-param` command to modify the
file.

When you are creating a virtual cluster, you can *pick* your nodes of
interest from the cloudmesh configuration and just pass it as an
argument to `create virtual-cluster` and you will have your *Virtual
Cluster* created this way. When you are done with a Virtual Cluster,
aka `vcluster`, you can simply destroy it.

## Creating a Virtual Cluster and testing connections

Consider the following two dummy clusters in the `cloudmesh4.yaml` file:

```yaml
cloudmesh: 
	...
    vcluster_test1:
      computer_a:
        name: machine1
        label: one
        address: localhost
        credentials:
          sshconfigpath: ~/vms/ubuntu14/sshconfig1
      computer_b:
        name:                       computer_a
        label:                      one
        address:                    localhost
        credentials:
          username:                 TBD
          pulickey:                 ~/.ssh/id_rsa.pub
    vcluster_test2:
      c2:
        name: machine2
        label: two
        address: localhost
        credentials:
          sshconfigpath: ~/vms/ubuntu14/sshconfig2
    ...
```



Suppose you want to create a virtual cluster called `new_vcluster`
using `computer_a` from `vcluster_test1` and `c2` from
`vcluster_test2`. This can be achieved using the following command:

```console
$ cms vcluster create virtual-cluster vcluster1 --clusters=vcluster_test1,vcluster_test2 --computers=computer_a,c2
Virtual cluster created/replaced successfully.
```

This command will create the `vcluster.yaml` file in the
`vcluster_workspace` folder and will keep the information about the
virtual cluster in there. Now, we can get the information about the
virtual cluster that we just created:

```console
$ cms vcluster list virtual-clusters
 vcluster1:
	 computer_a
	 c2
```

By passing a depth higher than one as an extra argument, you can get
more information about the virtual clusters:

```console
$ cms vcluster list virtual-clusters 2
 vcluster1:
	 computer_a:
		 name:
			 machine1
		 label:
			 one
		 address:
			 localhost
		 credentials:
			 sshconfigpath
	 c2:
		 name:
			 machine2
		 label:
			 two
		 address:
			 localhost
		 credentials:
			 sshconfigpath

```

Now that the virtual cluster is created, we can test the connection to
the remote nodes. We will try that using 2 processes in parallel:

```console
$ cms vcluster test-connection vcluster1 2
Node computer_a is accessible.
Node c2 is accessible.
```

The output indicates that both nodes in the `vcluster1` are
accessible. In case you did not need the `vcluster1` anymore, you can
easily remove it using:

```console
$ cms vcluster destroy virtual-cluster vcluster1
Virtual-cluster vcluster1 destroyed successfully.
```

## Creating a runtime-configuration 

Next, we have to create a `runtime-configuration` which defines the
type of input and output for possibly a set of jobs that are going to
be submitted later.  In the next example we will create a runtime
configuration for jobs that we want to run remotely using 5 processes,
fetch their results using 3 processes and the script that we want to
run remotely takes just some parameter (which could be left empty for
no parameters), and the output of the script is going to be printed on
the standard output, and suppose we want to just submit the jobs for
running on remote nodes and download them later (hence the
`--download-later` flag):

```console
$ cms vcluster create runtime-config ParamInStdOut 5 in:params out:stdout --fetch-proc-num=3 --download-later
Runtime-configuration created/replaced successfully.
```

Let's get the list of runtime configurations to make sure our
configuration is created as we expected:

```console
$ cms vcluster list runtime-configs 2
 ParamInStdOut:
	 proc_num:
		 5
	 download_proc_num:
		 1
	 download-later:
		 False
	 input-type:
		 params
	 output-type:
		 stdout
```

Similar to the virtual cluster, you can remove a runtime-configuration
using the `destroy` sub-command:

```console
$ cms vcluster destroy runtime-config ParamInStdOut
Runtime-configuration ParamInStdOut destroyed successfully.
```

## Running Parallel Remote Jobs 

Now that we have both the virtual cluster and runtime configuration
ready, we can try to submit a batch job to our virtual cluster using
`cms vcluster run-script`. This is by far the most complicated
sub-command of the `vcluster`, however, the name of the arguments are
pretty clear and looking at the names you would be able to pretty much
find your way. In the next example, we submit the
`inf_script_stdin_stdout.sh` file to the nodes of `vcluster1` and
using the `ParamInStdOut` configuration we run 10 instance of that
script on the virtual cluster. This script will be copied and run on
the home directory of the remote nodes (`~/`).  Note that even though
the remote path is set to home directory, for each job a folder with a
unique suffix will be created to avoid conflicts. Also, note that this
script does not take any argument, but we indicated 10 `_` separated
by commas as a meaningless argument. This will notify the tool that
you need 10 instances of this script to be executed:

```console
$ cms vcluster run-script --script-path=./cm4/vcluster/sample_scripts/inf_script_stdin_stdout.sh --job-name=TestJob1 --vcluster-name=vcluster1 --config-name=ParamInStdOut --arguments=_,_,_,_,_,_,_,_,_,_ --remote-path=~/ --local-path=./cm4/vcluster/sample_output --overwrite
Remote Pid on c2: 10104
Remote Pid on c2: 10109
Remote Pid on c2: 10402
Remote Pid on computer_a: 8973
Remote Pid on computer_a: 8979
Remote Pid on computer_a: 8983
Remote Pid on computer_a: 9464
Remote Pid on c2: 10884
Remote Pid on c2: 10993
Remote Pid on computer_a: 9592
collecting results
waiting for other results if any...
Results collected from c2.
Results collected from c2.
Results collected from c2.
Results collected from computer_a.
Results collected from computer_a.
Results collected from computer_a.
Results collected from computer_a.
Results collected from c2.
Results collected from c2.
Results collected from computer_a.
waiting for other results if any...
All of the remote results collected.
```

As you can see all of the jobs were submitted (using 5 processes) and
results were collected afterwards (using 3 processes). We can check
the existence of the results:

```console
$ ll ./cloudmesh-cloud/vcluster/sample_output/
total 48
drwxr-xr-x 2 corriel 4096 Oct 31 22:12 ./
drwxr-xr-x 8 corriel 4096 Oct 31 22:12 ../
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_0_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_1_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_2_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_3_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_4_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_5_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_6_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_7_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_8_20181031_22123465
-rw-r--r-- 1 corriel  255 Oct 31 22:12 outputfile_9_20181031_22123465
```

Now, suppose the jobs were going to take so long that we could not
wait for the results and we had to download them later. To prepare
this scenario, we can set the `download-later` attribute of the
runtime configuration to `true`:

```console
$ cms vcluster set-param runtime-config ParamInStdOut download-later true
Runtime-configuration parameter download-later set to true successfully.
```

Now that we set this parameter, we can submit the jobs and this time
the tool will not wait for the results:

```console
$ cms vcluster run-script --script-path=./cloudmesh-cloud/vcluster/sample_scripts/inf_script_stdin_stdout.sh --job-name=TestJob1 --vcluster-name=vcluster1 --config-name=ParamInStdOut --arguments=_,_,_,_,_,_,_,_,_,_ --remote-path=~/ --local-path=./cloudmesh-cloud/vcluster/sample_output --overwrite
Remote Pid on c2: 12981
Remote Pid on c2: 12987
Remote Pid on c2: 13280
Remote Pid on computer_a: 11858
Remote Pid on computer_a: 11942
Remote Pid on computer_a: 11945
Remote Pid on computer_a: 12300
Remote Pid on c2: 13795
Remote Pid on computer_a: 12427
Remote Pid on c2: 13871
```

As you can see, the jobs are submitted and the script is
finished. Note that since a job with that exact job name exists, you
cannot submit the job unless you use the `--overwrite` flag. Now that
we have submitted the jobs and their results are ready, we can fetch
their produced results using the `fetch` command and all results will
be collected using the same number of processes that were indicated in
the runtime-configuration using which the job was submitted in the
first place:

```console
$ cms vcluster fetch TestJob1
collecting results
Results collected from c2.
Results collected from c2.
Results collected from c2.
Results collected from computer_a.
Results collected from computer_a.
Results collected from computer_a.
Results collected from c2.
Results collected from computer_a.
Results collected from computer_a.
Results collected from c2.
waiting for other results if any...
All of the remote results collected.
```

## Cleaning the remote

By default the Virtual Cluster tool does not clean the remotes
automatically and this task is left to be performed manually since
important results might be lose due to mistakes. To clean the remotes,
the user has to explicitly use the `clean-remote` command for a
specific job and this way only the results of that particular job will
be removed from **ALL** remotes using 2 parallel processes:

```console
$ cms vcluster clean-remote TestJob1 4
Node c2 cleaned successfully.
Node computer_a cleaned successfully.
```
