from abc import ABCMeta

from cloudmesh.configuration.Config import Config


# noinspection PyUnusedLocal
class StorageABC(metaclass=ABCMeta):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        try:
            self.config = Config(config_path=config)

            spec = self.config["cloudmesh.storage"]
            self.credentials = spec[service]['credentials']
            self.kind = spec[service]['cm']['kind']
            self.cloud = service
            self.service = service
            self.default = spec[service]['default']
        except Exception as e:
            raise ValueError(f"storage service {service} not specified")
            print(e)

    def create_dir(self,
                   service=None,
                   directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        raise NotImplementedError
        return {}

    def list(self, service=None, source=None, recursive=False):
        """
        lists the information as dict

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def put(self, service=None, source=None, destination=None, recursive=False):
        """
        puts the source on the service

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def get(self, service=None, source=None, destination=None, recursive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def delete(self, service=None, source=None, recursive=False):
        """
        deletes the source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def search(self, service=None, directory=None, filename=None,
               recursive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def tree(self, directory=None):
        """
        Prints a visual representation of the files and directories
        :param directory:
        :type directory:
        :return:
        :rtype:
        """
        raise NotImplementedError
        return ""
