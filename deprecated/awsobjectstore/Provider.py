import boto3
from botocore.exceptions import ClientError
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.storage.StorageABC import StorageABC


# from libmagic import magic
#
# BUG: des not follow named arguments in abc class
#
class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        super().__init__(service=service, config=config)
        # self.container_name = self.credentials['container']

        credential = {
            'aws_access_key_id': self.credentials['access_key_id'],
            'aws_secret_access_key': self.credentials['secret_access_key'],
            'region_name': self.credentials['region']
        }

        # TODO: use **credentials in the next calls

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.credentials['access_key_id'],
            aws_secret_access_key=self.credentials['secret_access_key'],
            region_name=self.credentials['region']
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.credentials['access_key_id'],
            aws_secret_access_key=self.credentials['secret_access_key'],
            region_name=self.credentials['region']
        )
        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    def get(self, bucket_name, object_name):
        """Retrieve an object from an Amazon S3 bucket

        :param bucket_name: string
        :param object_name: string
        :return: botocore.response.StreamingBody object. If error, return None.
        """

        # Retrieve the object
        # s3 = boto3.client('s3')
        try:
            response = self.s3_client.get_object(Bucket=bucket_name,
                                                 Key=object_name)
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            VERBOSE(e)
            return None
        # Return an open StreamingBody object
        return response['Body']

    def put(self, dest_bucket_name, dest_object_name, src_data):
        """Add an object to an Amazon S3 bucket
        The src_data argument must be of type bytes or a string that references
        a file specification.

        :param dest_bucket_name: string
        :param dest_object_name: string
        :param src_data: bytes of data or string reference to file spec
        :return: True if src_data was added to dest_bucket/dest_object,
                 otherwise
        False
        """

        # Construct Body= parameter
        if isinstance(src_data, bytes):
            object_data = src_data
        elif isinstance(src_data, str):
            try:
                object_data = open(src_data, 'rb')
                # possible FileNotFoundError/IOError exception
            except Exception as e:
                VERBOSE(e)
                return False
        else:
            kind = type(src_data)
            Console.error(
                f"Type of {kind} for the argument 'src_data' is not supported.")
            return False

        # Put the object
        # s3 = boto3.client('s3')
        try:
            self.s3_client.put_object(Bucket=dest_bucket_name,
                                      Key=dest_object_name,
                                      Body=object_data)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest
            # error == (dest bucket/obj == src bucket/obj)
            VERBOSE(e)
            return False
        finally:
            if isinstance(src_data, str):
                object_data.close()
        return True
        # must return dict

    def copy(self, src_bucket_name, src_object_name,
             dest_bucket_name, dest_object_name=None):
        """Copy an Amazon S3 bucket object

        :param src_bucket_name: string
        :param src_object_name: string
        :param dest_bucket_name: string. Must already exist.
        :param dest_object_name: string. If dest bucket/object exists, it is
                                         overwritten. Default: src_object_name
        :return: True if object was copied, otherwise False
        """

        # Construct source bucket/object parameter
        copy_source = {'Bucket': src_bucket_name, 'Key': src_object_name}
        if dest_object_name is None:
            dest_object_name = src_object_name

        # Copy the object
        # s3 = boto3.client('s3')
        try:
            self.s3_client.copy_object(CopySource=copy_source,
                                       Bucket=dest_bucket_name,
                                       Key=dest_object_name)
        except ClientError as e:
            VERBOSE(e)
            return False
        return True

    def list(self, bucket_name):
        """List the objects in an Amazon S3 bucket
        :param bucket_name: string
        :return: List of bucket objects. If error, return None.
        """

        # Retrieve the list of bucket objects
        # s3 = boto3.client('s3')
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            VERBOSE(e)
            return None
        return response['Contents']

    def delete(self, bucket_name, object_names):
        """Delete multiple objects from an Amazon S3 bucket
        :param bucket_name: string
        :param object_names: list of strings
        :return: True if the referenced objects were deleted, otherwise False
        """

        # Convert list of object names to appropriate data format
        objlist = [{'Key': obj} for obj in object_names]

        # Delete the objects
        # s3 = boto3.client('s3')
        try:
            self.s3_client.delete_objects(Bucket=bucket_name,
                                          Delete={'Objects': objlist})
        except ClientError as e:
            VERBOSE(e)
            return False
        return True
