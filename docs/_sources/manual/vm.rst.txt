vm
==

::

    Usage:
        vm default [--cloud=CLOUD][--output=OUTPUT]
        vm refresh [all][--cloud=CLOUD]
        vm boot [--name=NAME]
                [--cloud=CLOUD]
                [--username=USERNAME]
                [--image=IMAGE]
                [--flavor=FLAVOR]
                [--group=GROUP]
                [--public]
                [--secgroup=SECGROUP]
                [--key=KEY]
                [--dryrun]
        vm boot [--n=COUNT]
                [--cloud=CLOUD]
                [--username=USERNAME]
                [--image=IMAGE]
                [--flavor=FLAVOR]
                [--group=GROUP]
                [--public]
                [--secgroup=SECGROUP]
                [--key=KEY]
                [--dryrun]
        vm ping [NAME] [N]
        vm run [--name=NAMES] [--username=USERNAME] COMMAND
        vm script [--name=NAMES] [--username=USERNAME] SCRIPT
        vm console [NAME]
                 [--group=GROUP]
                 [--cloud=CLOUD]
                 [--force]
        vm start [NAMES]
                 [--group=GROUP]
                 [--cloud=CLOUD]
                 [--force]
        vm stop [NAMES]
                [--group=GROUP]
                [--cloud=CLOUD]
                [--force]
        vm terminate [NAMES]
                  [--group=GROUP]
                  [--cloud=CLOUD]
                  [--force]
        vm delete [NAMES]
                  [--group=GROUP]
                  [--cloud=CLOUD]
                  [--keep]
                  [--dryrun]
        vm ip assign [NAMES]
                  [--cloud=CLOUD]
        vm ip show [NAMES]
                   [--group=GROUP]
                   [--cloud=CLOUD]
                   [--output=OUTPUT]
                   [--refresh]
        vm ip inventory [NAMES]
                        [--header=HEADER]
                        [--file=FILE]
        vm ssh [NAME] [--username=USER]
                 [--quiet]
                 [--ip=IP]
                 [--cloud=CLOUD]
                 [--key=KEY]
                 [--command=COMMAND]
                 [--modify-knownhosts]
        vm rename [OLDNAMES] [NEWNAMES] [--force] [--dryrun]
        vm list [NAMES]
                [--cloud=CLOUDS|--active]
                [--group=GROUP]
                [--output=OUTPUT]
                [--refresh]
        vm status [NAMES]
        vm wait [--cloud=CLOUD] [--interval=SECONDS]
        vm info [--cloud=CLOUD]
                [--output=OUTPUT]
        vm check NAME
        vm username USERNAME [NAMES] [--cloud=CLOUD]
        vm resize [SIZE]

    Arguments:
        COMMAND        positional arguments, the commands you want to
                       execute on the server(e.g. ls -a) separated by ';',
                       you will get a return of executing result instead of login to
                       the server, note that type in -- is suggested before
                       you input the commands
        NAME           server name. By default it is set to the name of last vm from database.
        NAMES          server name. By default it is set to the name of last vm from database.
        KEYPAIR_NAME   Name of the openstack keypair to be used to create VM. Note this is
                       not a path to key.
        NEWNAMES       New names of the VM while renaming.
        OLDNAMES       Old names of the VM while renaming.

    Options:
      -H --modify-knownhosts  Do not modify ~/.ssh/known_hosts file when ssh'ing into a machine
        --username=USERNAME  the username to login into the vm. If not specified it will be guessed
                             from the image name and the cloud
        --ip=IP          give the public ip of the server
        --cloud=CLOUD    give a cloud to work on, if not given, selected
                         or default cloud will be used
        --count=COUNT    give the number of servers to start
        --detail         for table print format, a brief version
                         is used as default, use this flag to print
                         detailed table
        --flavor=FLAVOR  give the name or id of the flavor
        --group=GROUP          give the group name of server
        --secgroup=SECGROUP    security group name for the server
        --image=IMAGE    give the name or id of the image
        --key=KEY        specify a key to use, input a string which
                         is the full path to the private key file
        --keypair_name=KEYPAIR_NAME   Name of the openstack keypair to be used to create VM.
                                      Note this is not a path to key.
        --user=USER      give the user name of the server that you want
                         to use to login
        --name=NAME      give the name of the virtual machine
        --force          rename/ delete vms without user's confirmation
        --command=COMMAND
                         specify the commands to be executed


    Description:
        commands used to boot, start or delete servers of a cloud

        vm default [options...]
            Displays default parameters that are set for vm boot either on the
            default cloud or the specified cloud.

        vm boot [options...]
            Boots servers on a cloud, user may specify flavor, image .etc, otherwise default values
            will be used, see how to set default values of a cloud: cloud help

        vm start [options...]
            Starts a suspended or stopped vm instance.

        vm stop [options...]
            Stops a vm instance .

        vm delete [options...]
            Delete servers of a cloud, user may delete a server by its name or id, delete servers
            of a group or servers of a cloud, give prefix and/or range to find servers by their names.
            Or user may specify more options to narrow the search

        vm floating_ip_assign [options...]
            assign a public ip to a VM of a cloud

        vm ip show [options...]
            show the ips of VMs

        vm ssh [options...]
            login to a server or execute commands on it

        vm list [options...]
            same as command "list vm", please refer to it

        vm status [options...]
            Retrieves status of last VM booted on cloud and displays it.

    Tip:
        give the VM name, but in a hostlist style, which is very
        convenient when you need a range of VMs e.g. sample[1-3]
        => ['sample1', 'sample2', 'sample3']
        sample[1-3,18] => ['sample1', 'sample2', 'sample3', 'sample18']

    Quoting commands:
        cm vm login gvonlasz-004 --command="uname -a"

