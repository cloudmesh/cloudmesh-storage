#test_gdrive.py
from cloudmesh.storage.provider.parallelgdrive.Provider import Provider
p = Provider(service='parallelgdrive', config="~/.cloudmesh/cloudmesh.yaml")
p.storage.service
#print(p.create_dir())
#print(p.list())
p.get_credentials()
