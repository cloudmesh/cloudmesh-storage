from cloudmesh.storage.provider.gdrive.Provider import \
    Provider as GdriveProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.azureblob.Provider import Provider as AzureblobProvider
from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider

from cloudmesh.common.console import Console


class Provider(object):

    def __init__(self, cloud=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(cloud=cloud, config=config)
        self.provider = None

        if self.kind == "gdrive":
            self.provider = GdriveProvider()
        elif self.kind == "box":
            self.provider = BoxProvider()
        elif self.kind == "azureblob":
            self.provider = AzureblobProvider()
        elif self.kind == "awss3":
            self.provider = AwsProvider()
        else:
            raise ValueError(f"Storage provider {cloud} not yet supported")

    def get(self, service, source, destination, recursive):
        Console.ok(f"get {service} {source} {destination} {recursive}")
        provider = self._provider(service)
        d = provider.get(service, source, destination, recursive)
        return d

    def put(self, service, source, destination, recursive):
        Console.ok(f"put {service} {source}")
        provider = self._provider(service)
        d = provider.put(service, source, destination, recursive)
        return d

    def createdir(self, service, directory):
        Console.ok(f"create_dir {directory}")
        provider = self._provider(service)
        print(directory)
        d = provider.create_dir(service, directory)
        return d

    def delete(self, service, source):
        Console.ok(f"delete filename {service} {source}")
        provider = self._provider(service)
        provider.delete(service, source)

    def search(self, service, directory, filename, recursive):
        Console.ok(f"search {directory}")
        provider = self._provider(service)
        d = provider.search(service,directory, filename, recursive)
        return d

    def list(self, service, source, recursive):
        Console.ok(f"list {source}")
        provider = self._provider(service)
        d = provider.list(service, source, recursive)
        return d

