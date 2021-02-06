import os
import platform
import stat
import textwrap

import boto3
import botocore
from cloudmesh.storage.provider.StorageQueue import StorageQueue
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase

from cloudmesh.storage.provider.awss3.path_manager import \
    extract_file_dict
from cloudmesh.storage.provider.awss3.path_manager import massage_path


class Provider(StorageQueue):
    kind = "awss3"

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
                kind: awss3
                version: latest
                service: storage
              default:
                directory: /
              credentials:
                name: {username}
                bucket: {container_name}
                container: {container_name}
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

    output = {
        "monitor": {
            "sort_keys": ["cm.number"],
            "order": ["cm.number",
                      "cm.name",
                      "cm.kind",
                      "cm.cloud",
                      "action",
                      "status",
                      "path",
                      "source",
                      "destination",
                      "recursive",
                      ],
            "header": ["Number",
                       "Name",
                       "Kind",
                       "Cloud",
                       "Action",
                       "Status",
                       "Path",
                       "Source",
                       "Destination",
                       "Recursive",
                       ]
        },
        "files": {
            "sort_keys": ["fileName"],
            "order": [
                "fileName",
                "contentLength",
                "lastModificationDate",
            ],
            "header": [
                "FileName",
                "Size",
                "LastModified",
            ]
        }
    }

    def __init__(self, service=None, parallelism=4):
        """
        :param service: service name
        :param config:
        """
        super().__init__(service=service, parallelism=parallelism)
        self.container_name = self.credentials['bucket']
        self.dir_marker_file_name = 'marker.txt'

    def mkdir_run(self, specification):
        """
        function to create a directory the function will
        first check if the bucket  exists or not,
        if the bucket doesn't exist it will create the bucket
        and it will create the directory specified.
        the name of the bucket will come from YAML specifications and the
        directory name comes from the arguments.

        :param specification:
        :return:
        """
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
        # AWS S3 doesn't allow the first character in the path to be /
        if len(directory) > 0 and directory[0] == '/':
            directory = directory[1:]
        self.s3_resource, self.s3_client = self.get_s3_resource_client()

        file_content = ""
        file_path = massage_path(directory)
        dir_files_list = []

        bucket = self.container_name
        if not self.bucket_exists(name=bucket):
            self.bucket_create(name=bucket)

        obj = list(
            self.s3_resource.Bucket(self.container_name)
                .objects.filter(Prefix=file_path + '/'))

        if len(obj) == 0:
            self.s3_resource.Object(
                self.container_name,
                f"{file_path}/{self.dir_marker_file_name}"
            ).put(Body=file_content)

            # make head call to extract meta data
            # and derive obj dict
            metadata = self.s3_client.head_object(
                Bucket=self.container_name,
                Key=f"{file_path}/{self.dir_marker_file_name}")
            dir_files_list.append(extract_file_dict(
                f"{file_path}/", metadata)
            )
        else:
            Console.warning('Directory already present')

        self.pretty_print(data=dir_files_list, data_type="files",
                          output="table")
        specification['status'] = 'completed'
        return specification

    def get_s3_resource_client(self):
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.credentials['access_key_id'],
            aws_secret_access_key=self.credentials['secret_access_key'],
            region_name=self.credentials['region']
        )
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.credentials['access_key_id'],
            aws_secret_access_key=self.credentials['secret_access_key'],
            region_name=self.credentials['region']
        )

        return s3_resource, s3_client

    def list_run(self, specification):
        """
        function to list file  or directory
        lists the information as dict
        :return: dict
        """
        # if dir_only:
        #    raise NotImplementedError
        source = specification['path']
        # AWS S3 doesn't allow the first character in the path to be /
        if len(source) > 0 and source[0] == '/':
            source = source[1:]
        dir_only = specification['dir_only']
        recursive = specification['recursive']

        self.s3_resource, self.s3_client = self.get_s3_resource_client()

        objs = list(self.s3_resource.Bucket(self.container_name).objects.all())

        dir_files_list = []
        trimmed_source = massage_path(source)

        if not recursive:
            # call will not be recursive and need to look only in the
            # specified directory
            for obj in objs:
                if obj.key.startswith(massage_path(trimmed_source)):
                    file_name = obj.key
                    if file_name[-1] == '/':

                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):

                            dirFilesList.append(fileName)
                        '''
                        Console.msg()
                    else:
                        # Its a file
                        trimmed_filename = file_name.replace(trimmed_source, '')
                        if len(trimmed_filename) == 0:
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

                        elif (trimmed_filename[0] == '/'
                              and 1 == trimmed_filename.count('/')):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

                        elif (trimmed_filename[0] != '/'
                              and 0 == trimmed_filename.count('/')):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

        else:
            # call will be recursive and need to look recursively in the
            # specified directory as well
            for obj in objs:
                if obj.key.startswith(massage_path(trimmed_source)):
                    file_name = obj.key
                    if file_name[-1] == '/':
                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            dirFilesList.append(fileName)
                        '''
                        Console.msg()
                    else:
                        # its a file
                        # dir_files_list.append(file_name)

                        # make head call to extract meta data
                        # and derive obj dict
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=file_name)
                        dir_files_list.append(
                            extract_file_dict(file_name, metadata))

        self.pretty_print(data=dir_files_list, data_type="files",
                          output="table")
        specification['status'] = 'completed'
        return specification

    def delete_run(self, specification):
        # function to delete file or directory
        """
        deletes the source
        :param specification:
        :return: dict
        """
        source = specification['path']
        # AWS S3 doesn't allow the first character in the path to be /
        if len(source) > 0 and source[0] == '/':
            source = source[1:]
        recursive = specification['recursive']

        trimmed_source = massage_path(source)

        dir_files_list = []
        file_obj = ''

        # setting recursive as True for all delete cases
        # recursive = True
        self.s3_resource, self.s3_client = self.get_s3_resource_client()

        try:
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=trimmed_source)
        except botocore.exceptions.ClientError as e:
            # object not found
            # Console.warning(e)
            # Console.warning(e)
            x = 1

        if file_obj:
            # Its a file and can be deleted

            # make head call to extract meta data
            # and derive obj dict
            metadata = self.s3_client.head_object(
                Bucket=self.container_name, Key=trimmed_source)
            dir_files_list.append(
                extract_file_dict(trimmed_source, metadata))

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
                Console.msg()
                # self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is True:
                for obj in all_objs:
                    # if obj.key.startswith(self.massage_path(trimmedSource)):

                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=obj.key)
                    # make head call to extract meta data
                    # and derive obj dict
                    if os.path.basename(obj.key) != self.dir_marker_file_name:
                        dir_files_list.append(
                            extract_file_dict(obj.key, metadata))
                    else:
                        dir_files_list.append(extract_file_dict(
                            obj.key.replace(os.path.basename(obj.key), ''),
                            metadata))

                    self.s3_resource.Object(self.container_name,
                                            obj.key).delete()
                    # dir_files_list.append(obj.key)

                # self.storage_dict['message'] = 'Source Deleted'

            elif total_all_objs > 0 and recursive is False:
                # check if marker file exists in this directory
                pre_key = f"{trimmed_source}/{self.dir_marker_file_name}"
                marker_obj_list = list(
                    self.s3_resource.Bucket(
                        self.container_name).objects.filter(Prefix=pre_key)
                )
                marker_exits = False
                if len(marker_obj_list) == 1:
                    marker_exits = True

                if marker_exits is True and total_all_objs == 1:
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=pre_key)

                    dir_files_list.append(
                        extract_file_dict(f"{trimmed_source}/", metadata))

                    self.s3_resource.Object(
                        self.container_name, pre_key).delete()
                    # self.storage_dict['message'] = 'Source Deleted'
                else:
                    Console.msg()
                    # self.storage_dict[
                    # 'message'] = 'Source has child objects. Please delete ' \
                    # 'child objects first or use recursive option'

        # self.storage_dict['objlist'] = dir_files_list
        # pprint(self.storage_dict)
        # dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        # return dict_obj
        self.pretty_print(data=dir_files_list, data_type="files",
                          output="table")

        specification['status'] = 'completed'
        return specification

    def get_run(self, specification):
        """
        function to download file or directory
        gets the source from the service
        :param: specification:
        :return: dict
        """

        source = specification['source']
        # AWS S3 doesn't allow the first character in the path to be /
        if len(source) > 0 and source[0] == '/':
            source = source[1:]
        destination = specification['destination']
        recursive = specification['recursive']
        trimmed_src = massage_path(source)
        trimed_dest = massage_path(destination)

        self.s3_resource, self.s3_client = self.get_s3_resource_client()

        file_obj = ''

        try:
            search_key = trimmed_src
            if len(trimmed_src) == 0:
                search_key = "/"
            file_obj = self.s3_client.get_object(Bucket=self.container_name,
                                                 Key=search_key)
        except botocore.exceptions.ClientError as e:   # noqa: F841
            # object not found
            x=1
        files_downloaded = []

        is_target_file = os.path.isfile(trimed_dest)
        is_target_dir = os.path.isdir(trimed_dest)

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
                    os_path_trim_source = os.path.basename(trimmed_src)
                    blob = self.s3_resource.Bucket(
                        self.container_name).download_file(
                        trimmed_src,
                        f"{trimed_dest}/{os_path_trim_source}"
                    )
                else:
                    blob = self.s3_resource.Bucket(
                        self.container_name).download_file(
                        trimmed_src, trimed_dest)

                # make head call since file download does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_src)
                files_downloaded.append(
                    extract_file_dict(trimmed_src, metadata))

                self.storage_dict['message'] = 'Source downloaded'
            except FileNotFoundError as e:
                self.storage_dict['message'] = 'Destination not found'
                Console.warning(e)

        else:
            # Search for a directory
            all_objs = list(
                self.s3_resource.Bucket(self.container_name).objects.filter(
                    Prefix=trimmed_src))

            total_all_objs = len(all_objs)

            if total_all_objs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_all_objs > 0 and recursive is False:
                for obj in all_objs:
                    if os.path.basename(obj.key) != self.dir_marker_file_name:
                        replaced_trimmed_src = obj.key.replace(trimmed_src, '')
                        if massage_path(replaced_trimmed_src).count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    f"{trimed_dest}/{os.path.basename(obj.key)}"
                                )

                                # make head call since file download does not
                                # return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    extract_file_dict(obj.key, metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'
                                Console.warning(e)

            elif total_all_objs > 0 and recursive is True:
                files_downloaded = []
                for obj in all_objs:
                    base_name = os.path.basename(obj.key)
                    name_equal_marker = base_name == self.dir_marker_file_name
                    if not name_equal_marker and obj.key[-1] != '/':
                        replaced_trimmed_src = obj.key.replace(
                            trimmed_src, '')
                        if massage_path(replaced_trimmed_src).count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    obj.key,
                                    f"{trimed_dest}/{os.path.basename(obj.key)}"
                                )

                                # make head call since file download does
                                # not return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    extract_file_dict(obj.key, metadata))

                            except FileNotFoundError as e:
                                Console.warning(e)
                        else:

                            folder_path = massage_path(
                                obj.key.replace(trimmed_src, '').replace(
                                    os.path.basename(obj.key), '')
                            )
                            dest_path = f"{trimed_dest}/{folder_path}"
                            try:
                                os.makedirs(dest_path, 0o777)
                                Console.msg()
                            except FileExistsError as e:
                                os.chmod(dest_path, stat.S_IRWXO)
                                Console.warning(e)

                            try:
                                blob = self.s3_resource.Bucket(
                                    self.container_name).download_file(
                                    # obj.key, trimmedDestination + '/'
                                    # + os.path.basename(obj.key))
                                    obj.key,
                                    f"{trimed_dest}/{folder_path}"
                                    f"/{os.path.basename(obj.key)}")

                                # make head call since file download
                                # does not return obj dict to extract meta data
                                metadata = self.s3_client.head_object(
                                    Bucket=self.container_name, Key=obj.key)
                                files_downloaded.append(
                                    extract_file_dict(obj.key, metadata))

                            except FileNotFoundError as e:
                                Console.warning(e)

        specification['status'] = 'completed'

        return specification

    def put_run(self, specification):
        """
        function to upload file or directory
        puts the source on the service
        :param: specification
        :return: dict
        """

        source = specification['source']
        destination = specification['destination']
        # AWS S3 doesn't allow the first character in the path to be /
        if len(destination) > 0 and destination[0] == '/':
            destination = destination[1:]
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

        trimmed_source = massage_path(source)
        trimmed_destination = massage_path(destination)

        is_source_file = os.path.isfile(trimmed_source)
        is_source_dir = os.path.isdir(trimmed_source)

        files_uploaded = []
        self.s3_resource, self.s3_client = self.get_s3_resource_client()

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

            if not is_trimmed_destination_file:
                if len(trimmed_destination) == 0:
                    trimmed_destination = os.path.basename(trimmed_source)
                else:
                    trimmed_destination = \
                        f"{trimmed_destination}/{os.path.basename(trimmed_source)}"

            blob_obj = self.s3_client.upload_file(trimmed_source,
                                                  self.container_name,
                                                  trimmed_destination)
            # make head call since file upload does not return
            # obj dict to extract meta data
            metadata = self.s3_client.head_object(
                Bucket=self.container_name, Key=trimmed_destination)
            files_uploaded.append(
                extract_file_dict(trimmed_destination, metadata))
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
                            massaged_dirpath = f"{massage_path(dirpath)}\\{f}"
                        else:
                            massaged_dirpath = f"{massage_path(dirpath)}/{f}"
                        files_to_upload.append(massaged_dirpath)

                for file in files_to_upload:
                    directory, tgtfile = os.path.split(file)
                    if not trimmed_destination.endswith("/"):
                        trimmed_destination = trimmed_destination + "/"
                    tgt_file = trimmed_destination + tgtfile
                    # AWS S3 doesn't allow the first character in the path to be /
                    if len(tgt_file) > 0 and tgt_file[0] == '/':
                        tgt_file = tgt_file[1:]
                    self.s3_client.upload_file(file,
                                               self.container_name, tgt_file)

                    # make head call since file upload does not return
                    # obj dict to extract meta data
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=tgt_file)
                    files_uploaded.append(extract_file_dict(tgt_file, metadata))
            else:
                # get the directories with in the folder as well and upload
                files_to_upload = []
                for (dirpath, dirnames, filenames) in os.walk(trimmed_source):
                    for f in filenames:
                        if platform.system() == "Windows":
                            massaged_dirpath = f"{massage_path(dirpath)}\\{f}"
                        else:
                            massaged_dirpath = f"{massage_path(dirpath)}/{f}"
                        files_to_upload.append(massaged_dirpath)

                for file in files_to_upload:
                    if not trimmed_destination.endswith("/"):
                        trimmed_destination = trimmed_destination + "/"
                    tmp_src = massage_path(file.replace(trimmed_source, ''))
                    if len(tmp_src) > 0 and tmp_src[0] == '/':
                        tmp_src = tmp_src[1:]
                    tgt_file = trimmed_destination + tmp_src
                    # AWS S3 doesn't allow the first character in the path to be /
                    if len(tgt_file) > 0 and tgt_file[0] == '/':
                        tgt_file = tgt_file[1:]
                    self.s3_client.upload_file(
                        file, self.container_name, tgt_file)

                    # make head call since file upload does not return
                    # obj dict to extract meta data
                    metadata = self.s3_client.head_object(
                        Bucket=self.container_name, Key=tgt_file)
                    files_uploaded.append(extract_file_dict(tgt_file, metadata))

            # self.storage_dict['filesUploaded'] = files_uploaded
            # self.storage_dict['message'] = 'Source uploaded'

        else:
            Console.warning("Source not found")
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

        directory = specification['path']
        # AWS S3 doesn't allow the first character in the path to be /
        if len(directory) > 0 and directory[0] == '/':
            directory = directory[1:]
        filename = specification['filename']
        recursive = specification['recursive']

        len_dir = len(massage_path(directory))
        if len_dir > 0:
            file_path = f"{massage_path(directory)}/{filename}"
        else:
            file_path = filename

        self.s3_resource, self.s3_client = self.get_s3_resource_client()

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
                    Prefix=massage_path(directory)))
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
            Console.warning("File not found")
        else:
            Console.msg("File found")

        self.pretty_print(data=info_list, data_type="files", output="table")
        specification['status'] = 'completed'
        return specification

    def cancel_run(self, specification):
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        name = specification['cm']['name']
        if name == 'None':
            for entry in entries:
                if entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
        else:
            for entry in entries:
                if entry['cm']['id'] == name and entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
                    break
        cm.update(entries)

        specification['status'] = 'completed'
        return specification

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
            Console.msg("Bucket Created:", name)
            file_content = ""
            file_path = massage_path(name)
            self.storage_dict['action'] = 'bucket_create'
            self.storage_dict['bucket'] = name
            dir_files_list = []
            self.container_name = name
            obj = list(self.s3_resource.Bucket(self.container_name)
                       .objects.filter(Prefix=file_path + '/'))

            if len(obj) == 0:
                marker_object = self.s3_resource.Object(
                    self.container_name, self.dir_marker_file_name
                ).put(Body=file_content)

                # make head call to extract meta data
                # and derive obj dict
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name,
                    Key=self.dir_marker_file_name)
                dir_files_list.append(extract_file_dict(
                    massage_path(name),
                    metadata)
                )
                self.storage_dict['message'] = 'Bucket created'
            self.storage_dict['objlist'] = dir_files_list
            VERBOSE(self.storage_dict)
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
                Console.warning(f"Bucket {name} is private. Access forbidden!")
                return True
            elif error_code == 404:
                Console.warning(f"Bucket {name} does not exist")
                return False


if __name__ == "__main__":
    print()
    p = Provider(service="aws")
    # p.put(source="./Provider.py", destination="myProvider.py")
    # p.create_dir(directory="testdir3")
    # p.create_dir(directory="testdir")
    # p.list(source="/", recursive=True)
    # p.delete(source="testdir3")
    # p.copy(sourcefile="./Provider.py", destinationfile="myProvider.py")
    # p.get(source="myProvider.py", destination="shihui.py", recursive=False)
    # p.get(source="/", destination="/Users/shihuijiang/test/", recursive=True)
    # p.search(directory="/", filename="myProvider.py")
    # p.run()
