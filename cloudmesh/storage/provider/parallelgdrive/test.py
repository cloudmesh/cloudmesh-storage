# From Niranda 4-16-20 for testing
# cms set storage=parallelaws3

from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.provider.parallelawss3.Provider import Provider

user = Config()["cloudmesh.profile.user"]

# cms set storage=parallelazure
variables = Variables()
service = variables.parameter('storage')

print(f"Test run for {service}")

if service is None:
    raise ValueError("storage is not set")

provider = Provider(service=service)
print('provider:', provider, provider.kind)

provider.mkdir_run(specification={
    "action": "mkdir",
    "path": "/tmp/test",
    "status": "waiting" })

output_spec = provider.list(source="/tmp/test", dir_only=False, recursive=False)
print(output_spec)

output = provider.list_run(specification=output_spec)

output = provider.list_run(specification={
    "action": "list",
    "source": "/tmp/test",
    "dir_only": "false",
    "recursive": "false",
    "status": "waiting"
})

print(output)

