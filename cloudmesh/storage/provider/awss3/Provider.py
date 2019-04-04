import boto3
import botocore
from cloudmesh.management.configuration.config import Config
import os, stat
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.docdict import docdict
from pathlib import Path
from os.path import dirname, basename

class Provider(object):

    # BUG do not use camel case

    def __init__(self, name=None):
        if name is None:
            raise ValueError("service name not specified")
        config = Config()
        credentials = config['cloudmesh']['storage'][name]['credentials']
        self.container_name = config['cloudmesh.storage.aws.credentials.container']

        self.s3Resource = boto3.resource(
            's3',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_credentils.key=credentials.secret_access_key,
            region_name=credentials.region
        )

        self.s3Client = boto3.client(
            's3',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            region_name=credentials.region
        )

        # Q: what is maker.txt?
        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    def update_dict(self, dictionary, name=None):
        # BUG todo values are comming from self. as defined from init
        d = dictionary
        c["cm"] ={
            "kind": self.kind,
            "name": name,
            "cloud": self.cloud,
            "updated": "todo",
            "created": "todo"
        }
        return d

    # function trim s3 filename

    # BUG, use dirname, basename, Path
    def trimFileNamePath(self, fileNamePath):
        trimmedFileNamePath = ''
        if (len(fileNamePath) > 0 and fileNamePath.strip()[0] == '/'):
            trimmedFileNamePath = fileNamePath.strip()[1:].replace('\\', '/')
        else:
            trimmedFileNamePath = fileNamePath.strip().replace('\\', '/')
        return trimmedFileNamePath

    # Function to join file name dir to get full file path
    # BUG use Path
    def joinFileNameDir(self, fileName, dirName):
        fullFilePath = ''
        if (len(self.trimFileNamePath(dirName)) > 0):
            fullFilePath = self.trimFileNamePath(dirName) + '/' + self.trimFileNamePath(fileName)
        else:
            fullFilePath = self.trimFileNamePath(fileName)
        return fullFilePath

    # Function to split string to list based on delimiter
    def splitToList(self, string):
        delimter = '/'
        return string.split(delimter)

    # function to create a directory
    def create_dir(self, service=None, directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        fileContent = ""
        filePath = self.joinFileNameDir(self.directory_marker_file_name, directory)

        # BUG upadte_dir missing
        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'create_dir'
        self.storage_dict['directory'] = directory

        obj = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=filePath))

        if len(obj) == 0:
            markerObject = self.s3Resource.Object(self.container_name, filePath).put(Body=fileContent)
            #print('Directory created')
            #print(markerObject)
            self.storage_dict['message'] = 'Directory created'
        else:
            #print('Directory already present')
            self.storage_dict['message'] = 'Directory already present'

        print(self.storage_dict['message'])
        return self.storage_dict

        # function to list file  or directory

    def list(self, service=None, source=None, recursive=False):
        """
        lists the information as dict

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict
        """
        # BUG upadte_dir missing

        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'list'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        objs = list(self.s3Resource.Bucket(self.container_name).objects.all())

        dirFilesList = []
        trimmedSource = self.trimFileNamePath(source)

        if recursive == False:
            # call will not be recursive and need to look only in the specified directory
            for obj in objs:
                if obj.key.startswith(self.trimFileNamePath(trimmedSource)):
                    # print(obj.key)
                    fileName = obj.key.replace(self.directory_marker_file_name, '')
                    if (fileName[-1] == '/'):
                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            dirFilesList.append(fileName)
                        '''
                        x = 1
                    else:
                        # Its a file
                        if (fileName.replace(trimmedSource, '')[0] == '/' and fileName.replace(trimmedSource, '').count(
                                '/') == 1):
                            dirFilesList.append(fileName)
                        elif (fileName.replace(trimmedSource, '')[0] != '/' and fileName.replace(trimmedSource,
                                                                                                 '').count('/') == 0):
                            dirFilesList.append(fileName)
                    # print(fileName)
        else:
            # call will be recursive and need to look recursively in the specified directory as well
            for obj in objs:
                if obj.key.startswith(self.trimFileNamePath(trimmedSource)):
                    # print(obj.key)
                    fileName = obj.key.replace(self.directory_marker_file_name, '')
                    if (fileName[-1] == '/'):
                        # Its a directory
                        '''
                        if (fileName.replace(trimmedSource,'').count('/') == 1):
                            dirFilesList.append(fileName)
                        '''
                        x = 1
                    else:
                        # its a file
                        dirFilesList.append(fileName)
                    # print(fileName)
        '''
        if len(dirFilesList) == 0:
            #print("No files found in directory")
            self.storage_dict['message'] = ''
        else:
            self.storage_dict['message'] = dirFilesList
        '''

        self.storage_dict['message'] = dirFilesList
        print(self.storage_dict['message'])
        return self.storage_dict

    # function to delete file or directory
    def delete(self, service=None, source=None, recursive=False):
        """
        deletes the source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source

        :return: dict
        """
        # BUG upadte_dir missing

        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'delete'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.trimFileNamePath(source)

        dirFilesList = []
        fileObj = ''

        try:
            fileObj = self.s3Client.get_object(Bucket=self.container_name, Key=trimmedSource)
        except botocore.exceptions.ClientError as e:
            # object not found
            x=1

        if fileObj:
            # Its a file and can be deleted
            self.s3Resource.Object(self.container_name, trimmedSource).delete()
            #print('File deleted')
            self.storage_dict['message'] = 'Source Deleted'

        else:
            # Search for a directory
            allObjs = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource))

            total_allObjs = len(allObjs)

            if total_allObjs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_allObjs > 0 and recursive is True:
                for obj in allObjs:
                    #if obj.key.startswith(self.trimFileNamePath(trimmedSource)):
                    self.s3Resource.Object(self.container_name, obj.key).delete()
                    dirFilesList.append(obj.key)

                self.storage_dict['message'] = 'Source Deleted'

            elif total_allObjs > 0 and recursive is False:
                # check if marker file exits in this directory
                marker_obj_list = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource+'/'+self.directory_marker_file_name))
                marker_exits = False
                if len(marker_obj_list) == 1:
                    marker_exits = True

                if marker_exits is True and total_allObjs == 1:
                    self.s3Resource.Object(self.container_name, trimmedSource+'/'+self.directory_marker_file_name).delete()
                    self.storage_dict['message'] = 'Source Deleted'
                else:
                    self.storage_dict['message'] = 'Source has child objects. Use recursive option'
        print(self.storage_dict['message'])
        return self.storage_dict


    # function to upload file or directory
    def put(self, service=None, source=None, destination=None, recursive=False):
        """
        puts the source on the service

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source

        :return: dict
        """
        # BUG upadte_dir missing

        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'put'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.trimFileNamePath(source)
        trimmedDestination = self.trimFileNamePath(destination)

        isSourceFile = os.path.isfile(trimmedSource)
        isSourceDir = os.path.isdir(trimmedSource)

        if isSourceFile is True:
            #print('file flow')
            # Its a file and need to be uploaded to the destination
            self.s3Client.upload_file(trimmedSource, self.container_name, trimmedDestination)
            self.storage_dict['message'] = 'Source uploaded'
        elif isSourceDir is True:
            # Look if its a directory
            #print('dir flow')
            filesUploaded = []
            if recursive is False:
                # get files in the directory and upload to destination dir
                dirfiles = next(os.walk(trimmedSource))[2]

                for file in dirfiles:
                    self.s3Client.upload_file(trimmedSource+'/'+file,
                                              self.container_name,
                                              trimmedDestination+'/'+file)
                    filesUploaded.append(trimmedDestination+'/'+file)
            else:
                # get the directories with in the folder as well and upload
                filesToUpload = []
                for (dirpath, dirnames, filenames) in os.walk(trimmedSource):
                    for fileName in filenames:
                        #print(self.trimFileNamePath(dirpath)+'/'+fileName)
                        filesToUpload.append(self.trimFileNamePath(dirpath)+'/'+fileName)


                for file in filesToUpload:
                    self.s3Client.upload_file(file,
                                              self.container_name,
                                              trimmedDestination+'/'+self.trimFileNamePath(file.replace(trimmedSource,'')))
                    filesUploaded.append(trimmedDestination+'/'+self.trimFileNamePath(file.replace(trimmedSource,'')))



            self.storage_dict['filesUploaded'] = filesUploaded
            self.storage_dict['message'] = 'Source uploaded'

        else:
            self.storage_dict['message'] = 'Source not found'

        print(self.storage_dict['message'])
        return self.storage_dict

        # function to download file or directory

    def get(self, service=None, source=None, destination=None, recursive=False):
        """
       gets the source from the service

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source

        :return: dict
        """
        # BUG upadte_dir missing

        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'get'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.trimFileNamePath(source)
        trimmedDestination = self.trimFileNamePath(destination)

        fileObj = ''

        try:
            fileObj = self.s3Client.get_object(Bucket=self.container_name, Key=trimmedSource)
            print(fileObj)
        except botocore.exceptions.ClientError as e:
            # object not found
            x = 1

        if fileObj:
            # Its a file and can be downloaded
            # print('downloading file..')
            # print(os.path.basename(trimmedSource))
            try:
                blob = self.s3Resource.Bucket(self.container_name).download_file(
                    trimmedSource, trimmedDestination)
                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                # print('File downloaded')
                self.storage_dict['message'] = 'Source downloaded'
            except FileNotFoundError as e:
                self.storage_dict['message'] = 'Destination not found'

        else:
            # Search for a directory
            allObjs = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource))

            total_allObjs = len(allObjs)

            # print('total_allObjs : '+str(total_allObjs))

            if total_allObjs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_allObjs > 0 and recursive is False:
                # print('directory found and recursive is false')
                filesDownloaded = []
                for obj in allObjs:
                    if os.path.basename(obj.key) != self.directory_marker_file_name:
                        if self.trimFileNamePath(obj.key.replace(trimmedSource, '')).count('/') == 0:
                            try:
                                blob = self.s3Resource.Bucket(self.container_name).download_file(
                                    obj.key, trimmedDestination + '/' + os.path.basename(obj.key))
                                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                                # print('File downloaded')
                                self.storage_dict['message'] = 'Source downloaded'
                                filesDownloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict['message'] = 'Destination not found'

                self.storage_dict['filesDownloaded'] = filesDownloaded

            elif total_allObjs > 0 and recursive is True:
                # print('directory found and recursive is True')
                filesDownloaded = []
                for obj in allObjs:
                    #print(obj.key)
                    if os.path.basename(obj.key) != self.directory_marker_file_name and obj.key[-1] != '/':
                        if self.trimFileNamePath(obj.key.replace(trimmedSource, '')).count('/') == 0:
                            try:
                                blob = self.s3Resource.Bucket(self.container_name).download_file(
                                    obj.key, trimmedDestination + '/' + os.path.basename(obj.key))
                                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                                # print('File downloaded')
                                self.storage_dict['message'] = 'Source downloaded'
                                filesDownloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict['message'] = 'Destination not found'
                        else:

                            folderPath = self.trimFileNamePath(
                                obj.key.replace(trimmedSource, '').replace(os.path.basename(obj.key), '')
                            )
                            # print('folderPath  : '+folderPath)
                            try:
                                os.makedirs(trimmedDestination + '/' + folderPath, 0o777)
                                # os.chmod(trimmedDestination+'/'+folderPath, stat.S_IRWXO)
                                x = 1
                            except FileExistsError as e:
                                # print('Error :')
                                # print(e)
                                os.chmod(trimmedDestination + '/' + folderPath, stat.S_IRWXO)
                                x = 1

                            try:
                                blob = self.s3Resource.Bucket(self.container_name).download_file(
                                    # obj.key, trimmedDestination + '/' + os.path.basename(obj.key))
                                    obj.key, trimmedDestination + '/' + folderPath + os.path.basename(obj.key))
                                # print('File downloaded')
                                self.storage_dict['message'] = 'Source downloaded'
                                filesDownloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict['message'] = 'Destination not found'

                self.storage_dict['filesDownloaded'] = filesDownloaded

        print(self.storage_dict['message'])
        return self.storage_dict

    # function to search a file or directory and list its attributes
    def search(self, service=None, directory=None, filename=None, recursive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param filename: filename
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        # BUG upadte_dir missing

        self.storage_dict['service'] = service
        self.storage_dict['search'] = 'search'
        self.storage_dict['directory'] = directory
        self.storage_dict['filename'] = filename
        self.storage_dict['recursive'] = recursive

        filePath = self.joinFileNameDir(filename, directory)

        obj = []
        print(filePath)
        infoList = []

        if(len(directory) > 0) and recursive is False:
            objs = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
        elif(len(directory) == 0) and recursive is False:
            objs = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
            #objs = list(self.s3Resource.Bucket(self.container_name).objects.all())
        elif(len(directory) > 0) and recursive is True:
            objs = list(self.s3Resource.Bucket(self.container_name).objects.filter(Prefix=self.trimFileNamePath(directory)))
        elif(len(directory) == 0) and recursive is True:
            objs = list(self.s3Resource.Bucket(self.container_name).objects.all())


        if len(objs) > 0:
            for obj in objs:
                if self.splitToList(obj.key)[-1] == filename:
                    #print(obj.key)
                    metadata = self.s3Client.head_object(Bucket=self.container_name, Key=obj.key)
                    # print(metadata)
                    info = {
                        "fileName": obj.key,
                        # "creationDate" : metadata['ResponseMetadata']['HTTPHeaders']['date'],
                        "lastModificationDate": metadata['ResponseMetadata']['HTTPHeaders']['last-modified'],
                        "contentLength": metadata['ResponseMetadata']['HTTPHeaders']['content-length']
                    }
                    #pprint(info)
                    infoList.append(info)


        self.storage_dict['infoList'] = infoList

        if len(infoList) == 0:
            self.storage_dict['message'] = 'File not found'

        #print(self.storage_dict['message'])
        return self.storage_dict





