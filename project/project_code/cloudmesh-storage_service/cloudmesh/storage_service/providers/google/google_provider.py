
from cloudmesh.storage.StorageNewABC import StorageABC
from cloudmesh.configuration.Config import Config
#from cloudmesh.storage.provider.gdrive.Provider import Provider as GProv
from cloudmesh.storage.provider.awss3.Provider import Provider as AWS_Provider

from google.cloud import storage
import os
from pprint import pprint
from cloudmesh.common.console import Console

class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        super().__init__(service=service, config=config)
        self.config = Config()

        self.storage_credentials = self.config.credentials("storage", "gdrive")

        google_json = self.config["cloudmesh"]["storage"]["gdrive"]["default"]["service_account"]
        self.google_client = storage.Client.from_service_account_json(google_json)

        self.local_dir = self.config["cloudmesh"]["storage"]["local"]["dir"]
        self.bucket = self.config["cloudmesh"]["storage"]["gdrive"]["default"]["bucket"]



    def list(self, cloudName):
        bucket = self.google_client.bucket(self.bucket)
        keys = []
        for blob in bucket.list_blobs():
            keys.append(blob.name)
            pprint(blob.name)
        return keys


    def download_file(self, source_filename, destination_filename):
        bucket = self.google_client.get_bucket(self.bucket)
        blob = bucket.blob(source_filename)
        status = blob.download_to_filename(destination_filename)

        Console.ok(f"Blob {source_filename} downloaded to {destination_filename}.")

        return status

    def uploadfile(self, source_file, destination_file):

        bucket = self.google_client.get_bucket(self.bucket)
        blob = bucket.blob(destination_file)
        blob.upload_from_filename(source_file)
        status = "success"

        return status

    def copy(self, source=None, target=None, source_file_dir=None, target_fil_dir=None):

        if(source== "local"):
            print("Local to Google")
            source_file_dir = self.local_dir + source_file_dir
            self.uploadfile(source_file_dir, target_fil_dir)
        elif(source == "google"):
            if( target == "aws"):
                print("Google to AWS Copy")
                self.download_file(source_file_dir, target_fil_dir)
                print("File Downloaded from Google to Local")

                target = AWS_Provider(service="aws")
                config = Config(config_path="~/.cloudmesh/cloudmesh.yaml")

                local_target = self.local_dir

                sourceFile = local_target + source_file_dir
                status = target.put(sourceFile, target_fil_dir, True)

                if status is None:
                    return Console.error(f" Cannot Copy {source_file_dir} to {target_fil_dir}" )
                else:
                    Console.ok(f"File uploaded from {source} to {target}")
            elif(target == "local"):

                target_fil_dir = self.local_dir + target_fil_dir
                self.download_file(source_file_dir, target_fil_dir)
        else:
            NotImplementedError
