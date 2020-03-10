from cloudmesh.abstract.StorageABC import StorageABC
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.debug import VERBOSE
from pprint import pprint
from pathlib import Path
from cloudmesh.common.console import Console


class Provider(StorageABC):

    @staticmethod
    def get_kind():
        kind = ["local",
                "box",
                "gdrive",
                "azureblob",
                "awss3",
                "parallelawss3",
                "google",
                "oracle"]
        return kind


    @staticmethod
    def get_provider(kind):
        P = None
        if kind == "local":
            from cloudmesh.storage.provider.local.Provider import Provider as P
        elif kind == "box":
            from cloudmesh.storage.provider.box.Provider import Provider as P
        elif kind == "gdrive":
            from cloudmesh.storage.provider.gdrive.Provider import Provider as P
        elif kind == "azureblob":
            from cloudmesh.storage.provider.azureblob.Provider import \
                Provider as P
        elif kind == "awss3":
            from cloudmesh.storage.provider.awss3.Provider import Provider as P
        elif kind == "parallelawss3":
            from cloudmesh.storage.provider.awss3.Provider import Provider as P
        elif kind in ['google']:
            from cloudmesh.google.storage.Provider import Provider as P
        elif kind in ['oracle']:
            from cloudmesh.oracle.storage.Provider import Provider as P
        else:
            raise ValueError(
                f"Storage provider '{kind}' not supported")
        return P

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):

        super(Provider, self).__init__(service=service, config=config)
        P = Provider.get_provider(self.kind)
        self.provider = P(service=service, config=config)
        if self.provider is None:
            raise ValueError(
                f"Storage provider '{self.service}'"
                f"' not yet supported")

    @DatabaseUpdate()
    def get(self, source=None, destination=None, recursive=False):
        """
        gets the content of the source on the server to the local destination

        :param source: the source file on the server
        :type source: string
        :param destination: the destination location ion teh local machine
        :type destination: string
        :param recursive: True if the source is a directory
                          and ned to be copied recursively
        :type recursive: boolean
        :return: cloudmesh cm dict
        :rtype: dict
        """

        d = self.provider.get(source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    @DatabaseUpdate()
    def put(self, source=None, destination=None, recursive=False):

        service = self.service
        d = self.provider.put(source=source, destination=destination,
                              recursive=recursive)
        return d

    @DatabaseUpdate()
    def create_dir(self, directory=None):

        service = self.service
        d = self.provider.create_dir(directory=directory)
        return d

    @DatabaseUpdate()
    def delete(self, source=None):
        """
        deletes the source

        :param source: The source
        :return: The dict representing the source
        """

        service = self.service
        d = self.provider.delete(source=source)
        # raise ValueError("must return a value")
        return d

    def search(self, directory=None, filename=None, recursive=False):

        d = self.provider.search(directory=directory, filename=filename,
                                 recursive=recursive)
        return d

    @DatabaseUpdate()
    def list(self, source=None, dir_only=False, recursive=False):

        d = self.provider.list(source=source, dir_only=dir_only,
                               recursive=recursive)
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

    @staticmethod
    def get_source_provider(source_kind, source, config):
        # VERBOSE(source_kind)
        if source_kind == "azureblob":
            from cloudmesh.storage.provider.azureblob.Provider import \
                Provider as AzureblobProvider
            source_provider = AzureblobProvider(service=source,
                                                config=config)
        elif source_kind == "awss3":
            from cloudmesh.storage.provider.awss3.Provider import \
                Provider as AwsProvider
            source_provider = AwsProvider(service=source, config=config)
        elif source_kind == "oracle":
            from cloudmesh.oracle.storage.Provider import \
                Provider as OracleStorageProvider
            source_provider = OracleStorageProvider(service=source,
                                                    config=config)
        elif source_kind == "google":
            from cloudmesh.google.storage.Provider import \
                Provider as GoogleStorageProvider
            source_provider = GoogleStorageProvider(service=source,
                                                    config=config)
        else:
            return Console.error(f"Provider for {source_kind} is not "
                                 f"yet implemented.")

        return source_provider

    @DatabaseUpdate()
    def copy(self, source=None, destination=None, recursive=False):
        """
        Copies object(s) from source to destination

        :param source: "awss3:source.txt" the source is combination of
                        source CSP name and source object name which either
                        can be a directory or file
        :param destination: "azure:target.txt" the destination is
                            combination of destination CSP and destination
                            object name which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        # Fetch CSP names and object names
        if source:
            source, source_obj = source.split(':')
        else:
            source, source_obj = None, None

        if destination:
            target, target_obj = destination.split(':')
        else:
            target, target_obj = None, None

        source_obj.replace(":", "")

        # oracle provider expects a target name
        if target_obj is None or \
            len(target_obj.strip()) == 0:
            # print("DEBUG:", Path(source_obj).parts)
            target_obj = Path(source_obj).parts[-1]

        source_obj = str(Path(source_obj).expanduser())
        target_obj = str(Path(target_obj).expanduser())

        print("DEBUG Provider: values= ", source, source_obj, target,
              target_obj)

        if source == "local":
            print(f"CALL PUT METHOD OF {self.kind} PROVIDER.")
            result = self.provider.put(source=source_obj,
                                       destination=target_obj,
                                       recursive=recursive)
            return result
        elif target == "local":
            print(f"CALL GET METHOD OF {self.kind} PROVIDER.")
            result = self.provider.get(source=source_obj,
                                       destination=target_obj,
                                       recursive=recursive)
            return result
        else:
            # VERBOSE(f"Copy from {source} to {destination}.")
            target_kind = self.kind
            target_provider = self.provider
            config = "~/.cloudmesh/cloudmesh.yaml"

            if source:
                super().__init__(service=source, config=config)
                source_kind = self.kind
                source_provider = self.get_source_provider(source_kind,
                                                           source, config)

            # get local storage directory
            super().__init__(service="local", config=config)
            local_storage = self.config[
                "cloudmesh.storage.local.default.directory"]

            local_target_obj = str(Path(local_storage).expanduser())
            source_obj = str(Path(source_obj).expanduser())

            try:
                result = source_provider.get(source=source_obj,
                                             destination=local_target_obj,
                                             recursive=recursive)
                if result and len(result) == 0:
                    return Console.error(f"{source_obj} could not be found "
                                         f"in {source} CSP. Please check.")
                Console.ok(f"Fetched {source_obj} from {source} CSP")
            except Exception as e:
                return Console.error(f"Error while fetching {source_obj} from "
                                     f"{source} CSP. Please check. {e}")
            else:
                source_obj = str(Path(local_target_obj) / source_obj)

                try:
                    result = target_provider.put(source=source_obj,
                                                 destination=target_obj,
                                                 recursive=recursive)

                    if result is None:
                        return Console.error(f"{source_obj} couldn't be copied"
                                             f" to {target} CSP.")
                    Console.ok(f"Copied {source_obj} to {target} CSP")
                    return result
                except Exception as e:
                    return Console.error(f"Error while copying {source_obj} to "
                                         f"{target} CSP. Please check,{e}")
                finally:
                    Console.info("\nRemoving local intermediate file.")
                    from cloudmesh.storage.provider.local.Provider import \
                        Provider as LocalProvider
                    local_provider = LocalProvider(service="local",
                                                   config=config)
                    try:
                        local_provider.delete(source_obj, recursive=recursive)
                    except Exception as e:
                        Console.error(f"{source_obj} could not be deleted from "
                                      f"local storage.")
