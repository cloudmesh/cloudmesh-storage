from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.console import Console
import os


def get_id(source, results, type):
    if not any((result.name == source and result.type == type) for result in results):
        return False
    else:
        ind = next((index for (index, result) in enumerate(results) if (result.name == source)), None)
        id = results[ind].id
        return id


class Provider(object):

    def __init__(self):
        self.config = Config()
        credentials = self.config.credentials("storage", "box")
        self.sdk = JWTAuth.from_settings_file(credentials['config_path'])
        self.client = Client(self.sdk)

    def put(self, source, destination, recursive=False):
        """

        :param source: local file or directory to be uploaded
        :param destination: cloud directory to upload to
        :param recursive: if true upload all files in source directory, source must be directory not file
        :return: file dict(s) that have been uploaded


        """
        try:
            destpath = destination.split('/')
            dest = destpath[len(destpath)-1]
            sourcepath = source.strip('/').split('/')
            if os.path.isfile(source):
                filename = sourcepath[len(sourcepath)-1]
                if recursive:
                    Console.error("Invalid option recursive for source type.")
                    return
            uploaded = []
            if dest == '':
                files = [item for item in self.client.folder('0').get_items()]
            else:
                items = self.client.search().query(dest, type='folder')
                folders = [item for item in items]
                folder_id = get_id(dest, folders, 'folder')
                if folder_id:
                    files = [item for item in self.client.folder(folder_id).get_items()]
                else:
                    Console.error("Destination directory not found")
                    return
            if not recursive:
                file_id = get_id(filename, files, 'file')
                if not file_id:
                    file = self.client.folder('0').upload(source)
                    return file.__dict__
                else:
                    file = self.client.file(file_id).update_contents(source)
                    return file.__dict__
            else:
                for s in os.listdir(source):
                    s_id = get_id(s, files, 'file')
                    if not s_id:
                        file = self.client.folder('0').upload(source+'/'+s)
                        uploaded.append(file)
                    else:
                        file = self.client.file(s_id).update_contents(source+'/'+s)
                        uploaded.append(file)
                return uploaded
        except Exception as e:
            Console.error(e)

    def get(self, source, destination, recursive=False):
        """

        :param source: cloud file or directory to download
        :param destination: local directory to be downloaded into
        :param recursive: if true download all files in source directory, source must be directory
        :return: file dict(s) that have been downloaded


        """
        try:
            boxpath = source.split('/')
            target = boxpath[len(boxpath)-1]
            downloads = []
            if recursive:
                if target == '':
                    files = [item for item in self.client.folder('0').get_items()]
                else:
                    results = [item for item in self.client.search().query(target)]
                    folder_id = get_id(target, results, 'folder')
                    if folder_id:
                        files = [item for item in self.client.folder(folder_id).get_items()]
                    else:
                        Console.error("Source directory not found.")
                        return
                for f in files:
                    if f.type == 'file':
                        file = self.client.file(f.id).get()
                        with open(destination + "/" + file.name, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            downloads.append(file)
                return downloads
            else:
                results = [item for item in self.client.search().query(target)]
                if not any(result.name == target for result in results):
                    Console.error("Source file not found.")
                else:
                    file_id = get_id(target, results, 'file')
                    if file_id:
                        file = self.client.file(file_id).get()
                        with open(destination + "/" + file.name, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            return file.__dict__
        except Exception as e:
            Console.error(e)

    def search(self, directory, filename, recursive=False):
        """

        :param directory: cloud directory to search in
        :param filename: name of file to search for
        :param recursive: if true search all child directories of original directory
        :return: file dict(s) matching filename in specified directory


        """
        try:
            path = directory.split('/')
            results = []
            if path[len(path)-1] == '':
                folder_id = '0'
            else:
                items = self.client.search().query(path[len(path)-1], type='folder')
                folder_id = get_id(path[len(path)-1], items, 'folder')
                if not folder_id:
                    Console.error("Directory not found.")
                    return
            files = [item for item in self.client.search().query(filename, type='file', ancestor_folder_ids=folder_id)]
            if not recursive:
                for file in files:
                    if file.parent.name == path[len(path)-1]:
                        results.append(file)
                if len(results) > 0:
                    return results
                else:
                    Console.error("No files found.")
                    return
            else:
                if len(files) > 0:
                    return files
                else:
                    Console.error("No files found.")
                    return
        except Exception as e:
            Console.error(e)

    def create_dir(self, directory):
        """

        :param directory: directory in which to create a new directory
        :return: dict of new directory


        """
        try:
            path = directory.strip('/').split('/')
            if len(path) == 1:
                folder = self.client.folder('0').create_subfolder(path[0])
                return folder.__dict__
            else:
                parent = path[len(path) - 2]
                folders = [item for item in self.client.search().query(parent, type='folder')]
                if len(folders) > 0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(path[len(path)-1])
                    return folder.__dict__
                else:
                    Console.error("Destination directory not found")
        except Exception as e:
            Console.error(e)

    def list(self, directory, recursive=False):
        """

        :param directory: cloud directory to list all contents of
        :param recursive: if true list contents of all child directories
        :return: dict(s) of files and directories


        """
        try:
            list = []
            path = directory.split('/')
            for i in range(1, len(path)+1):
                if path[len(path)-i] == '':
                    if len(path) - i > 1:
                        pass
                    else:
                        items = self.client.folder('0').get_items()
                        contents = [item for item in items]
                        for c in contents:
                            list.append(c)
                else:
                    folders = [item for item in self.client.search().query(path[len(path)-i], type='folder')]
                    folder_id = get_id(path[len(path)-i], folders, 'folder')
                    if folder_id:
                        results = self.client.folder(folder_id).get_items()
                        contents = [result for result in results]
                        for c in contents:
                            list.append(c)
                    else:
                        Console.error("Directory " + path[len(path) - i] + " not found.")
                if not recursive and i == 1:
                    return list
            return list
        except Exception as e:
            Console.error(e)

    def delete(self, source):
        """

        :param source: file or directory to be deleted
        :return: null


        """
        try:
            path = source.strip('/').split('/')
            name = path[len(path)-1]
            items = self.client.search().query(name)
            results = [item for item in items]
            if not any(result.name == name for result in results):
                Console.error("Source not found")
            else:
                item_ind = next((index for (index, result) in enumerate(results) if (result.name == name)), None)
                item_id = results[item_ind].id
                item_type = results[item_ind].type
                if item_type == 'folder':
                    print(self.client.folder(item_id).delete())
                elif item_type == 'file':
                    print(self.client.file(item_id).delete())
        except Exception as e:
            Console.error(e)

    def entries(self, name):
        return {
            "name": name,
            "cloud": "box",
            "kind": "storage",
            "driver": "box",
            "collection": "box-storage"
        }
