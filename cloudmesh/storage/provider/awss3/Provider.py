import boto3
import botocore
from cloudmesh.management.configuration.config import Config
import os, stat
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import HEADING
from pprint import pprint
from cloudmesh.abstractclass.StorageABC import StorageABC


class Provider(StorageABC):

    def __init__(self, cloud=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super().__init__(cloud=cloud, config=config)
        self.container_name = self.credentials['container']
        self.s3_resource = boto3.resource('s3',
                                    aws_access_key_id=self.credentials['access_key_id'],
                                    aws_secret_access_key=self.credentials['secret_access_key'],
                                    region_name=self.credentials['region']
                                    )
        self.s3_client = boto3.client('s3',
                                    aws_access_key_id=self.credentials['access_key_id'],
                                    aws_secret_access_key=self.credentials['secret_access_key'],
                                    region_name=self.credentials['region']
                                )
        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    # function to massage file path and do some transformations
    # for different scenarios of file inputs
    def massage_path(self, fileNamePath):
        massaged_path = fileNamePath

        # remove leading slash symbol in path
        if (len(massaged_path) > 0 and massaged_path[0] == '/'):
            massaged_path = massaged_path[1:]

        # expand home directory in path
        massaged_path = massaged_path.replace('~', os.path.expanduser('~'))

        # expand possible current directory reference in path
        if massaged_path[0:2] == '.\\' or massaged_path[0:2] == './':
            massaged_path = os.path.abspath(massaged_path)

        # convert possible windows style path to unix path
        massaged_path = massaged_path.replace('\\', '/')

        return massaged_path

    # Function to join file name dir to get full file path
    def joinFileNameDir(self, fileName, dirName):
        fullFilePath = ''
        if (len(self.massage_path(dirName)) > 0):
            #fullFilePath = self.massage_path(dirName) + '/' + self.massage_path(fileName)
            fullFilePath = self.massage_path(dirName) + '/' + self.massage_path(fileName)
        else:
            fullFilePath = self.massage_path(fileName)
        return fullFilePath

    '''
    # Function to split string to list based on delimiter
    def splitToList(self, string):
        delimter = '/'
        return string.split(delimter)
    '''

    # function to create a directory
    def create_dir(self, service=None, directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        HEADING()
        fileContent = ""
        #filePath = self.joinFileNameDir(self.directory_marker_file_name, directory)
        #filePath = self.massage_path(directory) + '/' + self.directory_marker_file_name
        filePath = self.massage_path(directory)

        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'create_dir'
        self.storage_dict['directory'] = directory

        #obj = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
        obj = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=filePath+'/'))

        if len(obj) == 0:
            #markerObject = self.s3_resource.Object(self.container_name, filePath).put(Body=fileContent)
            markerObject = self.s3_resource.Object(
                self.container_name, self.massage_path(directory) + '/' + self.directory_marker_file_name
            ).put(Body=fileContent)
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
        HEADING()
        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'list'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        objs = list(self.s3_resource.Bucket(self.container_name).objects.all())

        dirFilesList = []
        trimmedSource = self.massage_path(source)

        if recursive == False:
            # call will not be recursive and need to look only in the specified directory
            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmedSource)):
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
                        if len(fileName.replace(trimmedSource, '')) == 0:
                            dirFilesList.append(fileName)
                        elif (fileName.replace(trimmedSource, '')[0] == '/' and fileName.replace(trimmedSource, '').count(
                                '/') == 1):
                            dirFilesList.append(fileName)
                        elif (fileName.replace(trimmedSource, '')[0] != '/' and fileName.replace(trimmedSource,
                                                                                                 '').count('/') == 0):
                            dirFilesList.append(fileName)
                    # print(fileName)
        else:
            # call will be recursive and need to look recursively in the specified directory as well
            for obj in objs:
                if obj.key.startswith(self.massage_path(trimmedSource)):
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
        HEADING()
        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'delete'
        self.storage_dict['source'] = source
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.massage_path(source)

        dirFilesList = []
        fileObj = ''

        try:
            fileObj = self.s3_client.get_object(Bucket=self.container_name, Key=trimmedSource)
        except botocore.exceptions.ClientError as e:
            # object not found
            x=1

        if fileObj:
            # Its a file and can be deleted
            self.s3_resource.Object(self.container_name, trimmedSource).delete()
            #print('File deleted')
            self.storage_dict['message'] = 'Source Deleted'

        else:
            # Search for a directory
            allObjs = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource))

            total_allObjs = len(allObjs)

            if total_allObjs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_allObjs > 0 and recursive is True:
                for obj in allObjs:
                    #if obj.key.startswith(self.massage_path(trimmedSource)):
                    self.s3_resource.Object(self.container_name, obj.key).delete()
                    dirFilesList.append(obj.key)

                self.storage_dict['message'] = 'Source Deleted'

            elif total_allObjs > 0 and recursive is False:
                # check if marker file exits in this directory
                marker_obj_list = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource+'/'+self.directory_marker_file_name))
                marker_exits = False
                if len(marker_obj_list) == 1:
                    marker_exits = True

                if marker_exits is True and total_allObjs == 1:
                    self.s3_resource.Object(self.container_name, trimmedSource+'/'+self.directory_marker_file_name).delete()
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
        HEADING()
        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'put'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.massage_path(source)
        trimmedDestination = self.massage_path(destination)

        isSourceFile = os.path.isfile(trimmedSource)
        isSourceDir = os.path.isdir(trimmedSource)

        if isSourceFile is True:
            #print('file flow')
            # Its a file and need to be uploaded to the destination
            self.s3_client.upload_file(trimmedSource, self.container_name, trimmedDestination)
            self.storage_dict['message'] = 'Source uploaded'
        elif isSourceDir is True:
            # Look if its a directory
            #print('dir flow')
            filesUploaded = []
            if recursive is False:
                # get files in the directory and upload to destination dir
                dirfiles = next(os.walk(trimmedSource))[2]

                for file in dirfiles:
                    self.s3_client.upload_file(trimmedSource+'/'+file,
                                              self.container_name,
                                              trimmedDestination+'/'+file)
                    filesUploaded.append(trimmedDestination+'/'+file)
            else:
                # get the directories with in the folder as well and upload
                filesToUpload = []
                for (dirpath, dirnames, filenames) in os.walk(trimmedSource):
                    for fileName in filenames:
                        #print(self.massage_path(dirpath)+'/'+fileName)
                        filesToUpload.append(self.massage_path(dirpath)+'/'+fileName)


                for file in filesToUpload:
                    self.s3_client.upload_file(file,
                                              self.container_name,
                                              trimmedDestination+'/'+self.massage_path(file.replace(trimmedSource,'')))
                    filesUploaded.append(trimmedDestination+'/'+self.massage_path(file.replace(trimmedSource,'')))



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
        HEADING()
        self.storage_dict['service'] = service
        self.storage_dict['action'] = 'get'
        self.storage_dict['source'] = source
        self.storage_dict['destination'] = destination
        self.storage_dict['recursive'] = recursive

        trimmedSource = self.massage_path(source)
        trimmedDestination = self.massage_path(destination)

        fileObj = ''

        try:
            fileObj = self.s3_client.get_object(Bucket=self.container_name, Key=trimmedSource)
            print(fileObj)
        except botocore.exceptions.ClientError as e:
            # object not found
            x = 1

        if fileObj:
            # Its a file and can be downloaded
            # print('downloading file..')
            # print(os.path.basename(trimmedSource))
            try:
                blob = self.s3_resource.Bucket(self.container_name).download_file(
                    trimmedSource, trimmedDestination)
                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                # print('File downloaded')
                self.storage_dict['message'] = 'Source downloaded'
            except FileNotFoundError as e:
                self.storage_dict['message'] = 'Destination not found'

        else:
            # Search for a directory
            allObjs = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=trimmedSource))

            total_allObjs = len(allObjs)

            # print('total_allObjs : '+str(total_allObjs))

            if total_allObjs == 0:
                self.storage_dict['message'] = 'Source Not Found'

            elif total_allObjs > 0 and recursive is False:
                # print('directory found and recursive is false')
                filesDownloaded = []
                for obj in allObjs:
                    if os.path.basename(obj.key) != self.directory_marker_file_name:
                        if self.massage_path(obj.key.replace(trimmedSource, '')).count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(self.container_name).download_file(
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
                        if self.massage_path(obj.key.replace(trimmedSource, '')).count('/') == 0:
                            try:
                                blob = self.s3_resource.Bucket(self.container_name).download_file(
                                    obj.key, trimmedDestination + '/' + os.path.basename(obj.key))
                                # trimmedSource, trimmedDestination + '/' + os.path.basename(trimmedSource))
                                # print('File downloaded')
                                self.storage_dict['message'] = 'Source downloaded'
                                filesDownloaded.append(obj.key)
                            except FileNotFoundError as e:
                                self.storage_dict['message'] = 'Destination not found'
                        else:

                            folderPath = self.massage_path(
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
                                blob = self.s3_resource.Bucket(self.container_name).download_file(
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
        HEADING()
        self.storage_dict['service'] = service
        self.storage_dict['search'] = 'search'
        self.storage_dict['directory'] = directory
        self.storage_dict['filename'] = filename
        self.storage_dict['recursive'] = recursive

        #filePath = self.joinFileNameDir(filename, directory)
        filePath = self.massage_path(directory) + '/' + filename

        obj = []
        #print(filePath)
        infoList = []

        if(len(directory) > 0) and recursive is False:
            objs = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
        elif(len(directory) == 0) and recursive is False:
            objs = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=filePath))
            #objs = list(self.s3_resource.Bucket(self.container_name).objects.all())
        elif(len(directory) > 0) and recursive is True:
            objs = list(self.s3_resource.Bucket(self.container_name).objects.filter(Prefix=self.massage_path(directory)))
        elif(len(directory) == 0) and recursive is True:
            objs = list(self.s3_resource.Bucket(self.container_name).objects.all())


        if len(objs) > 0:
            for obj in objs:
                #if self.splitToList(obj.key)[-1] == filename:
                if os.path.basename(obj.key) == filename:
                    #print(obj.key)
                    metadata = self.s3_client.head_object(Bucket=self.container_name, Key=obj.key)
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
        else:
            self.storage_dict['message'] = 'File found'

        print(self.storage_dict['infoList'])
        return self.storage_dict

