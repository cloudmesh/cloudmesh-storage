from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider
from cloudmesh.storage.provider.azureblob.Provider import \
    Provider as AzureblobProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.gdrive.Provider import \
    Provider as GdriveProvider
from cloudmesh.terminal.Terminal import VERBOSE


class Provider(object):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(service=service, config=config)
        self.provider = self.get_provider(self.kind)

    def get_provider(self, kind):
        provider = None
        if kind == "gdrive":
            provider = GdriveProvider()
        elif kind == "box":
            provider = BoxProvider()
        elif kind == "azureblob":
            provider = AzureblobProvider()
        elif kind == "awss3":
            provider = AwsProvider()
        else:
            raise ValueError(f"Storage provider {kind} not yet supported")
        return self.provider

    def get(self, service=None, source=None, destination=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        VERBOSE.print(f"get {service} {source} {destination} {recursive}",
                      verbose=9)
        d = self.provider.get(service=service,
                              source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def put(self, service=None, source=None, destination=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        VERBOSE.print(f"put {service} {source}", verbose=9)
        d = self.provider.put(service=service,
                              source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def createdir(self, service=None, directory=None):
        # BUG DOES NOT FOLLOW SPEC
        VERBOSE.print(f"create_dir {directory}", verbose=9)
        print(directory)
        d = self.provider.create_dir(service=service, directory=directory)
        return d

    def delete(self, service=None, source=None):
        VERBOSE.print(f"delete filename {service} {source}", verbose=9)
        self.provider.delete(service=service, source=source)
        raise ValueError("must return a value")

    def search(self, service=None, directory=None, filename=None, recursive=False):
        # BUG DOES NOT FOLLOW SPEC
        VERBOSE.print(f"search {directory}", verbose=9)
        d = self.provider.search(service=service,
                                 directory=directory,
                                 filename=filename,
                                 recursive=recursive)
        return d

    def list(self, service=None, source=None, recursive=None):
        # BUG DOES NOT FOLLOW SPEC
        VERBOSE.print(f"list {source}", verbose=9)
        d = self.provider.list(service=service,
                               source=source,
                               recursive=recursive)
        return d

