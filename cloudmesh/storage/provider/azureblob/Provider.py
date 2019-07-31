import os
import re
from pprint import pprint

from azure.storage.blob import BlockBlobService
from cloudmesh.common.console import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.storage.StorageABC import StorageABC


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        super().__init__(service=service, config=config)
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])
        self.container = self.credentials['container']
        self.cloud = service
        self.service = service

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
                element.properties["creation_time"].isoformat()[0]
            entry["cm"]["updated"] = \
                element.properties["last_modified"].isoformat()[0]
            entry["cm"]["size"] = element.properties["content_length"]
            del element.properties["copy"]
            del element.properties["lease"]
            del element.properties["content_settings"]
            del element.properties["creation_time"]
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
        if src_path[0] not in [".", "/", "~"]:
            src_path = os.path.join(os.getcwd(), source_path)
        return src_path

    def get(self, service=None, source=None, destination=None, recursive=False):
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
        # blob_file, blob_folder = self.cloud_path(destination)
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
        # pprint(dict_obj)
        return dict_obj

    def put(self, service=None, source=None, destination=None, recursive=False):
        """
        Uploads file from Source(local) to Destination(Service)

        :param source: the source can be a directory or file
        :param destination: the destination can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

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
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj

    def delete(self, service=None, source=None, recursive=False):
        """
        Deletes the source from cloud service

        :param source: the source can be a directory or file
        :return: None

        """
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

    def create_dir(self, service=None, directory=None):
        """
        Creates a directory in the cloud service

        :param directory: directory is a folder
        :return: dict

        """

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

        dict_obj = self.update_dict(blob_cre)
        pprint(dict_obj[0])
        return dict_obj[0]

    def search(self, service=None, directory=None, filename=None,
               recursive=False):
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

    def list(self, service=None, source=None, recursive=False):
        """
        lists all files specified in the source

        :param source: this can be a file or directory
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

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
        # pprint(dict_obj)
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
