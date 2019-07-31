import argparse
import io
import json
import mimetypes
import os
import sys
from pathlib import Path

import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.StorageABC import StorageABC
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):
        super().__init__(service=service, config=config)
        self.config = Config()
        self.storage_credentials = self.config.credentials("storage", "gdrive")
        if self.storage_credentials['maxfiles'] > 1000:
            Console.error("Page size must be smaller than 1000")
            sys.exit(1)
        self.limitFiles = self.storage_credentials['maxfiles']
        self.scopes = self.storage_credentials['scopes']
        self.clientSecretFile = path_expand(
            self.storage_credentials['location_secret'])
        self.applicationName = self.storage_credentials['application_name']
        self.generate_key_json()
        self.flags = self.generate_flags_json()
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.driveService = discovery.build('drive', 'v3', http=self.http)
        self.cloud = service
        self.service = service

        self.fields = "nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)"

    def generate_flags_json(self):
        #
        # TODO: Bug, argparse is not used, we use docopts.
        #
        args = argparse.Namespace(
            auth_host_name=self.storage_credentials["auth_host_name"],
            auth_host_port=self.storage_credentials["auth_host_port"],
            logging_level='ERROR', noauth_local_webserver=False)
        return args

    def generate_key_json(self):
        config_path = self.storage_credentials['location_secret']
        path = Path(path_expand(config_path)).resolve()
        config_folder = os.path.dirname(path)
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        data = {"installed": {
            "client_id": self.storage_credentials["client_id"],
            "project_id": self.storage_credentials["project_id"],
            "auth_uri": self.storage_credentials["auth_uri"],
            "token_uri": self.storage_credentials["token_uri"],
            "client_secret": self.storage_credentials["client_secret"],
            "auth_provider_x509_cert_url": self.storage_credentials[
                "auth_provider_x509_cert_url"],
            "redirect_uris": self.storage_credentials["redirect_uris"]
        }
        }
        with open(self.clientSecretFile, 'w') as fp:
            json.dump(data, fp)

    def get_credentials(self):

        """
            We have stored the credentials in ".credentials"
            folder and there is a file named 'google-drive-credentials.json'
            that has all the credentials required for our authentication
            If there is nothing stored in it this program creates credentials
            json file for future authentication
            Here the authentication type is OAuth2
        :return:
        :rtype:
        """
        cwd = self.storage_credentials['location_gdrive_credentials']
        path = Path(path_expand(cwd)).resolve()
        if not os.path.exists(path):
            os.makedirs(path)
        credentials_path = os.path.join(path, 'google-drive-credentials.json')
        credentials_path = Path(path_expand(credentials_path)).resolve()
        store = Storage(credentials_path)
        print(credentials_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file,
                                                  self.scopes)
            flow.user_agent = self.application_name
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)

        return credentials

    def put(self, service=None, source=None, destination=None, recursive=False):
        if recursive:
            if os.path.isdir(source):
                temp_res = []
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        temp_res.append(
                            self.upload_file(source=source, filename=f,
                                             parent_it=file_parent_id))
                return self.update_dict(tempres)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                res = self.upload_file(source=None, filename=source,
                                       parent_it=file_parent_id)
                return self.update_dict(res)
        else:
            if os.path.isdir(source):
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                temp_res = []
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        temp_res.append(
                            self.upload_file(source=source, filename=f,
                                             parent_it=file_parent_id))
                return self.update_dict(temp_res)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.driveService.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir(directory=destination)
                    file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                res = self.upload_file(source=None, filename=source,
                                       parent_it=file_parent_id)
                return self.update_dict(res)

    def get(self, service=None, source=None, destination=None, recursive=False):
        if not os.path.exists(source):
            os.makedirs(source)

        if recursive:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(
                q=query_params,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            print(sourceid)
            if len(sourceid) == 0:
                Console.error('No files found')
                sys.exit(1)
            file_id = sourceid['files'][0]['id']
            file_name = sourceid['files'][0]['name']
            mime_type = sourceid['files'][0]['mimeType']
            tempres = []
            if mime_type == 'application/vnd.google-apps.folder':
                items = self.driveService.files().list(
                    pageSize=self.limitFiles,
                    fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
                for item in items:
                    if item['mimeType'] != 'application/vnd.google-apps.folder':
                        self.download_file(source, item['id'], item['name'],
                                           item['mimeType'])
                        tempres.append(item)
            else:
                self.download_file(source, file_id, file_name, mime_type)
                tempres.append(sourceid['files'][0])
            return self.update_dict(tempres)
        else:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.driveService.files().list(
                q=query_params,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            print(sourceid)
            if len(sourceid) == 0:
                Console.error('No files found')
                sys.exit(1)
            file_id = sourceid['files'][0]['id']
            file_name = sourceid['files'][0]['name']
            mime_type = sourceid['files'][0]['mimeType']
            tempres = []
            if mime_type == 'application/vnd.google-apps.folder':
                items = self.driveService.files().list(
                    pageSize=self.limitFiles,
                    fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
                for item in items:
                    if item['mimeType'] != 'application/vnd.google-apps.folder':
                        self.download_file(source, item['id'], item['name'],
                                           item['mimeType'])
                        tempres.append(item)
            else:
                self.download_file(source, file_id, file_name, mime_type)
                tempres.append(sourceid['files'][0])
            return self.update_dict(tempres)

    def delete(self, service=None, filename=None,
               recursive=False):  # this is working
        file_id = ""
        file_rec = None
        if recursive:
            items = self.driveService.files().list(
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = items['files']
            for i in range(len(items)):
                if items[i]['name'] == filename:
                    file_rec = items[i]
                    file_id = items[i]['id']

            try:
                self.driveService.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                Console.error('No file found')
                return 'No file found'
        else:
            items = self.driveService.files().list(
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = items['files']
            for i in range(len(items)):
                if items[i]['name'] == filename:
                    file_rec = items[i]
                    file_id = items[i]['id']
            try:
                self.driveService.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                Console.error('No file found')
                return 'No file found'

        return self.update_dict(file_rec)

    def create_dir(self, service=None, directory=None):
        folders, filename = self.cloud_path(directory)
        id = None
        files = []
        for folder in folders:
            if id is None:
                file_metadata = {
                    'name': folder,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
            else:
                file_metadata = {
                    'name': folder,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [id]
                }
            file = self.driveService.files().create(
                body=file_metadata,
                fields='id, name, mimeType, parents, size, modifiedTime, createdTime').execute()
            files.append(file)
            print('Folder ID: %s' % file.get('id'))
            id = file.get('id')
        return self.update_dict(files)

    def list(self, service=None, source=None, recursive=False):
        if recursive:
            results = self.driveService.files().list(
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = results.get('files', [])
            if not items:
                Console.error('No files found')
                print('No files found.')
            else:
                return self.update_dict(items)
        else:
            query_params = "name='" + source + "' and trashed=false"
            sourceid = self.driveService.files().list(
                q=query_params,
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            file_id = sourceid['files'][0]['id']
            query_params = "'" + file_id + "' in parents"
            results = self.driveService.files().list(
                q=query_params,
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = results.get('files', [])
            print(items)
            if not items:
                Console.error('No files found')
                print('No files found.')
            else:
                return self.update_dict(items)

    def search(self, service=None, directory=None, filename=None,
               recursive=False):
        if recursive:
            found = False
            res_file = None
            list_of_files = self.driveService.files().list(
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            for file in list_of_files['files']:
                print(file)
                if file['name'] == filename:
                    res_file = file
                    found = True
                    break
                else:
                    continue
            return self.update_dict(res_file)
        else:
            found = False
            list_of_files = self.driveService.files().list(
                pageSize=self.limitFiles,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime, createdTime)").execute()
            for file in list_of_files['files']:
                print(file)
                if file['name'] == filename:
                    res_file = file
                    found = True
                    break
                else:
                    continue
            return self.update_dict(res_file)

    def upload_file(self, source, filename, parent_it):
        file_metadata = {'name': filename, 'parents': [parent_it]}
        self.driveService = self.driveService
        if source is None:
            filepath = filename
        else:
            filepath = source + '/' + filename
        media = MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0])
        file = self.driveService.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, parents,size,modifiedTime,createdTime').execute()
        return file

    def download_file(self, source, file_id, file_name, mime_type):
        filepath = source + '/' + file_name + mimetypes.guess_extension(
            mime_type)
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
        return filepath

    def cloud_path(self, srv_path):
        # Internal function to determine if the cloud path specified is file or folder or mix
        b_folder = []
        b_file = None
        src_file = srv_path
        if srv_path.startswith('/'):
            src_file = srv_path[1:]
        arr_folders = src_file.split('/')
        if '.' in arr_folders[-1]:
            return arr_folders[0:-1], arr_folders[-1]
        else:
            return arr_folders, None

    def update_dict(self, elements):
        if elements is None:
            return None
        elif type(elements) is list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for element in _elements:
            entry = element
            entry["cm"] = {
                "kind": "storage",
                "cloud": 'gdrive',
                "name": element['name'],
            }
        for c in ['modifiedTime', 'createdTime', 'size']:
            if c in entry.keys():
                entry['cm'][c] = entry[c]
            else:
                entry['cm'][c] = None
        for p in ['id', 'name', 'mimeType', 'parents', 'createdTime',
                  'size', 'modifiedTime']:
            if p in entry.keys():
                del (entry[p])
        d.append(entry)
        return d
