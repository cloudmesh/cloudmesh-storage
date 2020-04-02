import boto3

from cloudmesh.storage.StorageNewABC import StorageABC
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.provider.awss3.Provider import Provider as AWSProv
from cloudmesh.storage_service.providers.google.google_provider import Provider as Google_Provider
from pprint import pprint
from cloudmesh.common.console import Console
from pathlib import Path


class Provider(StorageABC):
    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):

        super().__init__(service=service, config=config)
        self.config = Config()
        credential = {
            'aws_access_key_id': self.credentials['access_key_id'],
            'aws_secret_access_key': self.credentials['secret_access_key'],
            'region_name': self.credentials['region']
        }
        self.s3_client = boto3.client('s3', aws_access_key_id=self.credentials['access_key_id'],
                                      aws_secret_access_key=self.credentials['secret_access_key'],
                                      region_name=self.credentials['region']
                                      )

        self.aws_provider = AWSProv(service='aws')
        self.local_dir = self.config["cloudmesh"]["storage"]["local"]["dir"]

    def list(self, sourceName):
        #cloudName = "aws"
        status = self.aws_provider.list(source=sourceName, recursive=True)
        if status is not None:
            pprint(status)
        else:
            Console.error(f"{sourceName} cannot be listed ")
        return status

    def copy(self, source=None, target=None, source_file_dir=None, target_fil_dir=None):

        print(source + target + source_file_dir + target_fil_dir)
        status = None
        if source == "local" and target == "aws":
            print(source_file_dir)
            source_path = self.getLocalPath(source_file_dir)
            target_fil_dir = target_fil_dir.replace("\\","/")
            status = self.aws_provider.put(source_path, target_fil_dir, True)
        elif source == "aws":
            if target == "google":
                target_local = self.getLocalPath(self.local_dir) + "/" +source_file_dir
                print("source_file=" + source_file_dir + " Target= " +target_local)
                status = self.aws_provider.get(source_file_dir, target_local, recursive=True)
                if status is not None:
                    google_provider = Google_Provider(service="google")
                    config = Config(config_path="~/.cloudmesh/cloudmesh.yaml")

                    #local_target = self.local_dir
                    #sourceFile = local_target + source_file_dir
                    status = google_provider.uploadfile(target_local, target_fil_dir)
                else:
                    Console.error("File cannot be downloaded from AWS")
            elif target == "local":
                target_fil_dir = self.getLocalPath(target_fil_dir)
                status = self.aws_provider.get(source_file_dir, target_fil_dir, True)

        if status is None:
            return Console.error(f"{source_file_dir} is not copied to {target_fil_dir}")
        else:
            Console.ok(f"File copied from {source} to {target}")

        return status

    def getLocalPath(self, fileOrDir):

        file_path = Path(fileOrDir).expanduser()
        print(str(file_path))
        if file_path.is_absolute():
            print("absolute")
            pprint(file_path)
            tar_dir = str(file_path)
        else:
            print("not absolute")
            # must be in local defaults
            local_path = Path(self.local_dir).expanduser()
            print(local_path)
            # tar_dir = str(local_dir.joinpath(file_path))
            tar_dir = (str(local_path) +"/"+ str(file_path)).replace("\\", "/")

            pprint(tar_dir)
        return tar_dir

    def delete(self, source):
        status = self.aws_provider.delete(source, recursive=True)
        if status is not None:
            pprint(status)
        else:
            Console.error(f"{source} cannot be deleted ")
        return status