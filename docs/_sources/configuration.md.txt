# Configuration (ok)

The Configuration of cloudmesh is controled with a yaml file that is placed in
`~/.clloudmesh/cloudmesh4.yaml`. It is created automatically from the templace
located at

* <https://github.com/cloudmesh/cloudmesh-cloud/blob/master/cloudmesh/etc/cloudmesh4.yaml>

You can customize the file in your local directory.

## Clouds (proposed)

The default yaml file includes templates to configure various clouds. YOu can
change these defaults and provide access to your cloud credentials to make the
management of cloud virtual machines easier. Templates for AWS, Azure, Google,
OpenStack are provided. Specific templates for Jetstream and Chameleopn cloud
are included

## Virtual Clusters (proposed)

## Aminsistartive Services

### MongoDB (ok)

The cache of cloudmesh is managed in a mongo db database with various
collections. However the user does not have to manage thes collections as this
is done for the user through cloudmesh. The mongo db can be started and stoped
with the command

```bash
$cms admin mongo start
$cms admin mongo stop
```

Before you can use it mongo needs to be installed and basic authentication needs
to be enabled with

```bash
$cms admin mongo install
$cms admin mongo create
```

The configuration detals are included in the yaml file.

### REST (proposed)

TBD

## Log File (proposed)

Log files are stored by default in `~/.cloudmesh/log` The directory can be
specified in the yaml file.

## Encryption (proposed)

The yaml file can also be encrupted which is done with the command

```bash
$cms admin encrypt
```

It will replace the yaml file with an encryoted version while using your public
private key/ You can keep the file encripted and use the command

```bash
$ssh-add
```

to access the file without using the password whenefer it is accessed.