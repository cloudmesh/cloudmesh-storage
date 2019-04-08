from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider
from cloudmesh.storage.provider.azureblob.Provider import \
    Provider as AzureblobProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.local.Provider import Provider as LocalProvider
from cloudmesh.storage.StorageABC import StorageABC

#from cloudmesh.storage.provider.gdrive.Provider import \
#    Provider as GdriveProvider
# from cloudmesh.DEBUG import VERBOSE

from pprint import pprint



class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(service=service, config=config)
        self.provider = self.get_provider(self.kind)

    def get_provider(self, kind):
        provider = None
        if kind == "local":
            provider = LocalProvider()
        if kind == "box":
            provider = BoxProvider()
        # elif kind == "gdrive":
        #    provider = GdriveProvider()
        elif kind == "azureblob":
            provider = AzureblobProvider()
        elif kind == "awss3":
            provider = AwsProvider()
        else:
            raise ValueError(f"Storage provider {kind} not yet supported")
        return provider

    def get(self, service=None, source=None, destination=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        pprint(f"get {service} {source} {destination} {recursive}")
        d = self.provider.get(service=service,
                              source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def put(self, service=None, source=None, destination=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        pprint(f"put {service} {source}")
        d = self.provider.put(service=service,
                              source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def createdir(self, service=None, directory=None):
        # BUG DOES NOT FOLLOW SPEC
        pprint(f"create_dir {directory}")
        print(directory)
        d = self.provider.create_dir(service=service, directory=directory)
        return d

    def delete(self, service=None, source=None):
        pprint(f"delete filename {service} {source}")
        self.provider.delete(service=service, source=source)
        raise ValueError("must return a value")

    def search(self, service=None, directory=None, filename=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        print(f"search {directory}")
        d = self.provider.search(service=service,
                                 directory=directory,
                                 filename=filename,
                                 recursive=recursive)
        return d

    def list(self, service=None, source=None, recursive=None):
        # BUG DOES NOT FOLLOW SPEC
        pprint(f"list {source}")
        d = self.provider.list(service=service,
                               source=source,
                               recursive=recursive)
        return d

