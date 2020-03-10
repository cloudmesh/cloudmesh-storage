import os
import stat
from pprint import pprint

import boto3
import botocore
from cloudmesh.abstract.StorageABC import StorageABC
from cloudmesh.common.console import Console

import platform


class Provider(StorageABC):
    kind = "parallelawss3"

    sample = "TODO: missing"

    output = {}  # "TODO: missing"

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        """
        TBD

        :param service: TBD
        :param config: TBD
        """
        # pprint(service)
        super().__init__(service=service, config=config)
        self.container_name = self.credentials['bucket']
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

    def update_dict(self, elements, kind=None):
        # this is an internal function for building dict object
        d = []
        for element in elements:
            # entry = element.__dict__
            # entry = element['objlist']
            entry = element
            entry["cm"] = {
                "kind": "storage",
                "cloud": self.cloud,
                "name": entry['fileName']
            }

            # element.properties = element.properties.__dict__
            d.append(entry)
        return d

    # function to massage file path and do some transformations
    # for different scenarios of file inputs
    def massage_path(self, file_name_path):
        massaged_path = file_name_path
        # pprint(massaged_path)

        # convert possible windows style path to unix path
        massaged_path = massaged_path.replace('\\', '/')

        # remove leading slash symbol in path
        if len(massaged_path) > 0 and massaged_path[0] == '/':
            massaged_path = massaged_path[1:]

        # expand home directory in path
        massaged_path = massaged_path.replace('~', os.path.expanduser('~'))
        # pprint(massaged_path)

        # expand possible current directory reference in path
        if massaged_path[0:2] == '.\\' or massaged_path[0:2] == './':
            massaged_path = os.path.abspath(massaged_path)

        return massaged_path

    # Function to join file name dir to get full file path
    def join_file_name_dir(self, filename, dirname):
        full_file_path = ''
        if len(self.massage_path(dirname)) > 0:
            # fullFilePath = self.massage_path(dirName) + '/' + self.massage_path(fileName)
            full_file_path = self.massage_path(
                dirname) + '/' + self.massage_path(
                filename)
        else:
            full_file_path = self.massage_path(filename)
        return full_file_path

    # Function to extract obj dict from metadata
    def extract_file_dict(self, filename, metadata):
        # print(metadata)
        info = {
            "fileName": filename,
            # "creationDate" : metadata['ResponseMetadata']['HTTPHeaders']['date'],
            "lastModificationDate":
                metadata['ResponseMetadata']['HTTPHeaders']['last-modified'],
            "contentLength":
                metadata['ResponseMetadata']['HTTPHeaders']['content-length']
        }

        return info

    def bucket_create(self, name=None):
        """
        gets the source name from the put function

        :param name: the bucket name which needs to be created

        :return: dict,Boolean

        """

        try:
            self.s3_client.create_bucket(
                ACL='private',
                Bucket=name,
            )
            print("Bucket Created:", name)
            file_content = ""
            file_path = self.massage_path(name)
            self.storage_dict['action'] = 'bucket_create'
            self.storage_dict['bucket'] = name
            dir_files_list = []
            self.container_name = name
            obj = list(self.s3_resource.Bucket(self.container_name) \
                       .objects.filter(Prefix=file_path + '/'))

            if len(obj) == 0:
                marker_object = self.s3_resource.Object(
                    self.container_name, self.directory_marker_file_name
                ).put(Body=file_content)

                # make head call to extract meta data
                # and derive obj dict
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name,
                    Key=self.directory_marker_file_name)
                dir_files_list.append(self.extract_file_dict(
                    self.massage_path(name),
                    metadata)
                )
                self.storage_dict['message'] = 'Bucket created'
            self.storage_dict['objlist'] = dir_files_list
            pprint(self.storage_dict)
            dict_obj = self.update_dict(self.storage_dict['objlist'])
            # return self.storage_dict
            return dict_obj
            return True

        except botocore.exceptions.ClientError as e:
            if e:
                message = "One or more errors occurred while creating the bucket: {}".format(
                    e)
                raise Exception(message)
                return True

    def bucket_exists(self, name=None):
        """
        gets the source from the put function

        :param name: the bucket name which needs to be checked for exists

        :return: Boolean

        """
        try:
            self.s3_client.head_bucket(Bucket=name)
            return True
            return name
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])

            if error_code == 403:
                Console.error(f"Bucket {name} is private. Access forbidden!")
                return True
            elif error_code == 404:
                Console.error(f"Bucket {name} does not exist")
                return False

    # function to create a directory the function will first check if the bucket exists or not,if the bucket doesn't exist it will create the bucket and it will create the directory specified.
    # the name of the bucket will come from YAML specifications and the directory name comes from the arguments.

    def create_dir(self, directory=None):
        """
        creates a directory

        :param directory: the name of the directory

        :return: dict

        """
        file_content = ""
        # filePath = self.joinFileNameDir(self.directory_marker_file_name, directory)
        # filePath = self.massage_path(directory) + '/' + self.directory_marker_file_name
        file_path = self.massage_path(directory)
        self.storage_dict['action'] = 'create_dir'
        self.storage_dict['directory'] = directory
        dir_files_list = []

        bucket = self.container_name
        if not self.bucket_exists(name=bucket):
            self.bucket_create(name=bucket)

        # obj = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
        obj = list(self.s3_resource.Bucket(self.container_name) \
                   .objects.filter(Prefix=file_path + '/'))

        if len(obj) == 0:
            # markerObject = self.s3_resource.Object(self.container_name, filePath).put(Body=fileContent)
            marker_object = self.s3_resource.Object(
                self.container_name, self.massage_path(
                    directory) + '/' + self.directory_marker_file_name
            ).put(Body=file_content)

            # make head call to extract meta data
            # and derive obj dict
            metadata = self.s3_client.head_object(
                Bucket=self.container_name, Key=self.massage_path(
                    directory) + '/' + self.directory_marker_file_name)
            dir_files_list.append(self.extract_file_dict(
                self.massage_path(directory) + '/',
                metadata)
            )

            # print('Directory created')
            # print(markerObject)
            self.storage_dict['message'] = 'Directory created'
        else:
            # print('Directory already present')
            self.storage_dict['message'] = 'Directory/Bucket already present'

        self.storage_dict['objlist'] = dir_files_list
        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj

        # function to list file  or directory

    def list(self, source=None, dir_only=False, recursive=False):
        """
        lists the information as dict

        :param source: the source which either can be a directory or file
        :param dir_only: Only the directory names
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source

        :return: dict

        """
        # if dir_only:
        #    raise NotImplementedError
        self.storage_dict['action'] = 'list'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        objs = list(self.s3_resource.Bucket(self.container_name).objects.all())
        pprint(objs)

        dir_files_list = []
        trimmed_source = self.massage_path(source)
        # trimmed_source = source
        pprint(trimmed_source)

        if not recursive:
            # call will not be recursive and need to look only in the specified directory
            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmed_source)):
                    pprint(obj.key)
                    file_name = obj.key
                    # obj.key.replace(self.directory_marker_file_name,
                    #                            '')
                    if file_name[-1] == '/':

                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            
                            dirFilesList.append(fileName)
                        '''
                        x = 1
                    else:
                        # Its a file
                        if len(file_name.replace(trimmed_source, '')) == 0:
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                self.extract_file_dict(file_name, metadata))

                        elif (file_name.replace(trimmed_source, '')[
                                  0] == '/' and file_name.replace(
                            trimmed_source,
                            '').count('/') == 1):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                self.extract_file_dict(file_name, metadata))

                        elif (file_name.replace(trimmed_source, '')[
                                  0] != '/' and file_name.replace(
                            trimmed_source,
                            '').count('/') == 0):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                self.extract_file_dict(file_name, metadata))

                    # print(fileName)
        else:
            # call will be recursive and need to look recursively in the specified directory as well
            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmed_source)):
                    # print(obj.key)
                    file_name = obj.key
                    # file_name = obj.key.replace(self.directory_marker_file_name,
                    #                            '')
                    if file_name[-1] == '/':
                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            dirFilesList.append(fileName)
                        '''
                        x = 1
                    else:
                        # its a file
                        # dir_files_list.append(file_name)

                        # make head call to extract meta data
                        # and derive obj dict
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=file_name)
                        dir_files_list.append(
                            self.extract_file_dict(file_name, metadata))
                    # print(fileName)
        '''
        if len(dirFilesList) == 0:
            #print("No files found in directory")
            self.storage_dict['message'] = ''
        else:
            self.storage_dict['message'] = dirFilesList
        '''

        self.storage_dict['objlist'] = dir_files_list
        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj

    # function to delete file or directory
    def delete(self, source=None, recursive=True):
        """
        deletes the source

        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source

        :return: dict

        """
        # self.storage_dict['service'] = service
        self.storage_dict['action'] = 'delete'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        trimmed_source = self.massage_path(source)

        dir_files_list = []
        file_obj = ''

        # setting recursive as True for all delete cases
        # recursive = True

        try:
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=trimmed_source)
        except botocore.exceptions.ClientError as e:
            # object not found
            x = 1

        if file_obj:
            # Its a file and can be deleted

            # make head call to extract meta data
            # and derive obj dict
            metadata = self.s3_client.head_object(
                Bucket=self.container_name, Key=trimmed_source)
            dir_files_list.append(
                self.extract_file_dict(trimmed_source, metadata))

            blob = self.s3_resource.Object(
                self.container_name,
                trimmed_source).delete()

            # print('File deleted')
            self.storage_dict['message'] = 'Source Deleted'

        else:
            # Search for a directory
            all_objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=trimmed_source))

            total_all_objs = len(all_objs)

            if total_all_objs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is True:
                for obj in all_objs:
                    # if obj.key.startswith(self.massage_path(trimmedSource)):

                    # make head call to extract meta data
                    # and derive obj dict
                    if os.path.basename(
                        obj.key) != self.directory_marker_file_name:
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=obj.key)
                        dir_files_list.append(
                            self.extract_file_dict(obj.key, metadata))
                    else:
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=obj.key)
                        dir_files_list.append(self.extract_file_dict(
                            obj.key.replace(os.path.basename(obj.key), ''),
                            metadata))

                    self.s3_resource.Object(self.container_name,
                                            obj.key).delete()
                    # dir_files_list.append(obj.key)

                self.storage_dict['message'] = 'Source Deleted'

            elif total_all_objs > 0 and recursive is False:
                # check if marker file exists in this directory
                marker_obj_list = list(
                    self.s3_resource.Bucket(
                        self.container_name).objects.filter(
                        Prefix=trimmed_source + '/' +
                               self.directory_marker_file_name)
                )
                marker_exits = False
                if len(marker_obj_list) == 1:
                    marker_exits = True

                if marker_exits is True and total_all_objs == 1:

                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name,
                        Key=trimmed_source + '/' + self.directory_marker_file_name)
                    dir_files_list.append(
                        self.extract_file_dict(trimmed_source + '/',
                                               metadata))

                    self.s3_resource.Object(
                        self.container_name,
                        trimmed_source + '/' +
                        self.directory_marker_file_name).delete()
                    self.storage_dict['message'] = 'Source Deleted'
                else:
                    self.storage_dict[
                        'message'] = 'Source has child objects. Please delete ' \
                                     'child objects first or use recursive option'

        self.storage_dict['objlist'] = dir_files_list
        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj

    # function to upload file or directory
    def put(self, source=None, destination=None, recursive=False):
        """
       puts the source on the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        # src_service, src = source.split(":", 1)
        # dest_service, dest = destination.split(":", 1)

        # check if the source an destination roots exist

        # self.storage_dict['service'] = service
        self.storage_dict['action'] = 'put'
        self.storage_dict['source'] = source  # src
        self.storage_dict['destination'] = destination  # dest
        self.storage_dict['recursive'] = recursive
        pprint(self.storage_dict)

        trimmed_source = self.massage_path(source)
        trimmed_destination = self.massage_path(destination)

        is_source_file = os.path.isfile(trimmed_source)
        is_source_dir = os.path.isdir(trimmed_source)

        files_uploaded = []

        bucket = self.container_name
        if not self.bucket_exists(name=bucket):
            self.bucket_create(name=bucket)

        if is_source_file is True:
            # print('file flow')
            # Its a file and need to be uploaded to the destination

            # check if trimmed_destination is file or a directory
            is_trimmed_destination_file = False
            dot_operator = '.'
            # print('destination base : '+ os.path.basename(trimmed_destination))
            if dot_operator in os.path.basename(trimmed_destination):
                is_trimmed_destination_file = True
                # print('dot_operator found')

            # print('is_trimmed_destination_file  :')
            # print(is_trimmed_destination_file)

            if is_trimmed_destination_file:
                blob_obj = self.s3_client.upload_file(trimmed_source,
                                                      self.container_name,
                                                      trimmed_destination)

                # make head call since file upload does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_destination)
                files_uploaded.append(
                    self.extract_file_dict(trimmed_destination, metadata))

            else:

                destination_key = ''
                if len(trimmed_destination) == 0:
                    destination_key = os.path.basename(trimmed_source)
                else:
                    destination_key = trimmed_destination + '/' + os.path.basename(
                        trimmed_source)

                blob_obj = self.s3_client.upload_file(trimmed_source,
                                                      self.container_name,
                                                      destination_key)

                # make head call since file upload does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=destination_key)
                files_uploaded.append(
                    self.extract_file_dict(destination_key, metadata))

            self.storage_dict['message'] = 'Source uploaded'
        elif is_source_dir is True:
            # Look if its a directory
            # print('dir flow')
            # files_uploaded = []
            if recursive is False:
                # get files in the directory and upload to destination dir
                files_to_upload = []
                for (dirpath, dirnames, filenames) in os.walk(trimmed_source):
                    for f in filenames:

                        if platform.system() == "Windows":
                            files_to_upload.append(
                                self.massage_path(dirpath) + '/' + f)
                        else:
                            files_to_upload.append(
                                '/' + self.massage_path(dirpath) + '/' + f)
                            # print('FILE :', os.path.join(dirpath, f))
                            # directory ,tgtfile = os.path.split(f)
                            # files_to_upload.append(tgtfile)

                for file in files_to_upload:
                    directory, tgtfile = os.path.split(file)
                    self.s3_client.upload_file(file,
                                               self.container_name,
                                               trimmed_destination + tgtfile)
                    # files_uploaded.append(trimmed_destination + '/' + file)

                    # make head call since file upload does not return
                    # obj dict to extract meta data
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name,
                        Key=trimmed_destination + tgtfile)
                    files_uploaded.append(
                        self.extract_file_dict(trimmed_destination + tgtfile,
                                               metadata))

            else:
                # get the directories with in the folder as well and upload
                files_to_upload = []
                for (dirpath, dirnames, filenames) in os.walk(trimmed_source):
                    for fileName in filenames:
                        #   print('/'+self.massage_path(dirpath)+'/'+fileName)

                        if platform.system() == "Windows":
                            files_to_upload.append(
                                self.massage_path(dirpath) + '/' + fileName)
                        else:
                            files_to_upload.append(
                                '/' + self.massage_path(
                                    dirpath) + '/' + fileName)

                for file in files_to_upload:
                    self.s3_client.upload_file(file,
                                               self.container_name,
                                               trimmed_destination + self.massage_path(
                                                   file.replace(trimmed_source,
                                                                '')))

                    '''
                    files_uploaded.append(
                    trimmed_destination + '/' + self.massage_path(
                        file.replace(trimmed_source, '')))
                    '''

                    # make head call since file upload does not return
                    # obj dict to extract meta data
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name,
                        Key=trimmed_destination + self.massage_path(
                            file.replace(trimmed_source, '')
                        )
                    )
                    files_uploaded.append(self.extract_file_dict(
                        trimmed_destination + self.massage_path(
                            file.replace(trimmed_source, '')
                        )
                        , metadata))

            # self.storage_dict['filesUploaded'] = files_uploaded
            self.storage_dict['message'] = 'Source uploaded'

        else:
            self.storage_dict['message'] = 'Source not found'

        self.storage_dict['objlist'] = files_uploaded
        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj

    # function to download file or directory
    def get(self, source=None, destination=None, recursive=False):
        """
       gets the source from the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        # self.storage_dict['service'] = service
        self.storage_dict['action'] = 'get'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmed_source = self.massage_path(source)
        trimmed_destination = self.massage_path(destination)

        file_obj = ''

        try:
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=trimmed_source)
            # print(file_obj)
        except botocore.exceptions.ClientError as e:
            # object not found
            x = 1

        files_downloaded = []

        is_target_file = os.path.isfile(trimmed_destination)
        is_target_dir = os.path.isdir(trimmed_destination)

        '''
        print('is_target_file')
        print(is_target_file)
        print('is_target_dir')
        print(is_target_dir)
        '''

        if file_obj:
            # Its a file and can be downloaded
            # print('downloading file..')
            # print(os.path.basename(trimmedSource))
            try:
                if is_target_dir:
                    '''
                    print('target is directory...')
                    print('trimmed_destination : '+ trimmed_destination)
                    print(trimmed_source)
                    '''
                    blob = self.s3_resource.Bucket(
                        self.container_name).download_file(
                        trimmed_source,
                        trimmed_destination + '/' + os.path.basename(
                            trimmed_source)
                    )
                else:
                    blob = self.s3_resource.Bucket(
                        self.container_name).download_file(
                        trimmed_source, trimmed_destination)
                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                # print('File downloaded')

                # make head call since file download does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_source)
                files_downloaded.append(
                    self.extract_file_dict(trimmed_source, metadata))

                self.storage_dict['message'] = 'Source downloaded'
            except FileNotFoundError as e:
                self.storage_dict['message'] = 'Destination not found'

        else:
            # Search for a directory
            all_objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=trimmed_source))

            total_all_objs = len(all_objs)

            # print('total_allObjs : '+str(total_allObjs))

            if total_all_objs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is False:
                # print('directory found and recursive is false')
                # files_downloaded = []
                for obj in all_objs:
                    if os.path.basename(obj.key) != \
                        self.directory_marker_file_name:
                        if self.massage_path(
                            obj.key.replace(trimmed_source, '')).count(
                            '/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    trimmed_destination + '/' + os.path.basename(
                                        obj.key))
                                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                                # print('File downloaded')

                                # make head call since file download does not return
                                # obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key, metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'

                self.storage_dict['filesDownloaded'] = files_downloaded

            elif total_all_objs > 0 and recursive is True:
                # print('directory found and recursive is True')
                files_downloaded = []
                for obj in all_objs:
                    # print(obj.key)
                    if os.path.basename(
                        obj.key) != self.directory_marker_file_name and obj.key[
                        -1] != '/':
                        if self.massage_path(
                            obj.key.replace(trimmed_source, '')).count(
                            '/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    trimmed_destination + '/' + os.path.basename(
                                        obj.key))
                                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                                # print('File downloaded')

                                # make head call since file download does not return
                                # obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key, metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'
                        else:

                            folder_path = self.massage_path(
                                obj.key.replace(trimmed_source, '').replace(
                                    os.path.basename(obj.key), '')
                            )
                            # print('folderPath  : '+folderPath)
                            try:
                                os.makedirs(
                                    trimmed_destination + '/' + folder_path,
                                    0o777)
                                # os.chmod(trimmedDestination+'/'+folderPath, stat.S_IRWXO)
                                x = 1
                            except FileExistsError as e:
                                # print('Error :')
                                # print(e)
                                os.chmod(
                                    trimmed_destination + '/' + folder_path,
                                    stat.S_IRWXO)
                                x = 1

                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    # obj.key, trimmedDestination + '/' + os.path.basename(obj.key))
                                    obj.key,
                                    trimmed_destination + '/' + folder_path + os.path.basename(
                                        obj.key))
                                # print('File downloaded')

                                # make head call since file download does not return
                                # obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key, metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'

        self.storage_dict['objlist'] = files_downloaded

        # print(self.storage_dict['message'])
        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj

    # function to search a file or directory and list its attributes
    def search(self,
               directory=None,
               filename=None,
               recursive=False):
        """
        gets the destination and copies it in source

        :param directory: the directory which either can be a directory or file
        :param filename: filename
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """

        # self.storage_dict['service'] = service
        self.storage_dict['search'] = 'search'
        self.storage_dict['directory'] = directory
        self.storage_dict['filename'] = filename
        self.storage_dict['recursive'] = recursive

        # filePath = self.joinFileNameDir(filename, directory)
        file_path = ''
        len_dir = len(self.massage_path(directory))
        if len_dir > 0:
            file_path = self.massage_path(directory) + '/' + filename
        else:
            file_path = filename

        # print('file_path : ' +file_path )

        info_list = []
        objs = []

        if (len_dir > 0) and recursive is False:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=file_path))
        elif (len_dir == 0) and recursive is False:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=file_path))
            # objs = list(self.s3_resource.Bucket(self.container_name).objects.all())
        elif (len_dir > 0) and recursive is True:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=self.massage_path(directory)))
        elif (len_dir == 0) and recursive is True:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.all())

        if len(objs) > 0:
            for obj in objs:
                # if self.splitToList(obj.key)[-1] == filename:
                if os.path.basename(obj.key) == filename:
                    # print(obj.key)
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=obj.key)
                    # print(metadata)
                    info = {
                        "fileName": obj.key,
                        # "creationDate" : metadata['ResponseMetadata']['HTTPHeaders']['date'],
                        "lastModificationDate":
                            metadata['ResponseMetadata']['HTTPHeaders'][
                                'last-modified'],
                        "contentLength":
                            metadata['ResponseMetadata']['HTTPHeaders'][
                                'content-length']
                    }
                    # pprint(info)
                    info_list.append(info)

        self.storage_dict['objlist'] = info_list

        if len(info_list) == 0:
            self.storage_dict['message'] = 'File not found'
        else:
            self.storage_dict['message'] = 'File found'

        pprint(self.storage_dict)
        dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        return dict_obj
