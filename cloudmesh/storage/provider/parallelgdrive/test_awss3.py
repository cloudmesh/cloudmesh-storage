#test_awss3.py in cloudmesh-storage repository
from cloudmesh.storage.provider.parallelawss3.Provider import Provider
p = Provider(name='aws')
p.mkdir("/abcworking2")
