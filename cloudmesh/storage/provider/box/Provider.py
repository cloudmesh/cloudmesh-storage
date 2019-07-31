from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from os.path import basename, join, dirname
import os
from cloudmesh.storage.StorageABC import StorageABC


def get_id(source, results, source_type):
    if not any((result.name == source and result.type == source_type) for result in
               results):
        return None
    else:
        ind = next((index for (index, result) in enumerate(results) if
                    (result.name == source)), None)
        source_id = results[ind].id
        return source_id


def change_path(source):
    src_path = path_expand(source)
    if src_path[0] not in [".", "/"]:
        src_path = os.path.join(os.getcwd(), source)
    return src_path


def update_dict(elements):
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
            "cloud": 'box',
            "name": element.name,
        }
        for c in ['modified_at', 'created_at', 'size']:
            if c in entry.keys():
                entry['cm'][c]: entry[c]
            else:
                entry['cm'][c]: None
        # TODO: They should not be deleted
        for p in ['_response_object',
                  '_session',
                  'session',
                  'response_object',
                  'created_by',
                  'file_version',
                  'modified_by',
                  'owned_by',
                  'parent',
                  'path_collection']:
            if p in entry.keys():
                del (entry[p])
        d.append(entry)
    return d


class Provider(StorageABC):

    def __init__(self,
                 service=None,
                 config="~/.cloudmesh/cloudmesh.yaml"):

        super().__init__(service=service, config=config)
        self.sdk = JWTAuth.from_settings_file(self.credentials['config_path'])
        self.client = Client(self.sdk)

    def put(self, service=None, source=None, destination=None, recursive=False):
        """
        uploads file to Box, if source is directory and recursive is true uploads all files in source directory
        :param source: local file or directory to be uploaded
        :param destination: cloud directory to upload to
        :param recursive: if true upload all files in source directory, source must be directory not file
        :return: file dict(s) that have been uploaded
        """
        try:
            dest = basename(destination)
            sourcepath = change_path(source)
            sourcebase = basename(sourcepath)
            uploaded = []
            files = []
            if dest == '':
                files += [item for item in self.client.folder('0').get_items() if item.type == 'file']
                folder_id = '0'
            else:
                items = self.client.search().query(dest, type='folder')
                folders = [item for item in items]
                folder_id = get_id(dest, folders, 'folder')
                if folder_id is not None:
                    files += [item for item in self.client.folder(folder_id).get_items() if item.type == 'file']
                else:
                    items = self.client.search().query(basename(dirname(destination)), type='folder')
                    folders = [item for item in items]
                    folder_id = get_id(dest, folders, 'folder')
                    if folder_id is not None:
                        new_folder = self.client.folder(folder_id).create_subfolder(dest)
                        folder_id = new_folder.id
                    else:
                        Console.error("Invalid destination.")
                        return
            if not recursive:
                if os.path.isfile(sourcepath):
                    filename = sourcebase
                else:
                    Console.error("Invalid source path.")
                    return
                file_id = get_id(filename, files, 'file')
                if file_id is None:
                    file = self.client.folder(folder_id).upload(sourcepath)
                    files_dict = update_dict(file)
                    return files_dict
                else:
                    file = self.client.file(file_id).update_contents(sourcepath)
                    files_dict = update_dict(file)
                    return files_dict
            else:
                folder_ids = [folder_id]
                uploads = [[s for s in os.listdir(source)]]
                while len(uploads) > 0:
                    for s in uploads[0]:
                        if os.path.isdir(s):
                            uploads += [d for d in os.listdir(s)]
                            new = self.client.folder(folder_ids[0]).create_subfolder(s)
                            folder_ids.append(new.id)
                        else:
                            s_id = get_id(s, files, 'file')
                            if s_id is None:
                                file = self.client.folder(folder_ids[0]).upload(sourcepath + '/' + s)
                                uploaded.append(file)
                            else:
                                file = self.client.file(s_id).update_contents(sourcepath + '/' + s)
                                uploaded.append(file)
                    uploads.pop(0)
                    folder_ids.pop(0)
                files_dict = update_dict(uploaded)
                return files_dict
        except Exception as e:
            Console.error(e)

    def get(self, service=None, source=None, destination=None, recursive=False):
        """
        downloads file from Box, if recursive is true and source is directory downloads all files in directory
        :param source: cloud file or directory to download
        :param destination: local directory to be downloaded into
        :param recursive: if true download all files in source directory, source must be directory
        :return: file dict(s) that have been downloaded
        """
        try:

            target = basename(source)
            dest = change_path(destination)
            downloads = []
            if recursive:
                if target == '':
                    files = [item for item in self.client.folder('0').get_items() if item.type == 'file']
                    folders = [item for item in self.client.folder('0').get_items() if item.type == 'folder']
                else:
                    results = [item for item in self.client.search().query(target, type='folder')]
                    folder_id = get_id(target, results, 'folder')
                    if folder_id:
                        files = [item for item in self.client.folder(folder_id).get_items() if item.type == 'file']
                        folders = [item for item in self.client.folder(folder_id).get_items() if item.type == 'folder']
                    else:
                        Console.error("Source directory not found.")
                        return
                while len(folders) > 0:
                    files += [item for item in self.client.folder(folders[0].id).get_items() if item.type == 'file']
                    folders += [item for item in self.client.folder(folders[0].id).get_items() if item.type == 'folder']
                    folders.pop(0)
                for f in files:
                    if f.type == 'file':
                        file = self.client.file(f.id).get()
                        full_dest = join(dest, file.name)
                        with open(full_dest, 'wb') as file_dest:
                            self.client.file(file.id).download_to(file_dest)
                            downloads.append(file)
                files_dict = update_dict(downloads)
                return files_dict
            else:
                results = [item for item in self.client.search().query(target)]
                if not any(result.name == target for result in results):
                    Console.error("Source file not found.")
                else:
                    file_id = get_id(target, results, 'file')
                    if file_id is not None:
                        file = self.client.file(file_id).get()
                        full_dest = join(dest, file.name)
                        with open(full_dest, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            files_dict = update_dict(file)
                            return files_dict
        except Exception as e:
            Console.error(e)

    def search(self, service=None, directory=None, filename=None, recursive=False):
        """
        searches directory for file, if recursive searches all subdirectories
        :param directory: cloud directory to search in
        :param filename: name of file to search for
        :param recursive: if true search all child directories of original directory
        :return: file dict(s) matching filename in specified directory
        """
        try:
            cloud_dir = basename(directory)
            results = []
            if cloud_dir == '':
                files = [item for item in self.client.folder('0').get_items() if item.type == 'file']
                folders = [item for item in self.client.folder('0').get_items() if item.type == 'folder']
            else:
                items = self.client.search().query(cloud_dir, type='folder')
                folder_id = get_id(cloud_dir, items, 'folder')
                if not folder_id:
                    Console.error("Directory not found.")
                files = [item for item in self.client.folder(folder_id).get_items() if item.type == 'file']
                folders = [item for item in self.client.folder(folder_id).get_items() if item.type == 'folder']
            for file in files:
                if filename in file.name:
                    results.append(file)
            if not recursive:
                if len(results) > 0:
                    files_dict = update_dict(results)
                    return files_dict
                else:
                    Console.error("No files found.")
            else:
                while len(folders) > 0:
                    files = [item for item in self.client.folder(folders[0].id).get_items() if item.type == 'file']
                    folders += [item for item in self.client.folder(folders[0].id).get_items() if item.type == 'folder']
                    for file in files:
                        if filename in file.name:
                            results.append(file)
                    folders.pop(0)
                if len(results) > 0:
                    files_dict = update_dict(results)
                    return files_dict
                else:
                    Console.error("No files found.")
        except Exception as e:
            Console.error(e)

    def create_dir(self, service=None, directory=None):
        """
        creates a new directory
        :param directory: path for new directory
        :return: dict of new directory
        """
        try:
            path = directory.split('/')
            new_dir = basename(directory)
            if len(path) == 1:
                Console.error('Invalid path specified.')
            else:
                parent = path[len(path) - 2]
                if parent == '':
                    folder = self.client.folder('0').create_subfolder(new_dir)
                    folder_dict = update_dict(folder)
                    return folder_dict
                folders = [item for item in self.client.search().query(parent, type='folder')]
                if len(folders) > 0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(new_dir)
                    folder_dict = update_dict(folder)
                    return folder_dict
                else:
                    Console.error("Destination directory not found")
        except Exception as e:
            Console.error(e)

    def list(self, service=None, source=None, recursive=False):
        """
        lists all contents of directory, if recursive lists contents of subdirectories as well
        :param source: cloud directory to list all contents of
        :param recursive: if true list contents of all child directories
        :return: dict(s) of files and directories
        """
        try:
            result_list = []
            subfolders = []
            path = basename(source)
            if path == '':
                contents = [item for item in self.client.folder('0').get_items()]
                for c in contents:
                    if c.type == 'folder':
                        subfolders.append(c)
                    result_list.append(c)
            else:
                folders = [item for item in self.client.search().query(path, type='folder')]
                folder_id = get_id(path, folders, 'folder')
                if folder_id:
                    contents = [result for result in self.client.folder(folder_id).get_items()]
                    for c in contents:
                        if c.type == 'folder':
                            subfolders.append(c)
                        result_list.append(c)
                else:
                    Console.error("Directory " + path + " not found.")
            if recursive:
                while len(subfolders) > 0:
                    contents = [item for item in self.client.folder(subfolders[0].id).get_items()]
                    for c in contents:
                        if c.type == 'folder':
                            subfolders.append(c)
                        result_list.append(c)
                    subfolders.pop(0)
            list_dict = update_dict(result_list)
            return list_dict
        except Exception as e:
            Console.error(e)

    def delete(self, service=None, source=None, recursive=False):
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
            deleted = []
            if not any(result.name == name for result in results):
                Console.error("Source not found.")
            else:
                item_ind = next((index for (index, result) in enumerate(results) if (result.name == name)), None)
                item_id = results[item_ind].id
                item_type = results[item_ind].type
                deleted.append(results[item_ind])
                if item_type == 'folder':
                    self.client.folder(item_id).delete()
                elif item_type == 'file':
                    self.client.file(item_id).delete()
                result_list = update_dict(deleted)
                return result_list
        except Exception as e:
            Console.error(e)
