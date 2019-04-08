import os
from pathlib import Path

from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.storage.StorageABC import StorageABC
from cloudmesh.DEBUG import VERBOSE
import shutil
from os import stat
from pwd import getpwuid

from grp import getgrgid

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

        self.credentials["directory"] = path_expand(self.credentials["directory"])

    def _filename(self, filename):
        return Path(self.credentials["directory"]) / filename

    def _dirname(self, dirname):
        if dirname == "/":
            dirname = ""
        location = Path(self.credentials["directory"]) / dirname
        return location

    def identifier(self, dirname, filename):
        stat_info = os.stat(filename)
        uid = stat_info.st_uid
        gid = stat_info.st_gid

        identity = {
            "cm":
                {"modified": "today",
                 "created": "today",
                 "location": str(Path(dirname) / filename),
                 "directory": dirname,
                 "filename": filename,
                 "isfile": os.path.isfile(filename),
                 "isdir": os.path.isdir(filename),
                 "name": os.path.basename(filename),
                 "size": "TBD",
                 "service": self.service
                 },
            "size": os.path.getsize(filename),
            "name": filename,
            "ownwer": getpwuid(uid)[0],
            "group": getgrgid(gid)[0]
        }
        return identity

    def create_file(self, location, content):
        self.create_dir(location)
        writefile(location, content)

    def create_dir(self,
                   service=None,
                   directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """

        d = Path(os.path.dirname(path_expand(directory)))
        d.mkdir(parents=True, exist_ok=True)
        identity = self.identifier(directory, None)
        return identity

    def list(self, source=None, recursive=False):
        """
        lists the information as dict

        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        location = self._dirname(source)
        VERBOSE(location)
        if recursive:
            files = location.glob("**/*")
        else:
            files = location.glob("*")
        result = []
        for file in files:
            entry = self.identifier(source, str(file))
            result.append(entry)
        return result

    def put(self, source=None, service=None, destination=None, recusrive=False):
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

        files = self.list()
        if recusrive:
            raise NotImplementedError

        src = path_expand(source)
        dest = path_expand(destination)
        shutil.copy2(src, dest)

        return []

    def get(self, source=None, service=None, destination=None, recusrive=False):
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

    def delete(self, source=None, recusrive=False):
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

    def search(self,
               directory=None,
               filename=None,
               recursive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """


        VERBOSE(locals())
        files = self.list(source=directory, recursive=recursive)
        VERBOSE(files)
        result = []
        for entry in files:
            if entry["cm"]["name"] == filename:
                result.append(entry)
        return result
