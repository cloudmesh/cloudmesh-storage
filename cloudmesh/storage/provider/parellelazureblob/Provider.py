import os
import stat
from pprint import pprint

from azure.storage.blob import BlockBlobService
from cloudmesh.abstract.StorageABC import StorageABC
from cloudmesh.common.console import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from pathlib import Path
import platform
import textwrap
import uuid
import oyaml as yaml
from multiprocessing import Pool

from cloudmesh.common.DateTime import DateTime
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Provider(StorageABC):
    kind = "parallelazureblob"

    sample = textwrap.dedent(
        """
        cloudmesh:
          storage:
            {name}:
              cm:
                active: false
                heading: Azure
                host: azure.microsoft.com
                label: azure_blob
                kind: parallelazureblob
                version: TBD
                service: storage
              default:
                resource_group: cloudmesh
                location: Central US
              credentials:
                account_name: {account_name}
                account_key: {account_key}
                container: {container}
                AZURE_TENANT_ID: {azure_tenant_id}
                AZURE_SUBSCRIPTION_ID: {azure_subscription_id}
                AZURE_APPLICATION_ID: {azure_application_id}
                AZURE_SECRET_KEY: {azure_secret_key}
                AZURE_REGION: Central US
             """
    )
    status = [
        'completed',
        'waiting',
        'inprogress',
        'canceled'
    ]

    output = {}  # "TODO: missing"

    def __init__(self, name=None, parallelism=4):
        """
        TBD

        :param service: TBD
        :param config: TBD
        """
        # pprint(service)
        super().__init__(service=name)
        self.parallelism = parallelism
        self.name = name
        self.collection = f"storage-queue-{name}"
        self.number = 0
        self.storage_dict = {}
    '''
    def __init__(self, service= None):
        super().__init__(service=service)
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])
        self.container = self.credentials['container']
        self.cloud = service
        self.service = service
    '''

    @DatabaseUpdate()

    def update_dict(self, elements, func=None):
        # this is an internal function for building dict object
        d = []
        for element in elements:

            entry = element.__dict__
            entry["cm"] = {
                "kind": "storage",
                "cloud": self.cloud,
                "name": element.name
            }

            element.properties = element.properties.__dict__
            entry["cm"]["created"] = \
                element.properties["create"].isoformat()[0]
            entry["cm"]["updated"] = \
                element.properties["last_modified"].isoformat()[0]
            entry["cm"]["size"] = element.properties["content_length"]
            del element.properties["copy"]
            del element.properties["lease"]
            del element.properties["content_settings"]
            del element.properties["create"]
            del element.properties["last_modified"]
            if func == 'delete':
                entry["cm"]["status"] = "deleted"
            else:
                entry["cm"]["status"] = "exists"
            if element.properties["deleted_time"] is not None:
                entry["cm"]["deleted"] = element.properties[
                    "deleted_time"].isoformat()
                del element.properties["deleted_time"]

            d.append(entry)
        return d

    def cloud_path(self, srv_path):
        # Internal function to determine if the cloud path specified is file or folder or mix
        b_folder = None
        b_file = None
        src_file = srv_path
        if srv_path.startswith('/'):
            src_file = srv_path[1:]
        if self.storage_service.exists(self.container, src_file):
            b_file = os.path.basename(srv_path)
            if srv_path.startswith('/'):
                b_folder = os.path.dirname(src_file)
        else:
            if srv_path.startswith('/'):
                b_folder = src_file
            else:
                b_file = os.path.basename(srv_path)
        return b_file, b_folder

    def local_path(self, source_path):
        src_path = path_expand(source_path)
        # Code added to skip join for absolute paths
        # In Windows src_path[0] is drive name "C"
        if not Path(src_path).is_absolute():
            if src_path[0] not in [".", "/", "~"]:
                src_path = os.path.join(os.getcwd(), source_path)
        return src_path

    
    def _mkdir(self, specification):
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
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])

        HEADING()
        banner("Please note: Directory in Azure is a virtual folder, "
               "hence creating it with a uni-byte file - dummy.txt")

        marker_file = 'dummy.txt'
        blob_cre = []

        if re.search('/', directory[1:]) is None:
            data = b' '
            blob_name = directory[1:] + '/' + marker_file
            self.storage_service.create_blob_from_bytes(self.container,
                                                        blob_name, data)
            blob_cre.append(
                self.storage_service.get_blob_to_bytes(self.container,
                                                       blob_name))
        else:
            dir_list = directory[1:].split('/')
            path_list = []
            path_list.append(directory[1:])
            old_path = directory[1:]
            for i in range(len(dir_list) - 1):
                new_path = os.path.dirname(old_path)
                path_list.append(new_path)
                old_path = new_path

            dir_gen = self.storage_service.list_blobs(self.container)
            for path in path_list:
                path_found = False
                for blob in dir_gen:
                    if os.path.dirname(blob.name) == path:
                        path_found = True
                if not path_found:
                    data = b' '
                    blob_name = path + '/' + marker_file
                    self.storage_service.create_blob_from_bytes(self.container,
                                                                blob_name, data)
                    if path == directory[1:]:
                        blob_cre.append(
                            self.storage_service.get_blob_to_bytes(
                                self.container, blob_name))

        # dict_obj = self.update_dict(blob_cre)
        # pprint(dict_obj[0])
        return blob_cre


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
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def delete(self, path, recursive=True):
        """
        adds a delete action to the queue

        :param path:
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
        :param service: service must be either source or destination
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
        :param service: service must be either source or destination
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
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        mkdir = []
        copy = []
        list = []
        delete = []
        cancel = []
        for entry in entries:
            pprint(entry)
            if entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                mkdir.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                copy.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                list.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                delete.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                cancel.append(entry)

        return mkdir, copy, list, delete, cancel

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        mkdir_action, copy_action, list_action, delete_action, cancel_action = self.get_actions()

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
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])

        HEADING()

        blob_file, blob_folder = self.cloud_path(source)

        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        obj_list = []
        fold_list = []
        file_list = []
        if blob_folder is None:
            # SOURCE specified is File only
            if not recursive:
                if self.storage_service.exists(self.container, blob_file):
                    blob_prop = self.storage_service.get_blob_properties(
                        self.container,
                        blob_file)
                    blob_size = self.storage_service.get_blob_properties(
                        self.container,
                        blob_file).properties.content_length
                    obj_list.append(blob_prop)
                else:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
            else:
                file_found = False
                srch_gen = self.storage_service.list_blobs(self.container)
                for blob in srch_gen:
                    if os.path.basename(blob.name) == blob_file:
                        obj_list.append(blob)
                        file_found = True
                if not file_found:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
        else:
            if blob_file is None:
                # SOURCE specified is Directory only
                if not recursive:
                    file_found = False
                    srch_gen = self.storage_service.list_blobs(self.container)
                    for blob in srch_gen:
                        if os.path.dirname(blob.name) == blob_folder:
                            obj_list.append(blob)
                            file_list.append(os.path.basename(blob.name))
                            file_found = True
                        if blob_folder == '':
                            if re.search('/', blob.name):
                                srch_fold = \
                                    os.path.dirname(blob.name).split('/')[0]
                                file_found = True
                                if srch_fold not in fold_list:
                                    fold_list.append(srch_fold)
                        else:
                            if blob not in obj_list:
                                if len(os.path.dirname(blob.name).split(
                                    '/')) == len(blob_folder.split('/')) + 1:
                                    fold_match = 'Y'
                                    for e in os.path.dirname(blob.name).split(
                                        '/')[:-1]:
                                        if e not in blob_folder.split('/'):
                                            fold_match = 'N'
                                    if fold_match == 'Y':
                                        srch_fold = \
                                            os.path.dirname(blob.name).split(
                                                '/')[
                                                len(blob_folder.split('/'))]
                                        file_found = True
                                        if srch_fold not in fold_list:
                                            fold_list.append(srch_fold)
                    if not file_found:
                        return Console.error(
                            "Directory does not exist: {directory}".format(
                                directory=blob_folder))
                else:
                    file_found = False
                    srch_gen = self.storage_service.list_blobs(self.container)
                    for blob in srch_gen:
                        if (os.path.dirname(blob.name) == blob_folder) or \
                            (os.path.commonpath(
                                [blob.name, blob_folder]) == blob_folder):
                            obj_list.append(blob)
                            file_list.append(blob.name)
                            file_found = True
                    if not file_found:
                        return Console.error(
                            "Directory does not exist: {directory}".format(
                                directory=blob_folder))
            else:
                # SOURCE is specified with Directory and file
                if not recursive:
                    if self.storage_service.exists(self.container, source[1:]):
                        blob_prop = self.storage_service.get_blob_properties(
                            self.container, source[1:])
                        blob_size = self.storage_service.get_blob_properties(
                            self.container,
                            source[1:]).properties.content_length
                        obj_list.append(blob_prop)
                    else:
                        return Console.error(
                            "File does not exist: {file}".format(
                                file=source[1:]))
                else:
                    return Console.error(
                        "Invalid arguments, recursive not applicable")
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj

        if len(file_list) > 0:
            hdr = '#' * 90 + '\n' + 'List of files in the folder ' + '/' + blob_folder + ':'
            Console.cprint("BLUE", "", hdr)
            print(file_list)
            if len(fold_list) == 0:
                trl = '#' * 90
                Console.cprint("BLUE", "", trl)

        if len(fold_list) > 0:
            hdr = '#' * 90 + '\n' + 'List of Sub-folders under the folder ' + '/' + blob_folder + ':'
            Console.cprint("BLUE", "", hdr)
            print(fold_list)
            trl = '#' * 90
            Console.cprint("BLUE", "", trl)
        return dict_obj
    # function to delete file or directory
    def _delete(self, specificatioin):
        """
        deletes the source

        :param specificatioin:

        :return: dict

        """
        source = specificatioin['source']['path']
        recursive = specificatioin['recursive']

        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])

        # setting recursive as True for all delete cases
        # recursive = True

        HEADING()

        blob_file, blob_folder = self.cloud_path(source)
        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        obj_list = []
        if blob_folder is None:
            # SOURCE specified is File only
            if self.storage_service.exists(self.container, blob_file):
                blob_prop = self.storage_service.get_blob_properties(
                    self.container,
                    blob_file)
                obj_list.append(blob_prop)
                self.storage_service.delete_blob(self.container, blob_file)
            else:
                return Console.error(
                    "File does not exist: {file}".format(file=blob_file))
        else:
            if blob_file is None:
                # SOURCE specified is Folder only
                del_gen = self.storage_service.list_blobs(self.container)
                file_del = False
                for blob in del_gen:
                    if os.path.commonpath(
                        [blob.name, blob_folder]) == blob_folder:
                        obj_list.append(blob)
                        self.storage_service.delete_blob(self.container,
                                                         blob.name)
                        file_del = True
                if not file_del:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_folder))
            else:
                # Source specified is both file and directory
                if self.storage_service.exists(self.container, source[1:]):
                    blob_prop = self.storage_service.get_blob_properties(
                        self.container,
                        source[1:])
                    obj_list.append(blob_prop)
                    self.storage_service.delete_blob(self.container, source[1:])
                else:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
        dict_obj = self.update_dict(obj_list, func='delete')
        pprint(dict_obj)
        return dict_obj

    # function to upload file or directory
    def _put(self, specification):
        """
       puts the source on the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        source = specification['source']['path']
        destination = specification['destination']['path']
        recursive = specification['recursive']
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])

        HEADING()
        # Determine service path - file or folder
        if self.storage_service.exists(self.container, destination[1:]):
            return Console.error("Directory does not exist: {directory}".format(
                directory=destination))
        else:
            blob_folder = destination[1:]
            blob_file = None

        # Determine local path i.e. upload-from-folder
        src_path = self.local_path(source)

        if os.path.isdir(src_path) or os.path.isfile(src_path):
            obj_list = []
            if os.path.isfile(src_path):
                # File only specified
                upl_path = src_path
                if blob_folder == '':
                    upl_file = os.path.basename(src_path)
                else:
                    upl_file = blob_folder + '/' + os.path.basename(src_path)
                self.storage_service.create_blob_from_path(self.container,
                                                           upl_file, upl_path)
                obj_list.append(
                    self.storage_service.get_blob_properties(self.container,
                                                             upl_file))
            else:
                # Folder only specified - Upload all files from folder
                #
                # TODO: large portion of the code is duplicated, when not use a
                #       function for things that are the same
                #

                if recursive:
                    ctr = 1
                    old_root = ""
                    new_dir = blob_folder
                    for (root, folder, files) in os.walk(src_path,
                                                         topdown=True):
                        if ctr == 1:
                            if len(files) > 0:
                                for base in files:
                                    upl_path = os.path.join(root, base)
                                    if blob_folder == '':
                                        upl_file = base
                                    else:
                                        upl_file = blob_folder + '/' + base
                                    self.storage_service.create_blob_from_path(
                                        self.container, upl_file, upl_path)
                                    obj_list.append(
                                        self.storage_service.get_blob_properties(
                                            self.container,
                                            upl_file))
                        else:
                            if os.path.dirname(old_root) != os.path.dirname(
                                root):
                                blob_folder = new_dir
                            new_dir = os.path.join(blob_folder,
                                                   os.path.basename(root))
                            self.create_dir(service=None,
                                            directory='/' + new_dir)
                            if len(files) > 0:
                                for base in files:
                                    upl_path = os.path.join(root, base)
                                    upl_file = new_dir + '/' + base
                                    self.storage_service.create_blob_from_path(
                                        self.container, upl_file, upl_path)
                                    obj_list.append(
                                        self.storage_service.get_blob_properties(
                                            self.container,
                                            upl_file))
                            old_root = root
                        ctr += 1
                else:
                    return Console.error(
                        "Source is a folder, recursive expected in arguments")
        else:
            return Console.error(
                "Directory or File does not exist: {directory}".format(
                    directory=src_path))
        # dict_obj = self.update_dict(obj_list)
        # pprint(dict_obj)
        # return dict_obj
        return obj_list
    def _cancel(self, specification):
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        id = specification['cm']['name']
        if id == 'None':
            for entry in entries:
                if entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
        else:
            for entry in entries:
                if entry['cm']['id'] == id and entry['status'] == 'waiting':
                    entry['status'] = "cancelled"
                    break
        cm.update(entries)

        specification['status'] = 'completed'
        return specification
    def get(self,source=None, destination=None, recursive=False):
        """
        Downloads file from Destination(Service) to Source(local)

        :param source: the source can be a directory or file
        :param destination: the destination can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        HEADING()
        # Determine service path - file or folder
        #blob_file, blob_folder = self.cloud_path(destination)
        blob_file, blob_folder = self.cloud_path(source)
        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        # Determine local path i.e. download-to-folder
        src_path = self.local_path(destination)
        err_flag = 'N'
        rename = 'N'
        if os.path.isdir(src_path):
            rename = 'N'
        else:
            if os.path.isfile(src_path):
                Console.msg("WARNING: A file already exists with same name, "
                            "overwrite issued")
                rename = 'Y'
            else:
                if os.path.isdir(os.path.dirname(src_path)):
                    rename = 'Y'
                else:
                    err_flag = 'Y'

        if err_flag == 'Y':

            return Console.error(
                "Local directory not found or file already exists: {""src_path}")
        else:
            obj_list = []
            if blob_folder is None:
                # file only specified
                if not recursive:
                    if self.storage_service.exists(self.container, blob_file):
                        if rename == 'Y':
                            download_path = os.path.join(
                                os.path.dirname(src_path),
                                blob_file)
                        else:
                            download_path = os.path.join(src_path, blob_file)
                        obj_list.append(
                            self.storage_service.get_blob_to_path(
                                self.container,
                                blob_file,
                                download_path))
                        if rename == 'Y':
                            rename_path = src_path
                            os.rename(download_path, rename_path)
                    else:
                        return Console.error(
                            f"File does not exist: {blob_file}")
                else:
                    file_found = False
                    get_gen = self.storage_service.list_blobs(self.container)
                    for blob in get_gen:
                        if os.path.basename(blob.name) == blob_file:
                            download_path = os.path.join(src_path, blob_file)
                            obj_list.append(
                                self.storage_service.get_blob_to_path(
                                    self.container,
                                    blob.name,
                                    download_path))
                            file_found = True
                    if not file_found:
                        return Console.error(
                            "File does not exist: {file}".format(
                                file=blob_file))
            else:
                if blob_file is None:
                    # Folder only specified
                    if not recursive:
                        file_found = False
                        get_gen = self.storage_service.list_blobs(
                            self.container)
                        for blob in get_gen:
                            if os.path.dirname(blob.name) == blob_folder:
                                download_path = os.path.join(
                                    src_path,
                                    os.path.basename(blob.name))
                                obj_list.append(
                                    self.storage_service.get_blob_to_path(
                                        self.container, blob.name,
                                        download_path))
                                file_found = True
                        if not file_found:
                            return Console.error(
                                "Directory does not exist: {directory}".format(
                                    directory=blob_folder))
                    else:
                        file_found = False
                        srch_gen = self.storage_service.list_blobs(
                            self.container)
                        for blob in srch_gen:
                            if (os.path.dirname(blob.name) == blob_folder) or \
                                (os.path.commonpath([blob.name,
                                                     blob_folder]) == blob_folder):
                                cre_path = os.path.join(src_path,
                                                        os.path.dirname(
                                                            blob.name))
                                if not os.path.isdir(cre_path):
                                    os.makedirs(cre_path, 0o777)
                                download_path = os.path.join(src_path,
                                                             blob.name)
                                obj_list.append(
                                    self.storage_service.get_blob_to_path(
                                        self.container, blob.name,
                                        download_path))
                                file_found = True
                        if not file_found:
                            return Console.error(
                                "Directory does not exist: {directory}".format(
                                    directory=blob_folder))
                else:
                    # SOURCE is specified with Directory and file
                    if not recursive:
                        if self.storage_service.exists(self.container,
                                                       source[1:]):
                            if rename == 'Y':
                                download_path = os.path.join(
                                    os.path.dirname(src_path), blob_file)
                            else:
                                download_path = os.path.join(src_path,
                                                             blob_file)
                            obj_list.append(
                                self.storage_service.get_blob_to_path(
                                    self.container,
                                    source[1:],
                                    download_path))
                            if rename == 'Y':
                                rename_path = src_path
                                os.rename(download_path, rename_path)
                        else:
                            return Console.error(
                                "File does not exist: {file}".format(
                                    file=source[1:]))
                    else:
                        return Console.error(
                            "Invalid arguments, recursive not applicable")

        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj
        #return obj_list

    def search(self, directory=None, filename=None,recursive=False):
        """
        searches the filename in the directory

        :param directory: directory on cloud service
        :param filename: filename to be searched
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified directory
        :return: dict

        """


        HEADING()

        srch_gen = self.storage_service.list_blobs(self.container)
        obj_list = []
        if not recursive:

            srch_file = os.path.join(directory[1:], filename)
            file_found = False
            for blob in srch_gen:
                if blob.name == srch_file:
                    obj_list.append(blob)
                    file_found = True
            if not file_found:
                return Console.error(
                    "File does not exist: {file}".format(file=srch_file))
        else:
            file_found = False
            for blob in srch_gen:
                if re.search('/', blob.name) is not None:
                    if os.path.basename(blob.name) == os.path.basename(
                        filename):
                        if os.path.commonpath(
                            [blob.name, directory[1:]]) == directory[1:]:
                            if filename.startswith('/'):
                                if filename[1:] in blob.name:
                                    obj_list.append(blob)
                                    file_found = True
                            else:
                                if filename in blob.name:
                                    obj_list.append(blob)
                                    file_found = True
                else:

                    if blob.name == os.path.join(directory[1:], filename):
                        obj_list.append(blob)
                        file_found = True
            if not file_found:
                return Console.error(
                    "File does not exist: {file}".format(file=filename))

        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj
        #return obj_list

    # function to download file or directory


if __name__ == "__main__":
    p = Provider(name ="azure")
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

