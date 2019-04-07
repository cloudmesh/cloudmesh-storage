import cloudmesh.storage.provider.gdrive.Provider
import cloudmesh.storage.provider.box.Provider
import cloudmesh.storage.provider.awss3.Provider
import cloudmesh.storage.provider.azureblob.Provider
from cloudmesh.common.console import Console


class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))


    def _provider(self, service):
        provider = None
        if service == "gdrive":
            provider = cloudmesh.storage.provider.gdrive.Provider.Provider()
        elif service == "box":
            provider = cloudmesh.storage.provider.box.Provider.Provider()
        elif service == "aws":
            provider = cloudmesh.storage.provider.awss3.Provider.Provider()
        elif service == "azureblob":
            provider = cloudmesh.storage.provider.azureblob.Provider.Provider(service)

        return provider

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

