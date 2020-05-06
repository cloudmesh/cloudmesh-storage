import shutil
import uuid
import os

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider as P


class Provider(object):

    def __init__(self):

        self.config = Config()

    def copy(self,
             source_cloud,
             source,
             target_cloud,
             target,
             local_dir=None):

        self.provider_source = P(service=source_cloud)
        self.provider_target = P(service=target_cloud)
        self.provider_local =  P(service="local")

        if local_dir is None:
            unique = uuid.uuid4()
            self.provider_local.create_dir(directory=path_expand(f"~/.cloudmesh/storage/tmp/{unique}"))
            self.local_dir = path_expand(f"~/.cloudmesh/storage/tmp/{unique}")
#            print(self.local_dir)

        status = None

        if source_cloud == "local" and target_cloud == "local":

            shutil.copy(source, target)

        else:

            #
            # first copy from source provider to local
            #

            try:
                _local = f'{self.local_dir}/{source}'
                _local = _local.replace("\\","/")

                self.provider_source.get(source=source, destination=_local, recursive=True)
                if (source_cloud in "aws"):
                    status = self.provider_source.run()
                status = "Download Successful"

            except Exception as e:
                Console.error(f"Error fetching from  {source_cloud}:{source} to local")
                raise SystemError

            #
            # second copy from local to target provider
            #
            if status is not None:
                try:

                    result = self.provider_target.put(source=_local, destination=target)
                    if (target_cloud in "aws"):
                        status = self.provider_target.run()
                    status = "Success"

                except Exception as e:
                    Console.error(f"Error uploading from local to {target_cloud}:{target}")
                    raise SystemError

        return status
