# Cloudmesh yaml file

cpy the file

* <https://github.com/cloudmesh/cloudmesh-cloud/blob/master/cloudmesh/etc/cloudmesh4.yaml>

to `~/.cloudmesh/cloudmesh4.yaml`

```bash
$ put hed the code for thsi wit h git and so on wget or curl
```

make sure the permissions are 


Next edit the yaml file and add your credentials.

## Variables

### Replacing home 

Values in the yaml file that incluse a ~ or $HOME will be replaced with the home
directory.

Vales starting with . will be replaced with the current working directory.

In addition any value that includes strings such as `"{cloudmesh.attribute}"`
will be replaced with the value from within the yaml file.


For example. ;et us assume the yaml file contains:

from cloudmesh.management.configuration.config import Config

cloudmesh4.yaml:

```python
script =
"""
cloudmesh:
  profile:
    name: Gregor
  cloud:
    aws:
      username: "{cloudmesh.grofile.name}"
      key: ~/.ssh/id_rsa
      dir: $HOME
      current: .
```

will result be transformed with 

data = Config()

to for example

```
cloudmesh:
  profile:
    name: Gregor
  cloud:
    aws:
      username: "Gregor"
      key: /home/gergor/.ssh/id_rsa
      dir: /home/gregor
      current: /home/gregor/github/cm
```

end converted to a dict. The data in the cloudmesh4.yaml file stays unchanegd.


