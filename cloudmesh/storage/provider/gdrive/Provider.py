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
        self.generate_key_json()
        self.authInst = Authentication(self.scopes,
                                       self.clientSecretFile,
                                       self.applicationName)
        self.credentials = self.authInst.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.driveService = self.discovery.build('drive', 'v3', http=self.http)

    def generate_key_json(self):
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
            if os.path.isdir(source):
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=query_params,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        self.upload_file(source=source, filename=f,
                                         parent_it=file_parent_id)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=query_params,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                self.upload_file(source=None, filename=source,
                                 parent_it=file_parent_id)
        else:
            if (os.path.isdir(source)):
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=query_params,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        self.upload_file(source=source, filename=f,
                                         parent_it=file_parent_id)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(q=query_params,
                                                          fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if (len(sourceid['files']) == 0):
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                self.upload_file(source=None, filename=source,
                                 parent_it=file_parent_id)

    def get(self, service=None, source=None, destination=None, recursive=False):
        if not os.path.exists(source):
            os.makedirs(source)

        if recursive:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(q=query_params,
                                                      fields="nextPageToken, files(id, name, mimeType)").execute()
            print(sourceid)
            file_id = sourceid['files'][0]['id']
            file_name = sourceid['files'][0]['name']
            mime_type = sourceid['files'][0]['mimeType']
            if mime_type == 'application/vnd.google-apps.folder':
                items = self.list(source=destination, recursive=False)
                for item in items:
                    if (item[
                        'mimeType'] != 'application/vnd.google-apps.folder'):
                        print("dbsakjdjksa")
                        print(item['mimeType'])
                        self.download(source, item['id'], item['name'],
                                      item['mimeType'])
            else:
                self.download(source, file_id, file_name, mime_type)
        else:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(q=query_params,
                                                      fields="nextPageToken, files(id, name, mimeType)").execute()
            print(sourceid)
            file_id = sourceid['files'][0]['id']
            file_name = sourceid['files'][0]['name']
            mime_type = sourceid['files'][0]['mimeType']
            if mime_type == 'application/vnd.google-apps.folder':
                items = self.list(source=destination, recursive=False)
                for item in items:
                    if (item[
                        'mimeType'] != 'application/vnd.google-apps.folder'):
                        print("dbsakjdjksa")
                        print(item['mimeType'])
                        self.download_file(source, item['id'], item['name'],
                                           item['mimeType'])
            else:
                self.download_file(source, file_id, file_name, mime_type)

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
            #
            # BUG MUST ALSO BE SET IN INIT MAYBE TO 10000000, ISSUE IS LIST SHOULD PROBBALY GIVE ALL
            #
            self.size = size
            results = self.driveService.files().list(pageSize=size,
                                                     fields="nextPageToken, files(id, name,mimeType)").execute()
            items = results.get('files', [])
            if not items:
                print('No files found.')
            else:
                return items
        else:
            query_params = "name='" + source + "' and trashed=false"
            sourceid = self.driveService.files().list(q=query_params,
                                                      pageSize=size,
                                                      fields="nextPageToken, files(id)").execute()
            file_id = sourceid['files'][0]['id']
            query_params = "'" + file_id + "' in parents"
            results = self.driveService.files().list(q=query_params,
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
            list_of_files = self.list(recursive=True)
            print(list_of_files)
            for file in list_of_files:
                print(file)
                if (file['name'] == filename):
                    found = True
                    break
                else:
                    continue
            return found
        else:
            found = False
            list_of_files = self.list(source=directory, recursive=False)
            print(list_of_files)
            for file in list_of_files:
                print(file)
                if (file['name'] == filename):
                    found = True
                    break
                else:
                    continue
            return found

    def upload_file(self, source, filename, parent_it):
        file_metadata = {'name': filename, 'parents': [parent_it]}
        self.driveService = self.driveService
        if (source is None):
            filepath = filename
        else:
            filepath = source + '/' + filename
        media = MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0])
        file = self.driveService.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()

    def download_file(self, source, file_id, file_name, mime_type):
        filepath = source + '/' + file_name + mimetypes.guess_extension(mime_type)
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
