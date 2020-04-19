from cloudmesh.storage.Provider import Provider
import shutil
import uuid

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider


class Provider(object):

    def __init__(self):

        self.config = Config()

    def copy(self,
             source_cloud,
             source,
             target_cloud,
             target,
             local_dir=None):

        self.provider_source = Provider(service=source_cloud)
        self.provider_target = Provider(service=target_cloud)

        if local_dir is None:
            unique = uuid.uuid4()
            self.local_dir = path_expand("~/.cloudmesh/storage/tmp/{unique}")

        print(source_cloud + target_cloud + source + target)
        status = None

        if source_cloud == "local" and target_cloud == "local":

            shutil.copy(source, target)

        else:

            #
            # first copy from source provider to local
            #

            try:
                _local = f"{self.local_dir}/{source}"
                result = self.provider_source.get(source=source,
                                                  destination=_local)
            except Exception as e:
                Console.error("Error fetching directory to local")
                print(e)
                raise SystemError
            #
            # second copy from local to target provider
            #
            try:
                result = self.provider_source.get(source=_local,
                                                  destination=target)
            except Exception as e:
                Console.error("Error fetching directory to local")
                print(e)
                raise SystemError

        return status
