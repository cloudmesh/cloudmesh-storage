# Quickstart (proposed)

One of the features up Cloudmesh is to easily start new virtual machines on
vairous clouds. It uses defaults for these clouds that can be chaned, but are
easily stored in a yaml file located at  `~/.cloudmesh/cloudmesh4.yaml` This
file is  created upon first start of the shell. You need to edit it and include
some of your cloud information.

## Commandline (proposed)

It is easy to switch beteeen clouds with the set command. Ater the set and
specifying the cloud by name many commands will default to that cloud. The
exception is the `vm list` command that lists by default all vms on all clouds.
In addition the `vm refresh` command will also work on all clouds.

```bash
$ cms admin mongo start

$ cms set cloud=vagrant
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=aws
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=azure
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=chameleon
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=jetstream
$ cms vm start
$ cms image list
$ cms flavor list

$ cms vm refresh

$ cms vm list
```

In case you want a command explicitly apply to one or more clouds or one or more
vms, they can be specified by name such as

```bash
$ cms vm list --name vm[0-100]
$ cms vm list --cloud aws,azure
```

Defaults for the cloud and the name can be specified through set such as

```bash
$ cms set name=vm[0-100]
$ cms set cloud=aws,azure
```

Using the commands

```bash
$ cms vm list
```

would than add the appropriate options to the command. To reset the show to all
vms set name and cloud to all


```bash
$ cms set name=all
$ cms set cloud=all
```


## Interactive shell (proposed)

Cloudmesh uses cmd5 for its shell implementation and thus all commands that are
typed in in the terminal can also be typed in into a shell that is started with
cms

```bash
$ cms
cms> set cloud=aws
cms> vm start
```

## Command scripts (ok)

As we use cmd5 we also have access to piped and named scripts with

```bash
$ echo script.cms | cms
```

and

```bash
$ cms --script script.cms
```

## Cache (proposed)

All information about for example virtual machines are cached locally. The cache
for various information sources can be explicitly updated with the `--refresh`
flag. Thus the command

```bash
$ cms vm list --refresh
```

would first execute a refresh while the command

```bash
$ cms vm list 
```

would only read from the local cache

To chang ethe behavior and alwas do a refresh you can use the command

```bash
$ cms set refresh=True
```

To switch it off you can say 

```bash
$ cms set refresh=False
```

## Manual (ok)

The manaul page can be opened with 

```bash
$ cms open doc
```

or in case you start it in the source with 

```bash
$ cms open doc local
```


