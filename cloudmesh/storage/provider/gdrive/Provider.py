import io
import json
import mimetypes
import os

import httplib2
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.StorageABC import StorageABC
from cloudmesh.storage.provider.gdrive.Authentication import Authentication


class Provider(StorageABC):

    def __init__(self, cloud=None, config="~/.cloudmesh/cloudmesh4.yaml"):

        super(Provider, self).__init__(cloud=cloud, config=config)

        self.scopes = 'https://www.googleapis.com/auth/drive'
        self.clientSecretFile = path_expand(
            '~/.cloudmesh/gdrive/client_secret.json')
        self.applicationName = 'Drive API Python Quickstart'

        self.config = Config()
        self.generateKeyJson()
        self.authInst = Authentication(self.scopes,
                                       self.clientSecretFile,
                                       self.applicationName)
        self.credentials = self.authInst.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.driveService = self.discovery.build('drive', 'v3', http=self.http)

    def generateKeyJson(self):
        credentials = self.config.credentials("storage", "gdrive")

        data = {"installed": {
            "client_id": credentials["client_id"],
            "project_id": credentials["project_id"],
            "auth_uri": credentials["auth_uri"],
            "token_uri": credentials["token_uri"],
            "client_secret": credentials["client_secret"],
            "auth_provider_x509_cert_url": credentials[
                "auth_provider_x509_cert_url"],
            "redirect_uris": credentials["redirect_uris"]
        }
        }
        with open(self.clientSecretFile, 'w') as fp:
            json.dump(data, fp)

    def put(self, service=None, source=None, destination=None, recursive=False):
        if recursive:
            if (os.path.isdir(source)):
                queryParams = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=queryParams,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                fileParentId = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parentFile = self.create_dir(directory=destination)
                    fileParentId = parentFile['id']
                else:
                    print(sourceid['files'][0]['id'])
                    fileParentId = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        self.uploadFile(source=source, filename=f,
                                        parentId=fileParentId)
            else:
                queryParams = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=queryParams,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                fileParentId = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parentFile = self.create_dir(directory=destination)
                    fileParentId = parentFile['id']
                else:
                    print(sourceid['files'][0]['id'])
                    fileParentId = sourceid['files'][0]['id']

                self.uploadFile(source=None, filename=source,
                                parentId=fileParentId)
        else:
            if (os.path.isdir(source)):
                queryParams = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=queryParams,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                fileParentId = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parentFile = self.create_dir(directory=destination)
                    fileParentId = parentFile['id']
                else:
                    print(sourceid['files'][0]['id'])
                    fileParentId = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        self.uploadFile(source=source, filename=f,
                                        parentId=fileParentId)
            else:
                queryParams = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=queryParams,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                fileParentId = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parentFile = self.create_dir(directory=destination)
                    fileParentId = parentFile['id']
                else:
                    print(sourceid['files'][0]['id'])
                    fileParentId = sourceid['files'][0]['id']

                self.uploadFile(source=None, filename=source,
                                parentId=fileParentId)

    def get(self, service=None, source=None, destination=None, recursive=False):
        if not os.path.exists(source):
            os.makedirs(source)

        if recursive:
            queryParams = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(q=queryParams,
                                                      fields="nextPageToken, files(id, name, mimeType)").execute()
            print(sourceid)
            fileId = sourceid['files'][0]['id']
            fileName = sourceid['files'][0]['name']
            mimeType = sourceid['files'][0]['mimeType']
            if mimeType == 'application/vnd.google-apps.folder':
                items = self.list(source=destination, recursive=False)
                for item in items:
                    if (item[
                        'mimeType'] != 'application/vnd.google-apps.folder'):
                        print("dbsakjdjksa")
                        print(item['mimeType'])
                        self.download(source, item['id'], item['name'],
                                      item['mimeType'])
            else:
                self.download(source, fileId, fileName, mimeType)
        else:
            queryParams = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(q=queryParams,
                                                      fields="nextPageToken, files(id, name, mimeType)").execute()
            print(sourceid)
            fileId = sourceid['files'][0]['id']
            fileName = sourceid['files'][0]['name']
            mimeType = sourceid['files'][0]['mimeType']
            if mimeType == 'application/vnd.google-apps.folder':
                items = self.list(source=destination, recursive=False)
                for item in items:
                    if (item[
                        'mimeType'] != 'application/vnd.google-apps.folder'):
                        print("dbsakjdjksa")
                        print(item['mimeType'])
                        self.downloadFile(source, item['id'], item['name'],
                                          item['mimeType'])
            else:
                self.downloadFile(source, fileId, fileName, mimeType)

    def delete(self, service='gdrive', filename=None,
               recursive=False):  # this is working
        file_id = ""
        if (recursive):
            items = Provider.list(self, recursive=True)
            for i in range(len(items)):
                if items[i]['name'] == filename:
                    file_id = items[i]['id']

            try:
                self.driveService.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                return 'An error occurred:'  # %s' % error
        else:
            items = Provider.list(self, recursive=True)
            for i in range(len(items)):
                if items[i]['name'] == filename:
                    file_id = items[i]['id']
            try:
                self.driveService.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                return 'An error occurred:'  # %s' % error

    def create_dir(self, service='gdrive', directory=None):
        file_metadata = {'name': directory,
                         'mimeType': 'application/vnd.google-apps.folder'}
        file = self.driveService.files().create(body=file_metadata,
                                                fields='id').execute()
        print('Folder ID: %s' % file.get('id'))
        return file

    def list(self, service='gdrive', source=None, recursive=False):
        size = 10
        if recursive:
            self.size = size
            results = self.driveService.files().list(pageSize=size,
                                                     fields="nextPageToken, files(id, name,mimeType)").execute()
            items = results.get('files', [])
            if not items:
                print('No files found.')
            else:
                return items
        else:
            queryParams = "name='" + source + "' and trashed=false"
            sourceid = self.driveService.files().list(q=queryParams,
                                                      pageSize=size,
                                                      fields="nextPageToken, files(id)").execute()
            fileId = sourceid['files'][0]['id']
            queryParams = "'" + fileId + "' in parents"
            results = self.driveService.files().list(q=queryParams,
                                                     pageSize=size,
                                                     fields="nextPageToken, files(id, name, mimeType)").execute()
            items = results.get('files', [])
            if not items:
                print('No files found.')
            else:
                return items

    def search(self, service='gdrive', directory=None, filename=None,
               recursive=False):
        if (recursive):
            found = False
            listOfFiles = self.list(recursive=True)
            print(listOfFiles)
            for file in listOfFiles:
                print(file)
                if (file['name'] == filename):
                    found = True
                    break
                else:
                    continue
            return found
        else:
            found = False
            listOfFiles = self.list(source=directory, recursive=False)
            print(listOfFiles)
            for file in listOfFiles:
                print(file)
                if (file['name'] == filename):
                    found = True
                    break
                else:
                    continue
            return found

    def uploadFile(self, source, filename, parentId):
        file_metadata = {'name': filename, 'parents': [parentId]}
        self.driveService = self.driveService
        if (source == None):
            filepath = filename
        else:
            filepath = source + '/' + filename
        media = MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0])
        file = self.driveService.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()

    def downloadFile(self, source, file_id, fileName, mimeType):
        filepath = source + '/' + fileName + mimetypes.guess_extension(mimeType)
        request = self.driveService.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with io.open(filepath, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
