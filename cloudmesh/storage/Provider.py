from cloudmesh.storage.provider.gdrive.Provider import \
    Provider as GdriveProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.StorageABC import StorageABC


#
# bug does not follow the ABC class
#
class Provider(StorageABC):

    #
    # TODO: use whate we implemented in the StorageABC
    #
    def __init__(self, cloud=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(cloud=cloud, config=config)
        self.provider = None
        if self.kind == "gdrive":
            self.provider = GdriveProvider()
        elif self.kind == "box":
            self.provider = BoxProvider()
        else:
            raise ValueError(f"Storage provider {cloud} not yet supported")

    def list(self, parameter):
        print("list", parameter)
        provider = self._provider(self.service)

    def delete(self, filename):
        print("delete filename")
        provider = self._provider(self.service)
        provider.delete(filename)

    def get(self, service, filename):
        print("get", service, filename)
        provider = self._provider(service)
        provider.get(filename)

    def put(self, service, filename):
        print("put", service, filename)
        provider = self._provider(service)
        provider.put(filename)

    def search(self, service, directory, filename):
        print("search", service, directory, filename)
        provider = self._provider(service)
        provider.search(directory, filename)

    def create_dir(self, service, directory):
        print("create dir", service, directory)
        provider = self._provider(service)
        provider.create_dir(directory)
