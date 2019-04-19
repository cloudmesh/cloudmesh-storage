## REST Service (outdated)

The REST Api is built using flask and provides the cloud
information retrieval functionality through HTTP calls.

#### Pre-requisites

Use pip install to install the following packages.

- Flask
- Flask-PyMongo

#### How to run the REST API

- Navigate to the cm directory. example:

```bash
cd ~/git/cloudmesh/cm
```

- Configure cloudmesh

```bash
pip install .
```

- Add the MongoDB information in the configuration file

```bash
vi ~/.cloudmesh/cloudmesh4.yaml
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
