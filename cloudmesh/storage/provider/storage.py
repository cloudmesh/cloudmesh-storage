from cloudmesh.common.console import Console
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.provider.awss3 import Provider as AwsStorageProvider
from cloudmesh.storage.provider.azureblob import \
    Provider as AzureblobStorageProvider
from cloudmesh.storage.provider.box import Provider as BoxStorageProvider
from cloudmesh.storage.provider.gdrive import Provider as GdriveStorageProvider
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

class Provider(object):

    def __init__(self, service=None, config="~/.cloudmesh/.cloudmesh4.yaml"):

        super(Provider, self).__init__(service=service, config=config)

        self.config = Config()
        self.kind = config["cloudmesh"]["storage"][service]["cm"]["kind"]
        self.cloud = service
        self.service = service

        Console.msg("FOUND Kind", self.kind)

        if self.kind in ["awsS3"]:
            self.p = AwsStorageProvider(service=service,
                                        config=config)
        elif self.kind in ["box"]:
            self.p = BoxStorageProvider(service=service,
                                        config=config)
        elif self.kind in ["gdrive"]:
            self.p = GdriveStorageProvider(service=service,
                                           config=config)
        elif self.kind in ["azureblob"]:
            self.p = AzureblobStorageProvider(service=service,
                                              config=config)
        else:
            raise NotImplementedError

    @DatabaseUpdate()
    def create_dir(self, service=None, directory=None):
        """
        creates a directory
        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        return self.p.create_dir()

    @DatabaseUpdate()
    def list(self, service=None, source=None, recursive=False):
        """
        lists the information as dict
        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self.p.list()

    @DatabaseUpdate()
    def put(self, service=None, source=None, destination=None, recusrive=False):
        """
        puts the source on the service
        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self.p.put()

    @DatabaseUpdate()
    def get(self, service=None, source=None, destination=None, recusrive=False):
        """
        gets the destination and copies it in source
        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self.p.get()

    @DatabaseUpdate()
    def delete(self, service=None, source=None, recusrive=False):
        """
        deletes the source
        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self.p.delete()

    def search(self, service=None, directory=None, filename=None,
               recusrive=False):
        """
        gets the destination and copies it in source
        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self.p.search()
