import cloudmesh.storage.provider.parellelazureblob.Provider as Provider
from azure.storage.blob import BlockBlobService
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobClient
from azure.storage.blob import ContainerClient
import os
import uuid
from azure.storage.blob import BlobServiceClient
from cloudmesh.storage.provider.parellelazureblob.Provider import Provider
p=Provider(service="azure")
#from Provider import Provider
#p=Provider(service="azure", config="c:/users/hp/.cloudmesh/cloudmesh.yaml")
print(p.credentials)
#p.list(source='containerone', dir_only=False, recursive=False)


block_blob_service = BlockBlobService(p.credentials['account_name'], p.credentials['account_key'])
#Create Directory/Container
container_name = "mynewcontainer1"
block_blob_service.create_container(container_name)
print(' Create a container  - ' + container_name)

#Create blobs in the Container and put a file in the blobs

local_path = "c:/users/hp"
file_to_upload = "Helloworld.txt"
blob_name1 = "myblob1"
blob_name2 = "myblob2"
blob_name3 = "myblob3"
full_path_to_file = os.path.join(local_path, file_to_upload)
block_blob_service.create_blob_from_path(container_name, blob_name1, full_path_to_file)
block_blob_service.create_blob_from_path(container_name, blob_name2, full_path_to_file)
block_blob_service.create_blob_from_path(container_name, blob_name3, full_path_to_file)

#Get a file from blob and download it in the local drive

full_path_to_file1 = os.path.join(local_path, blob_name1.replace(
   '.txt', 'myblob1.txt'))
print("\nDownloading blob to " + full_path_to_file1)
block_blob_service.get_blob_to_path(
    container_name, blob_name1, full_path_to_file1)

# List all blobs in the container
generator = block_blob_service.list_blobs(container_name)
for blob in generator:
    print("\t" + blob.name)

 #Deleting the container
'''
if block_blob_service.exists(container_name):
    block_blob_service.delete_container(container_name)
'''
