import os
import platform
import stat
import textwrap
import uuid
from multiprocessing import Pool
from pprint import pprint

import boto3
import botocore
import oyaml as yaml
from cloudmesh.abstract.StorageABC import StorageABC
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.console import Console
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Provider(StorageABC):
    kind = "parallelawss3"

    sample = textwrap.dedent(
        """
        cloudmesh:
          storage:
            {name}:
              cm:
                active: true
                heading: homedir
                host: aws.com
                label: home-dir
                kind: parallelawss3
                version: TBD
                service: storage
              default:
                directory: TBD
              credentials:
                name: {username}
                bucket: {container_name}
                container: TBD
                access_key_id: {aws_access_key_id}
                secret_access_key: {aws_secret_access_key}
                region: {region_name}
            """
    )

    status = [
        'completed',
        'waiting',
        'inprogress',
        'canceled'
    ]

    output = {}  # "TODO: missing"

    def __init__(self,
                 service=None,
                 config="~/.cloudmesh/cloudmesh.yaml",
                 parallelism=4):
        """
        :param service: service name
        :param config:
        """
        super().__init__(service=service, config=config)
        self.parallelism = parallelism
        self.name = service
        self.collection = f"storage-queue-{service}"
        self.number = 0
        self.container_name = self.credentials['bucket']

        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    @DatabaseUpdate()
    def update_dict(self, elements, kind=None):
        # this is an internal function for building dict object
        d = []
        for element in elements:
            entry = element
            d.append(entry)
        return d

    # function to create a directory the function will
    # first check if the bucket  exists or not,
    # if the bucket doesn't exist it will create the bucket
    # and it will create the directory specified.
    # the name of the bucket will come from YAML specifications and the
    # directory name comes from the arguments.
    def mkdir_run(self, specification):
        #     cm:
        #     number: {self.number}
        #     kind: storage
        #     id: {uuid_str}
        #     cloud: {self.name}
        #     name: {path}
        #     collection: {self.collection}
        #     created: {date}
        #
        # action: mkdir
        # path: {path}
        # status: waiting
        directory = specification['path']
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
        file_content = ""
        file_path = self.massage_path(directory)
        dir_files_list = []

        bucket = self.container_name
        if not self.bucket_exists(name=bucket):
            self.bucket_create(name=bucket)

        obj = list(self.s3_resource.Bucket(self.container_name)
                   .objects.filter(Prefix=file_path + '/'))

        if len(obj) == 0:
            self.s3_resource.Object(
                self.container_name, self.massage_path(
                    directory) + '/' + self.directory_marker_file_name
            ).put(Body=file_content)

            # make head call to extract meta data
            # and derive obj dict
            metadata = self.s3_client.head_object(
                Bucket=self.container_name, Key=self.massage_path(
                    directory) + '/' + self.directory_marker_file_name)
            dir_files_list.append(self.extract_file_dict(
                self.massage_path(directory) + '/', metadata)
            )
        else:
            print('Directory already present')

        specification['status'] = 'completed'
        return specification

        # function to list file  or directory

    def list_run(self, specification):
        """
        lists the information as dict
        :return: dict

        """
        # if dir_only:
        #    raise NotImplementedError
        source = specification['path']
        recursive = True
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
        objs = list(self.s3_resource.Bucket(self.container_name).objects.all())

        dir_files_list = []
        trimmed_source = self.massage_path(source)
        # trimmed_source = source
        pprint(trimmed_source)

        if not recursive:
            # call will not be recursive and need to look
            # only in the specified directory
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

                        elif (file_name.replace(trimmed_source, '')[0] == '/'
                              and 1 == file_name.replace(trimmed_source, '')
                                  .count('/')):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                self.extract_file_dict(file_name, metadata))

                        elif (file_name.replace(trimmed_source, '')[0] != '/'
                              and 0 == file_name.replace(trimmed_source, '').
                                  count('/')):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                self.extract_file_dict(file_name, metadata))

        else:
            # call will be recursive and need to
            # look recursively in the specified directory as well
            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmed_source)):
                    file_name = obj.key
                    if file_name[-1] == '/':
                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            dirFilesList.append(fileName)
                        '''
                        print()
                    else:
                        # its a file
                        # dir_files_list.append(file_name)

                        # make head call to extract meta data
                        # and derive obj dict
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=file_name)
                        dir_files_list.append(
                            self.extract_file_dict(file_name, metadata))
        '''
        if len(dirFilesList) == 0:
            #print("No files found in directory")
            self.storage_dict['message'] = ''
        else:
            self.storage_dict['message'] = dirFilesList
        '''

        pprint(self.storage_dict)
        specification['status'] = 'completed'
        return specification

        # function to delete file or directory

    def delete_run(self, specificatioin):
        """
        deletes the source

        :param specificatioin:

        :return: dict

        """
        source = specificatioin['source']['path']
        recursive = specificatioin['recursive']

        trimmed_source = self.massage_path(source)

        dir_files_list = []
        file_obj = ''

        # setting recursive as True for all delete cases
        # recursive = True

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
        try:
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=trimmed_source)
        except botocore.exceptions.ClientError as e:
            # object not found
            print(e)

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

        else:
            # Search for a directory
            all_objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=trimmed_source))

            total_all_objs = len(all_objs)

            if total_all_objs == 0:
                print()
                # self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is True:
                for obj in all_objs:
                    # if obj.key.startswith(self.massage_path(trimmedSource)):

                    # make head call to extract meta data
                    # and derive obj dict
                    if self.directory_marker_file_name != \
                        os.path.basename(obj.key):
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

                # self.storage_dict['message'] = 'Source Deleted'

            elif total_all_objs > 0 and recursive is False:
                # check if marker file exists in this directory
                marker_obj_list = list(
                    self.s3_resource.Bucket(self.container_name).objects.filter(
                        Prefix=trimmed_source + '/' +
                               self.directory_marker_file_name))
                marker_exits = False
                if len(marker_obj_list) == 1:
                    marker_exits = True

                if marker_exits is True and total_all_objs == 1:

                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name,
                        Key=trimmed_source + '/' +
                            self.directory_marker_file_name)

                    dir_files_list.append(
                        self.extract_file_dict(trimmed_source + '/',
                                               metadata))

                    self.s3_resource.Object(
                        self.container_name,
                        trimmed_source + '/' +
                        self.directory_marker_file_name).delete()
                    # self.storage_dict['message'] = 'Source Deleted'
                else:
                    print()
                    # self.storage_dict[
                    # 'message'] = 'Source has child objects. Please delete ' \
                    # 'child objects first or use recursive option'

        # self.storage_dict['objlist'] = dir_files_list
        # pprint(self.storage_dict)
        # dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        # return dict_obj
        specificatioin['status'] = 'completed'
        return specificatioin

        # function to download file or directory
    def get_run(self, specficiation):
        """
        gets the source from the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be directory/file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """

        source = specficiation['source']
        destination = specficiation['destination']
        recursive = specficiation['recursive']
        trimmed_source = self.massage_path(source)
        trimmed_destination = self.massage_path(destination)

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

        file_obj = ''

        try:
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=trimmed_source)
        except botocore.exceptions.ClientError as e:
            # object not found
            print(e)
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

                # make head call since file download does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_source)
                files_downloaded.append(
                    self.extract_file_dict(trimmed_source, metadata))

                self.storage_dict['message'] = 'Source downloaded'
            except FileNotFoundError as e:
                self.storage_dict['message'] = 'Destination not found'
                print(e)

        else:
            # Search for a directory
            all_objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=trimmed_source))

            total_all_objs = len(all_objs)

            if total_all_objs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is False:
                for obj in all_objs:
                    if os.path.basename(obj.key) != \
                        self.directory_marker_file_name:
                        if self.massage_path(
                            obj.key.replace(trimmed_source, '')). \
                            count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    trimmed_destination + '/' +
                                    os.path.basename(obj.key))

                                # make head call since file download does not
                                # return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key,
                                                           metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'
                                print(e)


            elif total_all_objs > 0 and recursive is True:
                files_downloaded = []
                for obj in all_objs:
                    if os.path.basename(obj.key) != \
                        self.directory_marker_file_name \
                        and obj.key[-1] != '/':
                        if self.massage_path(
                            obj.key.replace(trimmed_source, '')) \
                            .count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    trimmed_destination + '/'
                                    + os.path.basename(obj.key))

                                # make head call since file download does
                                # not return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key,
                                                           metadata))

                            except FileNotFoundError as e:
                                print(e)
                        else:

                            folder_path = self.massage_path(
                                obj.key.replace(trimmed_source, '').replace(
                                    os.path.basename(obj.key), '')
                            )
                            try:
                                os.makedirs(
                                    trimmed_destination + '/' + folder_path,
                                    0o777)
                                print()
                            except FileExistsError as e:
                                os.chmod(
                                    trimmed_destination + '/' + folder_path,
                                    stat.S_IRWXO)
                                print(e)

                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    # obj.key, trimmedDestination + '/'
                                    # + os.path.basename(obj.key))
                                    obj.key,
                                    trimmed_destination + '/' + folder_path
                                    + os.path.basename(obj.key))

                                # make head call since file download
                                # does not return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    self.extract_file_dict(obj.key,
                                                           metadata))

                            except FileNotFoundError as e:
                                print(e)

        specficiation['status'] = 'completed'

        return specficiation

        # function to upload file or directory

    def put_run(self, specification):
        """
       puts the source on the service
        :return: dict

        """

        source = specification['source']
        destination = specification['destination']
        recursive = specification['recursive']
        # src_service, src = source.split(":", 1)
        # dest_service, dest = destination.split(":", 1)

        # check if the source an destination roots exist

        # self.storage_dict['service'] = service
        # self.storage_dict['action'] = 'put'
        # self.storage_dict['source'] = source  # src
        # self.storage_dict['destination'] = destination  # dest
        # self.storage_dict['recursive'] = recursive
        # pprint(self.storage_dict)

        trimmed_source = self.massage_path(source)
        trimmed_destination = self.massage_path(destination)

        is_source_file = os.path.isfile(trimmed_source)
        is_source_dir = os.path.isdir(trimmed_source)

        files_uploaded = []

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
        bucket = self.container_name
        if not self.bucket_exists(name=bucket):
            self.bucket_create(name=bucket)

        if is_source_file is True:
            # Its a file and need to be uploaded to the destination

            # check if trimmed_destination is file or a directory
            is_trimmed_destination_file = False
            dot_operator = '.'
            if dot_operator in os.path.basename(trimmed_destination):
                is_trimmed_destination_file = True

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

                if len(trimmed_destination) == 0:
                    destination_key = os.path.basename(trimmed_source)
                else:
                    destination_key = trimmed_destination + '/' \
                                      + os.path.basename(trimmed_source)

                blob_obj = self.s3_client.upload_file(trimmed_source,
                                                      self.container_name,
                                                      destination_key)

                # make head call since file upload does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=destination_key)
                files_uploaded.append(
                    self.extract_file_dict(destination_key, metadata))

            # self.storage_dict['message'] = 'Source uploaded'
        elif is_source_dir is True:
            # Look if its a directory
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

                for file in files_to_upload:
                    directory, tgtfile = os.path.split(file)
                    self.s3_client.upload_file(file,
                                               self.container_name,
                                               trimmed_destination + tgtfile)

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
                                               trimmed_destination +
                                               self.massage_path(
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
            # self.storage_dict['message'] = 'Source uploaded'

        else:
            print()
            # self.storage_dict['message'] = 'Source not found'

        # self.storage_dict['objlist'] = files_uploaded
        # pprint(self.storage_dict)
        # dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        # return dict_obj
        specification['status'] = 'completed'
        return specification

    # function to search a file or directory and list its attributes
    def search_run(self, specification):

        directory = specification['directory']
        filename = specification['filename']
        recursive = specification['recursive']

        len_dir = len(self.massage_path(directory))
        if len_dir > 0:
            file_path = self.massage_path(directory) + '/' + filename
        else:
            file_path = filename

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
        elif (len_dir > 0) and recursive is True:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=self.massage_path(directory)))
        elif (len_dir == 0) and recursive is True:
            objs = list(
                self.s3_resource.Bucket(self.container_name).objects.all())

        if len(objs) > 0:
            for obj in objs:
                if os.path.basename(obj.key) == filename:
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=obj.key)
                    info = {
                        "fileName": obj.key,
                        "lastModificationDate":
                            metadata['ResponseMetadata']['HTTPHeaders'][
                                'last-modified'],
                        "contentLength":
                            metadata['ResponseMetadata']['HTTPHeaders'][
                                'content-length']
                    }
                    info_list.append(info)

        if len(info_list) == 0:
            print("File not found")
        else:
            print("File found")

        specification['status'] = 'completed'
        return specification

    def cancel_run(self, specification):
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        act_id = specification['cm']['name']
        if act_id == 'None':
            for entry in entries:
                if entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
        else:
            for entry in entries:
                if entry['cm']['id'] == act_id and entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
                    break
        cm.update(entries)

        specification['status'] = 'completed'
        return specification

    @DatabaseUpdate()
    def copy(self, sourcefile, destinationfile, recursive=False):
        """
        adds a copy action to the queue

        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.

        The copy will not be performed if the files are the same.

        :param sourcefile: The source file to copy
        :param destinationfile: The destination file path
        :param recursive: whether or not copy the file/dir recursively
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{sourcefile}:{destinationfile}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            action: copy
            source: {sourcefile}
            destination: {destinationfile}
            recursive: {recursive}
            status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def delete(self, source, recursive=True):
        """
        adds a delete action to the queue

        :param source:
        :param recursive:
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                cm:
                   number: {self.number}
                   name: "{source}"
                   kind: storage
                   id: {uuid_str}
                   cloud: {self.name}
                   collection: {self.collection}
                   created: {date}
                action: delete
                source:
                  path: {source}
                recursive: {recursive}
                status: waiting
                """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def search(self, directory=None, filename=None, recursive=False):

        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                    cm:
                       number: {self.number}
                       name: "{directory}:{filename}"
                       kind: storage
                       id: {uuid_str}
                       cloud: {self.name}
                       collection: {self.collection}
                       created: {date}
                    action: search
                    directory: {directory}
                    filename: {filename}
                    recursive: {recursive}
                    status: waiting
                    """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def cancel(self, action_id=None):
        """
        cancels a job with a specific id
        :param action_id:
        :return:
        """
        # if None all are canceled
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                        cm:
                           number: {self.number}
                           name: "{action_id}"
                           kind: storage
                           id: {uuid_str}
                           cloud: {self.name}
                           collection: {self.collection}
                           created: {date}
                        action: cancel
                        status: waiting
                        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def get(self, source, destination, recursive=False):
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                          cm:
                            number: {self.number}
                            kind: storage
                            id: {uuid_str}
                            cloud: {self.name}
                            name: {source}:{destination}
                            collection: {self.collection}
                            created: {date}
                          action: get
                          source: {source}
                          destination: {destination}
                          recursive: {recursive}
                          status: waiting
                    """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def put(self, source, destination, recursive=False):
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                              cm:
                                number: {self.number}
                                kind: storage
                                id: {uuid_str}
                                cloud: {self.name}
                                name: {source}:{destination}
                                collection: {self.collection}
                                created: {date}
                              action: put
                              source: {source}
                              destination: {destination}
                              recursive: {recursive}
                              status: waiting
                        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def create_dir(self, directory):
        """
        adds a mkdir action to the queue

        create the directory in the storage service
        :param path:
        :return:
        """

        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                  cm:
                    number: {self.number}
                    kind: storage
                    id: {uuid_str}
                    cloud: {self.name}
                    name: {directory}
                    collection: {self.collection}
                    created: {date}
                  action: mkdir
                  path: {directory}
                  status: waiting
            """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def list(self, source, dir_only=False, recursive=False):
        """
        adds a list action to the queue

        list the directory in the storage service
        :param source:
        :param dir_only:
        :param recursive:
        :return:
        """

        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                      cm:
                        number: {self.number}
                        kind: storage
                        id: {uuid_str}
                        cloud: {self.name}
                        name: {source}
                        collection: {self.collection}
                        created: {date}
                      action: list
                      path: {source}
                      dironly: {dir_only}
                      status: waiting
                """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1

        return entries

    def action(self, specification):
        """
        executes the action identified by the specification. This is used by the
        run command.

        :param specification:
        :return:
        """
        action = specification["action"]
        if action == "copy":
            # print("COPY", specification)
            specification = self.put_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "delete":
            # print("DELETE", specification)
            specification = self.delete_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "mkdir":
            # print("MKDIR", specification)
            specification = self.mkdir_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "list":
            # print("LIST", specification)
            specification = self.list_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "cancel":
            specification = self.cancel_run(specification)
            self.update_dict(elements=[specification])
        elif action == "get":
            specification = self.get_run(specification)
            self.update_dict(elements=[specification])
        elif action == "put":
            specification = self.put_run(specification)
            self.update_dict(elements=[specification])
        elif action == "search":
            specification = self.search_run(specification)
            self.update_dict(elements=[specification])

    def get_actions(self):
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        get_actions = []
        put_actions = []
        mkdir_actions = []
        copy_actions = []
        list_actions = []
        delete_actions = []
        cancel_actions = []
        search_actions = []

        for entry in entries:
            pprint(entry)
            if entry['action'] == 'get' and entry['status'] == 'waiting':
                get_actions.append(entry)
            elif entry['action'] == 'put' and entry['status'] == 'waiting':
                put_actions.append(entry)
            elif entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                mkdir_actions.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                copy_actions.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                list_actions.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                delete_actions.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                cancel_actions.append(entry)
            elif entry['action'] == 'search' and entry['status'] == 'waiting':
                search_actions.append(entry)

        return get_actions, put_actions, mkdir_actions, copy_actions, \
               list_actions, delete_actions, cancel_actions, search_actions

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        get_action, put_action, mkdir_action, copy_action, list_action, \
        delete_action, cancel_action, search_action = self.get_actions()

        pool = Pool(self.parallelism)
        # cancel the actions
        pool.map(self.action, cancel_action)

        # delete files/directories
        pool.map(self.action, delete_action)

        # create directories
        pool.map(self.action, mkdir_action)

        # COPY FILES
        pool.map(self.action, copy_action)

        # PUT FILES
        pool.map(self.action, put_action)

        # GET FILES
        pool.map(self.action, get_action)

        # LIST FILES
        pool.map(self.action, list_action)

        # SEARCH FILES
        pool.map(self.action, search_action)

        # Worker processes within a Pool typically live for the complete \
        # duration of the Pool’s work queue.

        # Prevents any more tasks from being submitted to the pool.Once all
        # the tasks have been completed the worker processes will exit.
        pool.close()
        # Wait for the worker processes to exit.One must call close() or \
        # terminate() before using join().
        pool.join()


    # function to massage file path and do some transformations
    # for different scenarios of file inputs
    @staticmethod
    def massage_path(file_name_path):
        massaged_path = file_name_path

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

    # Function to extract obj dict from metadata
    @staticmethod
    def extract_file_dict(filename, metadata):
        info = {
            "fileName": filename,
            "lastModificationDate":
                metadata['ResponseMetadata']['HTTPHeaders'][
                    'last-modified'],
            "contentLength":
                metadata['ResponseMetadata']['HTTPHeaders'][
                    'content-length']
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
            obj = list(self.s3_resource.Bucket(self.container_name)
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
            return dict_obj

        except botocore.exceptions.ClientError as e:
            if e:
                message = "One or more errors occurred while creating the  " \
                          "bucket: {}".format(e)
                raise Exception(message)

    def bucket_exists(self, name=None):
        """
        gets the source from the put function

        :param name: the bucket name which needs to be checked for exists

        :return: Boolean

        """
        try:
            self.s3_client.head_bucket(Bucket=name)
            return True
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



if __name__ == "__main__":
    print()
    p = Provider(service="parallelawss3")

    # p.create_dir(directory="testdir2")
    # p.create_dir(directory="testdir3")
    # p.create_dir(directory="testdir4")
    # p.list(directory=".")
    # p.delete(path="testdir1")
    # p.copy(sourcefile="./Provider.py", destinationfile="myProvider.py")
    # p.put(source="shihui.txt", destination="shihui123.txt", recursive=False)
    # p.run()


