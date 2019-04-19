# Virtual Machine Management (proposed)

CLoudmesh v4 contains sophisticated virtual machine management services that
makes it easy for the user to manage a large number of virtual machines across
clouds with a uniform naming scheme.

For now we will focus on the command line and shell interface.

## Command Line and Shell Interface

The command line and shell interface to manage virtual machines are listed next.
```
vm ping [NAMES] [--cloud=CLOUDS] [N]
vm check [NAMES] [--cloud=CLOUDS]
vm refresh [NAMES] [--cloud=CLOUDS]
vm status [NAMES] [--cloud=CLOUDS]
vm console [NAME] [--force]
vm start [NAMES] [--cloud=CLOUD] [--dryrun]
vm stop [NAMES] [--cloud=CLOUD] [--dryrun]
vm terminate [NAMES] [--cloud=CLOUD] [--dryrun]
vm delete [NAMES] [--cloud=CLOUD] [--dryrun]
vm list [NAMES]
        [--cloud=CLOUDS]
        [--output=OUTPUT]
        [--refresh]
vm boot [--name=NAME]
        [--cloud=CLOUD]
        [--username=USERNAME]
        [--image=IMAGE]
        [--flavor=FLAVOR]
        [--public]
        [--secgroup=SECGROUPs]
        [--key=KEY]
        [--dryrun]
vm boot [--n=COUNT]
        [--cloud=CLOUD]
        [--username=USERNAME]
        [--image=IMAGE]
        [--flavor=FLAVOR]
        [--public]
        [--secgroup=SECGROUPS]
        [--key=KEY]
        [--dryrun]
vm run [--name=NAMES] [--username=USERNAME] [--dryrun] COMMAND
vm script [--name=NAMES] [--username=USERNAME] [--dryrun] SCRIPT
vm ip assign [NAMES]
          [--cloud=CLOUD]
vm ip show [NAMES]
           [--cloud=CLOUD]
           [--output=OUTPUT]
           [--refresh]
vm ip inventory [NAMES]
vm ssh [NAMES] [--username=USER]
         [--quiet]
         [--ip=IP]
         [--key=KEY]
         [--command=COMMAND]
         [--modify-knownhosts]
vm rename [OLDNAMES] [NEWNAMES] [--force] [--dryrun]
vm wait [--cloud=CLOUD] [--interval=SECONDS]
vm info [--cloud=CLOUD]
        [--output=OUTPUT]
vm username USERNAME [NAMES] [--cloud=CLOUD]
vm resize [NAMES] [--size=SIZE]
```

## Uniform Parameter Management

The parameters across thes commands are uniformly managed. Most of the plural
form allow a parameterized specification such as `a[00-03],a8` which would
result in an array `["a0", "a1", "a2", "a3", "a8"]`. This especially applies to
clouds as well as virtual machine names.


We destinguish the following parameterized options

:--cloud=CLOUDS: which specifies one or more clouds in parameterized fashion 

:--names=NAMES: which specifies one or more clouds in parameterized fashion 

We distinguish the following regular options

:--interval=INTERVAL: a specified interval in seconds

:--output=OUTPUT: The output format: txt, csv, table

:--refresh: To update the state of the vms specified with clouds and names

:--username=USERNAME: The username to be used for conectiing with the vm

:--quiet: do not print debug messages

:--dryrun: do not execute the command, but just print what would happen
        
:--ip=IP: specify a public IP
         
:--key=KEY: start the vm with the keypair name

## Virtual machine management

Virtual machines can be 

* Created
* Started
* Stoped
* Suspended
* Resumed
* Destroyed

Default behavior such as a key management nameing scheme as well as ip adress
and security management is conveniently provided

## Key management

Access to the virtual machien is governed by SSH keys. The default key can be
uploaded to the cloud with the key command. The name of the key in the cloud can
be used to associate it with virtual machines so that this key can be used to
log into the VM


## Security groups

A security group acts as a virtual firewall for the instance. When we launch a
instance, we want to attach security Groups for controlling the traffic in and
out of the VM.


## Command Examples

### Ping

m ping [NAMES] [--cloud=CLOUDS] [N]

### Check

vm check [NAMES] [--cloud=CLOUDS]

### Refersh

vm refresh [NAMES] [--cloud=CLOUDS]

### Status

vm status [NAMES] [--cloud=CLOUDS]

### Console

vm console [NAME] [--force]

### Start

vm start [NAMES] [--cloud=CLOUD] [--dryrun]

### Stop

vm stop [NAMES] [--cloud=CLOUD] [--dryrun]

### Terminate

vm terminate [NAMES] [--cloud=CLOUD] [--dryrun]

### Delete

vm delete [NAMES] [--cloud=CLOUD] [--dryrun]
