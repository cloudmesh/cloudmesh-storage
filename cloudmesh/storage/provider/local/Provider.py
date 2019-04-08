import os
from glob import glob
from pathlib import Path

from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.storage.StorageABC import StorageABC
from cloudmesh.terminal.Terminal import VERBOSE


class Provider(StorageABC):
    """

    cloudmesh:
      a:
        cm:
          active: False
          heading: Local A
          host: localhost
          label: local_a
          kind: local
          version: 1.0
        default:
          directory: .
        credentials:
          directory: ~/.cloudmesh/storage/a

    default location is credentials.directory / default.directory
    """

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(service=service, config=config)

    def _create_dir(self, location):
        d = Path(os.path.dirname(path_expand(location)))
        d.mkdir(parents=True, exist_ok=True)

    def _create_file(self, location, content):
        self._create_dir(location)
        writefile(location, content)

    def _filename(self, filename):
        return Path(self.credentials["directory"]) / filename

    def _dirname(self, dirname):
        return Path(self.credentials["directory"]) / dirname

    def identifier(self, dirname, filename):
        identity = {
            "cm":
                {"modified": "today",
                 "created": "today",
                 "name": Path(dirname) / filename,
                 "directory": dirname,
                 "filename": filename,
                 "size": "TBD",
                 "service": self.service
                 }
        }
        return identity

    def create_dir(self,
                   service=None,
                   directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        self.create_dir(directory)
        identity = self.identifier(directory, None)
        return identity

    def list(self, service=None, source=None, recursive=False):
        """
        lists the information as dict

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """

        location = self._dirname(source) / "*"
        files = glob(location)
        VERBOSE.print(files)
        result = []
        for file in files:
            result.append(self.identifier(source, file))
        return result

    def put(self, service=None, source=None, destination=None, recusrive=False):
        """
        puts the source on the service

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def get(self, service=None, source=None, destination=None, recusrive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

    def delete(self, service=None, source=None, recusrive=False):
        """
        deletes the source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        return []

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
        raise NotImplementedError
        return []
