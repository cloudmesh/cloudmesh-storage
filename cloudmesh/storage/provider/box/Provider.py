from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
import os
from cloudmesh.storage.StorageABC import StorageABC

#
# TODO: BIG BUG variables can not be named type
#
def get_id(source, results, type):
    if not any((result.name == source and result.type == type) for result in
               results):
        return False
    else:
        ind = next((index for (index, result) in enumerate(results) if
                    (result.name == source)), None)
        #
        # BIG BUG youmust not use id as variable name
        #
        id = results[ind].id
        return id


def change_path(source):
    src_path = path_expand(source)
    if src_path[0] not in [".", "/"]:
        src_path = os.path.join(os.getcwd(), source)
    return src_path




class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):

        super(Provider, self).__init__(service=service, config=config)

        self.sdk = JWTAuth.from_settings_file(self.credentials['config_path'])
        # this needs to be well defined in ~/.cloudmesh/box/ ....
        self.client = Client(self.sdk)

    def update_dict(self, elements, service):
        if elements is None:
            return None
        elif type(elements) is list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for element in _elements:
            entry = element.__dict__
            entry["cm"] = {
                "kind": "storage",
                "cloud": self.service,
                "name": element.name
            }
            # BUG: I suggest you keep many of the attributes. we wnat as many as possible
            del (entry['_response_object'])
            del (entry['_session'])
            del (entry['created_by'])
            del (entry['file_version'])
            del (entry['modified_by'])
            del (entry['owned_by'])
            del (entry['parent'])
            del (entry['path_collection'])
            d.append(entry)
        return d

    def put(self, service='box', source=None, destination=None,
            recursive=False):
        """

        uploads file to Box, if source is directory and recursive is true
        uploads all files in source directory

        :param source: local file or directory to be uploaded
        :param destination: cloud directory to upload to
        :param recursive: if true upload all files in source directory,
                          source must be directory not file
        :return: file dict(s) that have been uploaded


        """
        try:
            destpath = destination.split('/')
            dest = destpath[len(destpath) - 1]
            sourcepath = change_path(source)
            path_array = sourcepath.strip('/').split('/')
            uploaded = []
            if dest == '':
                files = [item for item in self.client.folder('0').get_items()]
            else:
                items = self.client.search().query(dest, type='folder')
                folders = [item for item in items]
                folder_id = get_id(dest, folders, 'folder')
                if folder_id:
                    files = [item for item in
                             self.client.folder(folder_id).get_items()]
                else:
                    Console.error("Destination directory not found")
                    return
            if not recursive:
                if os.path.isfile(sourcepath):
                    filename = path_array[len(path_array) - 1]
                else:
                    Console.error("Invalid source path.")
                    return
                file_id = get_id(filename, files, 'file')
                if not file_id:
                    file = self.client.folder('0').upload(sourcepath)
                    files_dict = self.update_dict(file)
                    return files_dict
                else:
                    file = self.client.file(file_id).update_contents(sourcepath)
                    files_dict = self.update_dict(file)
                    return files_dict
            else:
                for s in os.listdir(source):
                    s_id = get_id(s, files, 'file')
                    if not s_id:
                        file = self.client.folder('0').upload(
                            sourcepath + '/' + s)
                        uploaded.append(file)
                    else:
                        file = self.client.file(s_id).update_contents(
                            sourcepath + '/' + s)
                        uploaded.append(file)
                files_dict = self.update_dict(uploaded)
                return files_dict
        except Exception as e:
            Console.error(e)

    def get(self, service='box', source=None, destination=None,
            recursive=False):
        """

        downloads file from Box, if recursive is true and source is directory downloads all files in directory
        :param source: cloud file or directory to download
        :param destination: local directory to be downloaded into
        :param recursive: if true download all files in source directory, source must be directory
        :return: file dict(s) that have been downloaded


        """
        try:

            boxpath = source.split('/')
            target = boxpath[len(boxpath) - 1]
            dest = change_path(destination)
            downloads = []
            if recursive:
                if target == '':
                    files = [item for item in
                             self.client.folder('0').get_items()]
                else:
                    results = [item for item in
                               self.client.search().query(target,
                                                          type='folder')]
                    folder_id = get_id(target, results, 'folder')
                    if folder_id:
                        files = [item for item in
                                 self.client.folder(folder_id).get_items()]
                    else:
                        Console.error("Source directory not found.")
                        return
                for f in files:
                    if f.type == 'file':
                        file = self.client.file(f.id).get()
                        #
                        # BUG f already used can not be used in with statement
                        #
                        with open(dest + "/" + file.name, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            downloads.append(file)
                files_dict = self.update_dict(downloads)
                return files_dict
            else:
                results = [item for item in self.client.search().query(target)]
                if not any(result.name == target for result in results):
                    Console.error("Source file not found.")
                else:
                    file_id = get_id(target, results, 'file')
                    if file_id:
                        file = self.client.file(file_id).get()
                        with open(dest + "/" + file.name, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            files_dict = self.update_dict(file)
                            return files_dict
        except Exception as e:
            Console.error(e)

    def search(self, service='box', directory=None, filename=None,
               recursive=False):
        """

        searches directory for file, if recursive searches all subdirectories
        :param directory: cloud directory to search in
        :param filename: name of file to search for
        :param recursive: if true search all child directories of original directory
        :return: file dict(s) matching filename in specified directory


        """
        try:
            path = directory.split('/')
            results = []
            if path[len(path) - 1] == '':
                folder_id = '0'
            else:
                items = self.client.search().query(path[len(path) - 1],
                                                   type='folder')
                folder_id = get_id(path[len(path) - 1], items, 'folder')
                if not folder_id:
                    Console.error("Directory not found.")
            files = [item for item in
                     self.client.search().query(filename, type='file',
                                                ancestor_folder_ids=folder_id)]
            if not recursive:
                for file in files:
                    if file.parent.name == path[len(path) - 1]:
                        results.append(file)
                if len(results) > 0:
                    files_dict = self.update_dict(results)
                    return files_dict
                else:
                    Console.error("No files found.")
            else:
                if len(files) > 0:
                    files_dict = self.update_dict(files)
                    return files_dict
                else:
                    Console.error("No files found.")
        except Exception as e:
            Console.error(e)

    def create_dir(self, service='box', directory=None):
        """

        creates a new directory
        :param directory: path for new directory
        :return: dict of new directory


        """
        try:
            path = directory.split('/')
            if len(path) == 1:
                Console.error('Invalid path specified.')
            else:
                parent = path[len(path) - 2]
                if parent == '':
                    folder = self.client.folder('0').create_subfolder(
                        path[len(path) - 1])
                    folder_dict = self.update_dict(folder)
                    return folder_dict
                folders = [item for item in
                           self.client.search().query(parent, type='folder')]
                if len(folders) > 0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(
                        path[len(path) - 1])
                    folder_dict = self.update_dict(folder)
                    return folder_dict
                else:
                    Console.error("Destination directory not found")
        except Exception as e:
            Console.error(e)

    def list(self, service='box', source=None, recursive=False):
        """

        lists all contents of directory, if recursive lists contents of subdirectories as well
        :param directory: cloud directory to list all contents of
        :param recursive: if true list contents of all child directories
        :return: dict(s) of files and directories


        """
        try:
            #
            # big bug variables can not be named list
            #
            list = []
            path = source.split('/')
            for i in range(1, len(path) + 1):
                if path[len(path) - i] == '':
                    if len(path) - i > 1:
                        pass
                    else:
                        items = self.client.folder('0').get_items()
                        contents = [item for item in items]
                        for c in contents:
                            list.append(c)
                else:
                    folders = [item for item in
                               self.client.search().query(path[len(path) - i],
                                                          type='folder')]
                    folder_id = get_id(path[len(path) - i], folders, 'folder')
                    if folder_id:
                        results = self.client.folder(folder_id).get_items()
                        contents = [result for result in results]
                        for c in contents:
                            list.append(c)
                    else:
                        Console.error(
                            "Directory " + path[len(path) - i] + " not found.")
                if not recursive and i == 1:
                    list_dict = self.update_dict(list)
                    return list_dict
            list_dict = self.update_dict(list)
            return list_dict
        except Exception as e:
            Console.error(e)

    def delete(self, service='box', source=None):
        """

        deletes file or directory
        :param source: file or directory to be deleted
        :return: None


        """
        try:
            path = source.strip('/').split('/')
            name = path[len(path) - 1]
            items = self.client.search().query(name, type='file')
            files = [item for item in items]
            items2 = self.client.search().query(name, type='folder')
            folders = [item2 for item2 in items2]
            results = files + folders
            if not any(result.name == name for result in results):
                Console.error("Source not found.")
            else:
                item_ind = next(
                    (index for (index, result) in enumerate(results) if
                     (result.name == name)), None)
                item_id = results[item_ind].id
                item_type = results[item_ind].type
                if item_type == 'folder':
                    self.client.folder(item_id).delete()
                elif item_type == 'file':
                    self.client.file(item_id).delete()
        except Exception as e:
            Console.error(e)
