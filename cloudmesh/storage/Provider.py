from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider
from cloudmesh.storage.provider.azureblob.Provider import \
    Provider as AzureblobProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.local.Provider import Provider as LocalProvider
from cloudmesh.storage.StorageNewABC import StorageABC
from cloudmesh.storage.provider.gdrive.Provider import Provider as GdriveProvider
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.storage.provider.awsobjectstore.Provider import Provider as AwsobjectstoreProvider
from cloudmesh.DEBUG import VERBOSE
from cloudmesh.common.console import Console
import warnings
from pprint import pprint

class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):

        super(Provider, self).__init__(service=service, config=config)

        if self.kind == "local":
            self.provider = LocalProvider(service=service, config=config)
        elif self.kind == "box":
            self.provider = BoxProvider(service=service, config=config)
        elif self.kind == "gdrive":
            self.provider = GdriveProvider(service=service, config=config)
        elif self.kind == "azureblob":
            self.provider = AzureblobProvider(service=service, config=config)
        elif self.kind == "awss3":
            self.provider = AwsProvider(service=service, config=config)
        elif self.kind == "awsobjectstore":
            self.provider = AwsobjectstoreProvider(service=service, config=config)
        else:
            raise ValueError(f"Storage provider '{self.kind}' not yet supported")

    @DatabaseUpdate()
    def get(self, source=None, destination=None, recursive=False):

        VERBOSE(f"get {source} {destination} {recursive}")
        d = self.provider.get(source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    @DatabaseUpdate()
    def put(self, source=None, destination=None, recursive=False):

        service = self.service
        VERBOSE(f"put {service} {source} {destination}")
        d = self.provider.put(source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    @DatabaseUpdate()
    def createdir(self, directory=None):

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"create_dir {directory}")
        VERBOSE(directory)
        service = self.service
        d = self.provider.create_dir(service=service, directory=directory)
        return d

    @DatabaseUpdate()
    def delete(self, source=None):

        service = self.service
        VERBOSE(f"delete filename {service} {source}")
        d = self.provider.delete(service=service, source=source)
        #raise ValueError("must return a value")
        return d

    def search(self, directory=None, filename=None, recursive=False):

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"search {directory}")
        d = self.provider.search(directory=directory,
                                 filename=filename,
                                 recursive=recursive)
        return d

    @DatabaseUpdate()
    def list(self, source=None, recursive=None):

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"list {source}")
        VERBOSE(locals())
        d = self.provider.list(source=source,
                               recursive=recursive)
        return d

    def tree (self, source):

        data = self.provider.list(source=source)

        # def dict_to_tree(t, s):
        #    if not isinstance(t, dict) and not isinstance(t, list):
        #       print ("    " * s + str(t))
        #    else:
        #        for key in t:
        #            print ("    " * s + str(key))
        #            if not isinstance(t, list):
        #                dict_to_tree(t[key], s + 1)
        #
        # dict_to_tree(d, 0)

        pprint(data)
