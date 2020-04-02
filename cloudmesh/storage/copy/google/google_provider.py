from pathlib import Path
from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.StorageNewABC import StorageABC
# from cloudmesh.storage.provider.gdrive.Provider import Provider as GProv
from cloudmesh.storage.provider.awss3.Provider import Provider as AWS_Provider
from google.cloud import storage


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        super().__init__(service=service, config=config)
        self.config = Config()

        self.storage_credentials = self.config.credentials("storage", "gdrive")

        google_json = self.config["cloudmesh"]["storage"]["gdrive"]["default"]["service_account"]
        self.google_client = storage.Client.from_service_account_json(google_json)

        self.local_dir = self.config["cloudmesh"]["storage"]["local"]["dir"]
        self.bucket = self.config["cloudmesh"]["storage"]["gdrive"]["default"]["bucket"]



    def list(self, source=None):
        bucket = self.google_client.bucket(self.bucket)
        keys = []
        match = []
        for blob in bucket.list_blobs():

            datetimeObj = blob.time_created
            timestampStr = datetimeObj.strftime("%d-%b-%Y %H:%M:%S")
            keys.append("Name: " + blob.name + " , Created: " + timestampStr)
            #pprint(blob.name)
            if(blob.name).startswith(source):
                match.append("Name: " + blob.name + " , Created: " + timestampStr)

        if match is not None:
            pprint(f"Listing from source - {source}")
            pprint(match)
        else:
            Console.ok(f"{source} cannot be found in Google bucket{self.bucket}")
        pprint(f"Listing contents from bucket - {self.bucket}")
        pprint(keys)
        return keys


    def download_blob(self, source_filename, destination_filename):
        bucket = self.google_client.get_bucket(self.bucket)
        blob = bucket.blob(source_filename)
        blob.download_to_filename(destination_filename)
        status = "Success"
        #Console.ok(f"Blob {source_filename} downloaded to {destination_filename}.")

        return status

    def uploadfile(self, source_file, destination_file):

        bucket = self.google_client.get_bucket(self.bucket)
        blob = bucket.blob(destination_file)
        blob.upload_from_filename(source_file)
        result = "success"

        return result

    def copy(self, source=None, target=None, source_file_dir=None, target_fil_dir=None):
        print((source_file_dir,target_fil_dir))
        status = None
        if(source == "local"):
            print("Copying file from Local to Google")
            source_path = self.getLocalPath(source_file_dir)
            target_fil_dir = target_fil_dir.replace("\\", "/")
            status = self.uploadfile(source_path, target_fil_dir)
            Console.ok(f"File copied from {source_file_dir} to {target_fil_dir}")
        elif(source == "google"):
            if( target == "aws"):
                pprint(f"Copying from Google {source_file_dir} to AWS {target_fil_dir}")
                target_local = self.getLocalPath(self.local_dir) + "/" + source_file_dir
                self.download_blob(source_file_dir, target_local)

                target = AWS_Provider(service="aws")
                config = Config(config_path="~/.cloudmesh/cloudmesh.yaml")

                status = target.put(target_local, target_fil_dir, True)

                if status is None:
                    return Console.error(f" Cannot Copy {source_file_dir} to {target_fil_dir}" )
                else:
                    Console.ok(f"File copied from {source_file_dir} to {target_fil_dir}")
            elif(target == "local"):
                #To fix bucket, file
                target_fil_dir = self.getLocalPath(target_fil_dir)
                status = self.download_blob(source_file_dir, target_fil_dir)
                Console.ok(f"File copied from {source_file_dir} to {target_fil_dir}")
        else:
            NotImplementedError

        return status

    def getLocalPath(self, fileOrDir):

        file_path = Path(fileOrDir).expanduser()
        if file_path.is_absolute():
            tar_dir = str(file_path)
        else:
            local_path = Path(self.local_dir).expanduser()
            tar_dir = (str(local_path) +"/"+ str(file_path)).replace("\\", "/")
        return tar_dir

    def delete(self, source=None):
        bucket = self.google_client.bucket(self.bucket)
        blob = bucket.blob(source)
        blob.delete()
        Console.ok(f"{source} has been deleted from Google - {self.bucket}")
        keys = []
        for blob in bucket.list_blobs():
            keys.append(blob.name)
            pprint(blob.name)
        return keys
