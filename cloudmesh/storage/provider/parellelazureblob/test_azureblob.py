from Provider import Provider
from cloudmesh.common.util import path_expand

#
# TODO
#
location = path_expand(".cloudmesh/cloudmesh.yaml")
p = Provider(service="azure", config=location)
print(p.credentials)

