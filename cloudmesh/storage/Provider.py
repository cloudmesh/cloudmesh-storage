from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider
from cloudmesh.storage.provider.azureblob.Provider import \
    Provider as AzureblobProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.local.Provider import Provider as LocalProvider
from cloudmesh.storage.StorageNewABC import StorageABC
from cloudmesh.storage.provider.gdrive.Provider import Provider as GdriveProvider
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.storage.provider.awsobjectstore.Provider import Provider as AwsobjectstoreProvider
from cloudmesh.common.debug import VERBOSE
from pprint import pprint


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):

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
        elif self.kind in ['google']:
            from cloudmesh.google.storage.Provider import \
                Provider as GoogleStorageProvider
            self.provider = GoogleStorageProvider(service=service, config=config)
        else:
            raise ValueError(f"Storage provider '{self.kind}' not yet supported")



    @DatabaseUpdate()
    def get(self, source=None, destination=None, recursive=False):
        """
        gets the content of the source on the server to the local destination

        :param source: the source file on the server
        :type source: string
        :param destination: the destination location ion teh local machine
        :type destination: string
        :param recursive: True if the source is a directory and ned to be copied recursively
        :type recursive: boolean
        :return: cloudmesh cm dict
        :rtype: dict
        """

        VERBOSE(f"get {source} {destination} {recursive}")
        d = self.provider.get(source=source, destination=destination, recursive=recursive)
        return d

    @DatabaseUpdate()
    def put(self, source=None, destination=None, recursive=False):

        service = self.service
        VERBOSE(f"put {service} {source} {destination}")
        d = self.provider.put(source=source, destination=destination, recursive=recursive)
        return d

    @DatabaseUpdate()
    def create_dir(self, directory=None):

        VERBOSE(f"create_dir {directory}")
        VERBOSE(directory)
        service = self.service
        d = self.provider.create_dir(directory=directory)
        return d
    # commented it out as this provider is general and this bucket_create is there in create_dir implementation of AwsS3 provider.
    #@DatabaseUpdate()
    #def bucket_create(self, name=None):
    #    service = self.service
    #    d = self.provider.bucket_create(name=name)
    #    return d

    @DatabaseUpdate()
    def delete(self, source=None):
        """
        deletes the source

        :param source: The source
        :return: The dict representing the source
        """

        service = self.service
        VERBOSE(f"delete filename {service} {source}")
        d = self.provider.delete(source=source)
        # raise ValueError("must return a value")
        return d

    def search(self, directory=None, filename=None, recursive=False):

        VERBOSE(f"search {directory}")
        d = self.provider.search(directory=directory, filename=filename, recursive=recursive)
        return d

    @DatabaseUpdate()
    def list(self, source=None, dir_only=False, recursive=False):

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"list {source}")
        VERBOSE(locals())
        d = self.provider.list(source=source, dir_only=dir_only, recursive=recursive)
        return d

    def tree(self, source):

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
