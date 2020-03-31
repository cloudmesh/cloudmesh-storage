#test_gdrive.py
from cloudmesh.storage.provider.parallelgdrive.Provider import Provider
p = Provider(service='parallelgdrive', config="~/.cloudmesh/cloudmesh.yaml")
print(p.storage.service)
#print(p.create_dir())
#print(p.list())
print(p.get_credentials())
#print
#print
