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
from cloudmesh.storage.parallelawss3.path_manager import extract_file_dict
from cloudmesh.storage.parallelawss3.path_manager import massage_path


#
# TODO: use Console.error, Console.msg, Console.ok instead of print
#

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

    # TODO: BUG: missing we need that as the table printer requires it
    output = {}

    def __init__(self,
                 name=None,
                 config="~/.cloudmesh/cloudmesh.yaml",
                 parallelism=4):
        """
        TBD

        :param service: TBD
        :param config: TBD
        """
        # pprint(service)
        super().__init__(service=name, config=config)
        self.parallelism = parallelism
        self.name = name
        self.collection = f"storage-queue-{name}"
        self.number = 0
        self.container_name = self.credentials['bucket']

        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    @DatabaseUpdate()
    def update_dict(self, elements, kind=None):
        """
        this is an internal function for building dict object

        :param elements:
        :param kind:
        :return:
        """
        d = []
        for element in elements:
            # entry = element.__dict__
            # entry = element['objlist']
            entry = element

            # element.properties = element.properties.__dict__
            d.append(entry)
        return d

    #
    # TODO: make static and move to path_manager.py
    #
    def join_file_name_dir(self, filename, dirname):
        """
        Function to join file name dir to get full file path

        :param filename:
        :param dirname:
        :return:
        """
        full_file_path = ''
        if len(self.massage_path(dirname)) > 0:
            # fullFilePath = self.massage_path(dirName) + '/' + \
            #                self.massage_path(fileName)
            full_file_path = self.massage_path(
                dirname) + '/' + self.massage_path(
                filename)
        else:
            full_file_path = self.massage_path(filename)
        return full_file_path

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
            Console.ok(f"Bucket Created: {name}")
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
                dir_files_list.append(extract_file_dict(
                    self.massage_path(name),
                    metadata)
                )
                self.storage_dict['message'] = 'Bucket created'
            self.storage_dict['objlist'] = dir_files_list
            pprint(self.storage_dict)
            dict_obj = self.update_dict(self.storage_dict['objlist'])
            # return self.storage_dict
            return dict_obj

        except botocore.exceptions.ClientError as e:
            if e:
                message = "One or more errors occurred while " \
                          "creating the bucket: {}".format(e)
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

    def _mkdir(self, specification):
        """
        function to create a directory the function will first check if the
        bucket exists or not,if the bucket doesn't exist it will create the
        bucket and it will create the directory specified. the name of the
        bucket will come from YAML specifications and the directory name comes
        from the arguments.

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
        #
        # TODO: put the parameter litst into a dict _credentials and use
        #       self.s3_resource = boto3.resource(**_credentials)
        #       self.s3_resource = boto3.client(**_credentials)
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

        obj = list(
            self.s3_resource.Bucket(self.container_name)
                .objects.filter(Prefix=file_path + '/'))

        # TODO: simplify adding strings with f"" strings
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
            dir_files_list.append(extract_file_dict(
                self.massage_path(directory) + '/', metadata)
            )
        else:
            print('Directory already present')

        specification['status'] = 'completed'
        return specification

    def _add_cm(self, spec, kwargs):
        textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{sourcefile}:{destinationfile}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
        """).format(**kwargs).strip()

    @DatabaseUpdate()
    def copy(self, sourcefile, destinationfile, recursive=False):
        """
        adds a copy action to the queue

        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.

        The copy will not be performed if the files are the same.

        :param sourcefile:
        :param destinationfile:
        :param recursive:
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
            source: 
              path: {sourcefile}
            destination: 
              path: {destinationfile}
            recursive: {recursive}
            status: waiting
        """)
        #
        # TODO: consider
        #
        # removing cm from the specification and using
        #
        # specification = textwrap.dedent(f"""
        #             action: copy
        #             source:
        #               path: {sourcefile}
        #             destination:
        #               path: {destinationfile}
        #             recursive: {recursive}
        #             status: waiting
        #         """)
        #
        # specification = self._add_cm(**locals()) + specification.strip() + "\n"
        #
        # EVALUATE and adapt
        #

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    #
    # TODO: make indentations of the yaml uniform, see delete, do this for all
    #
    @DatabaseUpdate()
    def delete(self, path, recursive=True):
        """
        adds a delete action to the queue

        :param path:
        :param recursive:

        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{path}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            action: delete
            source: 
              path: {path}
            recursive: {recursive}
            status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    #
    # BUG: THis should ideally be name and not id. THis has impact on all
    # providers as there may be a bug in the cancel methods including the ABC
    # class.
    #
    @DatabaseUpdate()
    def cancel(self, id=None):
        """
        cancels a job with a specific id
        :param id:
        :return:
        """
        # if None all are canceled
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{id}"
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
    def mkdir(self, path):
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
                    name: {path}
                    collection: {self.collection}
                    created: {date}
                  action: mkdir
                  path: {path}
                  status: waiting
            """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1

        return entries

    @DatabaseUpdate()
    def list(self, path, dir_only=False, recursive=False):
        """
        adds a list action to the queue

        list the directory in the storage service
        :param path:
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
                name: {path}
                collection: {self.collection}
                created: {date}
              action: list
              path: {path}
              dir_only:{dir_only}
              recursive:{recursive}
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
            specification = self._put(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "delete":
            # print("DELETE", specification)
            specification = self._delete(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "mkdir":
            # print("MKDIR", specification)
            specification = self._mkdir(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "list":
            # print("LIST", specification)
            specification = self._list(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "cancel":
            specification = self._cancel(specification)
            self.update_dict(elements=[specification])

    def get_actions(self):
        """
        TODO: missing

        :return:
        """
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        _mkdir = []
        _copy = []
        _list = []
        _delete = []
        _cancel = []
        for entry in entries:
            pprint(entry)
            if entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                _mkdir.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                _copy.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                _list.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                _delete.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                _cancel.append(entry)

        return _mkdir, _copy, _list, _delete, _cancel

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        mkdir_action, \
        copy_action, \
        list_action, \
        delete_action, \
        cancel_action = self.get_actions()

        # cancel the actions
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, cancel_action)

        # delete files/directories
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, delete_action)

        # create directories
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, mkdir_action)

        # COPY FILES
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, copy_action)

        # LIST FILES
        p = Pool(self.parallelism)
        p.map(self.action, list_action)

        # function to list file  or directory

    def _list(self, specification):
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
        source = specification['path']
        dir_only = specification['dir_only']
        recursive = specification['recursive']
        #
        # TODO: create function as yo used this before in mkdir
        #

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

            # call will not be recursive and need to look only in the specified
            # directory

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
                        trimmed_filename = file_name.replace(trimmed_source, '')
                        if len(trimmed_filename) == 0:
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

                        elif (trimmed_filename[0] == '/' and
                              trimmed_filename.count('/') == 1):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

                        elif (trimmed_filename[0] != '/' and
                              trimmed_filename.count('/') == 0):
                            # dir_files_list.append(file_name)

                            # make head call to extract meta data
                            # and derive obj dict
                            metadata = self.s3_client.head_object(
                                Bucket=self.container_name, Key=file_name)
                            dir_files_list.append(
                                extract_file_dict(file_name, metadata))

                    # print(fileName)
        else:

            # call will be recursive and need to look recursively in the
            # specified directory as well

            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmed_source)):
                    # print(obj.key)
                    file_name = obj.key

                    # file_name = obj.key.replace(
                    #     self.directory_marker_file_name, '')

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
                            extract_file_dict(file_name, metadata))
                    # print(fileName)
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
    def _delete(self, specification):
        """
        deletes the source

        :param specification:

        :return: dict

        """
        source = specification['source']['path']
        recursive = specification['recursive']

        trimmed_source = self.massage_path(source)

        dir_files_list = []
        file_obj = ''

        # setting recursive as True for all delete cases
        # recursive = True
        #
        # TODO: create function as yo used this before in mkdir
        #

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

            # print('File deleted')
            # self.storage_dict['message'] = 'Source Deleted'

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
                    if os.path.basename(obj.key) != \
                        self.directory_marker_file_name:

                        #
                        # TODO: consider moving this before if to redux=ce redundancy
                        #       evaluate other such things in your rest of the code
                        #
                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=obj.key)
                        #
                        # TODO: ^^^^^^
                        #
                        dir_files_list.append(
                            extract_file_dict(obj.key, metadata))
                    else:
                        #
                        # TODO: consider moving this before if to redux=ce redundancy
                        #

                        metadata = self.s3_client.head_object(
                            Bucket=self.container_name, Key=obj.key)
                        #
                        # TODO: ^^^^^^
                        #

                        dir_files_list.append(extract_file_dict(
                            obj.key.replace(os.path.basename(obj.key), ''),
                            metadata))

                    self.s3_resource.Object(self.container_name,
                                            obj.key).delete()
                    # dir_files_list.append(obj.key)

                # self.storage_dict['message'] = 'Source Deleted'

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
                        Key=trimmed_source +
                            '/' + self.directory_marker_file_name)
                    dir_files_list.append(
                        extract_file_dict(trimmed_source + '/',
                                          metadata))

                    self.s3_resource.Object(
                        self.container_name,
                        trimmed_source + '/' +
                        self.directory_marker_file_name).delete()
                    # self.storage_dict['message'] = 'Source Deleted'
                else:
                    print()
                    # self.storage_dict[
                    #     'message'] = 'Source has child objects. Please delete ' \
                    #                  'child objects first or use recursive option'

        # self.storage_dict['objlist'] = dir_files_list
        # pprint(self.storage_dict)
        # dict_obj = self.update_dict(self.storage_dict['objlist'])
        # return self.storage_dict
        # return dict_obj
        specification['status'] = 'completed'
        return specification

    def _put(self, specification):
        """
        function to upload file or directory
        puts the source on the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory
                            or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        source = specification['source']['path']
        destination = specification['destination']['path']
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
        #
        # TODO: create function as yo used this before in mkdir
        #

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

        #
        # TODO: large portion of the code is duplicated, when not use a
        #       function for things that are the same
        #
        if is_source_file is True:
            # print('file flow')
            # Its a file and need to be uploaded to the destination

            # check if trimmed_destination is file or a directory
            is_trimmed_destination_file = False
            dot_operator = '.'
            # print('destination base:', os.path.basename(trimmed_destination))
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

                #
                # TODO: move similar code after the if condition
                #       consider for the rest of the code also elsewhere
                #
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_destination)
                files_uploaded.append(
                    extract_file_dict(trimmed_destination, metadata))

            else:

                destination_key = ''
                if len(trimmed_destination) == 0:
                    destination_key = os.path.basename(trimmed_source)
                else:
                    destination_key = trimmed_destination + '/' + \
                                      os.path.basename(trimmed_source)

                blob_obj = self.s3_client.upload_file(trimmed_source,
                                                      self.container_name,
                                                      destination_key)

                # make head call since file upload does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=destination_key)
                files_uploaded.append(
                    extract_file_dict(destination_key, metadata))

            # self.storage_dict['message'] = 'Source uploaded'
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
                        extract_file_dict(trimmed_destination + tgtfile,
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
                    self.s3_client.upload_file(
                        file,
                        self.container_name,
                        trimmed_destination +
                        self.massage_path(file.replace(trimmed_source, '')))

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
                    files_uploaded.append(extract_file_dict(
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

    def _cancel(self, specification):
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

    def get(self, source=None, destination=None, recursive=False):
        """
        function to download file or directory
        gets the source from the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory
                            or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        # self.storage_dict['service'] = service
        self.storage_dict['action'] = 'get'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmed_source = massage_path(source)
        trimmed_destination = massage_path(destination)

        file_obj = ''

        try:
            file_obj = self.s3_client.get_object(
                Bucket=self.container_name, Key=trimmed_source)
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
                # trimmedSource, trimmedDestination + '/' +
                # os.path.basename(trimmedSource))
                # print('File downloaded')

                # make head call since file download does not return
                # obj dict to extract meta data
                metadata = self.s3_client.head_object(
                    Bucket=self.container_name, Key=trimmed_source)
                files_downloaded.append(
                    extract_file_dict(trimmed_source, metadata))

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

                #
                # TODO: large portion of the code is duplicated, when not use a
                #       function for things that are the same
                #
                for obj in all_objs:
                    if os.path.basename(obj.key) != \
                        self.directory_marker_file_name:
                        if massage_path(
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
                                    extract_file_dict(obj.key, metadata))

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
                        if massage_path(
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
                                    extract_file_dict(obj.key, metadata))

                                self.storage_dict[
                                    'message'] = 'Source downloaded'
                                # files_downloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict[
                                    'message'] = 'Destination not found'
                        else:

                            folder_path = massage_path(
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
                                    extract_file_dict(obj.key, metadata))

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

    def search(self,
               directory=None,
               filename=None,
               recursive=False):
        """
        function to search a file or directory and list its attributes
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
        len_dir = len(massage_path(directory))
        if len_dir > 0:
            file_path = massage_path(directory) + '/' + filename
        else:
            file_path = filename

        # print('file_path : ' +file_path )

        info_list = []
        objs = []

        # TODO: consider thi strick to make code more readable
        # filter = self.s3_resource.Bucket(self.container_name).objects.filter
        #
        # objs = list(filter(Prefix=file_path)))

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
                    Prefix=massage_path(directory)))
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
                    #
                    # TODO: see path_manager.py
                    #
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


if __name__ == "__main__":
    p = Provider(name="aws")
    # p.mkdir("/abcworking2")
    # p.mkdir("/abcworking3")
    # p.mkdir("/abcworking4")
    # p.mkdir("/abcworking5")
    # p.mkdir("/abcworking6")

    # p.list('/')
    # p.run()
    # p.cancel()
    # p.delete(path="testABC")
    # p.copy(sourcefile="./Provider.py", destinationfile="testABC.txt")

    p.run()
