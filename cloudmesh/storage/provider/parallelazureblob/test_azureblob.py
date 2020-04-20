from azure.storage.blob import BlockBlobService
import os
#from cloudmesh.storage.provider.azureblob.Provider import Provider
from cloudmesh.storage.provider.parallelazureblob.Provider import Provider
'''
Class
Azure:


def authenticate(self, specification):
    pass


def mkdir(self, specification):
    pass


def get(self, specification):
    pass


def put(self, specification):
    pass


def list(self, specification):
    pass


def delete(self, specification):
    pass


if __name__ == "__main__":
'''
    # provider = Azure()
    # provider._mkdir(...)

#p = Provider(service="parallelazureblob")
#from Provider import Provider
p=Provider(service="azure")
print(p.credentials)
#p.list(source='dummy.txt', dir_only=False, recursive=False)
p.create_dir(directory='newcontainer4')#works
#p.put(source='c:/users/hp/.cloudmesh/storage/test/a/a3.txt', destination='containerone', recursive=False)#works
#p.search(directory='created_dir',filename='dummy.txt',recursive=False)
#p.get(source=' containerone', destination='a1.txt', recursive=False)
#p.delete(source='blob1', recursive=False)


'''
    block_blob_service = BlockBlobService(p.credentials['account_name'],
                                          p.credentials['account_key'])
    # Create Directory/Container
    container_name = "mynewcontainer1"
    block_blob_service.create_container(container_name)
    print(' Create a container  - ' + container_name) 

    # Create blobs in the Container and put a file in the blobs

    local_path = "c:/users/hp"
    file_to_upload = "Helloworld.txt"
    blob_name1 = "myblob1"
    blob_name2 = "myblob2"
    blob_name3 = "myblob3"
    full_path_to_file = os.path.join(local_path, file_to_upload)
    block_blob_service.create_blob_from_path(container_name, blob_name1,
                                             full_path_to_file)
    block_blob_service.create_blob_from_path(container_name, blob_name2,
                                             full_path_to_file)
    block_blob_service.create_blob_from_path(container_name, blob_name3,
                                             full_path_to_file)

    # Get a file from blob and download it in the local drive

    full_path_to_file1 = os.path.join(local_path, blob_name1.replace(
        '.txt', 'myblob1.txt'))
    print("\nDownloading blob to " + full_path_to_file1)
    block_blob_service.get_blob_to_path(
        container_name, blob_name1, full_path_to_file1)

    # List all blobs in the container
    generator = block_blob_service.list_blobs(container_name)
    for blob in generator:
        print("\t" + blob.name)

    # Deleting the container
    '''
'''
    if block_blob_service.exists(container_name):
        block_blob_service.delete_container(container_name)
  
'''
