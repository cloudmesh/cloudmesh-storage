from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import argparse
import io
import json
import mimetypes
import os
import sys
from pathlib import Path
from googleapiclient import errors
import httplib2
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config
from cloudmesh.abstract.StorageABC import StorageABC
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Below import statements are from awss3 Provider.py
import os
import platform
import stat
import textwrap

import boto3
import botocore
from cloudmesh.storage.provider.StorageQueue import StorageQueue
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase

from cloudmesh.storage.provider.awss3.path_manager import \
    extract_file_dict
from cloudmesh.storage.provider.awss3.path_manager import massage_path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class Provider(StorageQueue):

    kind = "parallelgdrive"

    sample = "TODO: missing"

    status = [
        'completed',
        'waiting',
        'inprogress',
        'canceled'
    ]

    output = {}  # "TODO: missing"

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml", parallelism=4):
        super().__init__(service=service, parallelism=parallelism)
        self.config = Config()
        self.storage_credentials = self.config.credentials("storage", "parallelgdrive")
        self.credentials_json_path = self.storage_credentials['credentials_json_path']
        self.token_path = self.storage_credentials['token_path']
        creds = None
        # Temporarily change directory to token_path specified in cloudmesh.yaml
        # This is to use the credentials.json file and token.pickle
        # Assuming credentials.json file and token.pickle will be in same directory in cloudmesh.yaml
        # Get current working directory
        cwd = os.getcwd()
        os.chdir(self.token_path)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # Change directory back to previous working directory
        os.chdir(cwd)

        service = build('drive', 'v3', credentials=creds)
        self.service = service

    def list_run(self, specification): # in mongdb, but can't run
        source = specification['path']
        dir_only = specification['dir_only']
        recursive = specification['recursive']
        if recursive:
            results = self.service.files().list(
                # pageSize=self.limitFiles,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = results.get('files', [])
            if not items:
                Console.error('No files found')
                print('No files found.')
            # else:
                # return self.update_dict(items)
        else:
            query_params = "name='" + source + "' and trashed=false"
            sourceid = self.service.files().list(
                q=query_params,
                # pageSize=self.limitFiles,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            file_id = sourceid['files'][0]['id']
            query_params = "'" + file_id + "' in parents"
            results = self.service.files().list(
                q=query_params,
                # pageSize=self.limitFiles,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = results.get('files', [])
            print(items)
            if not items:
                Console.error('No files found')
                print('No files found.')
            #else:
                # return self.update_dict(items)
        specification['status'] = 'completed'
        return specification

    def put_run(self, specification):
        source = specification['source']
        destination = specification['destination']
        recursive = specification['recursive']
        if recursive:
            if os.path.isdir(source):
                temp_res = []
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.service.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir_helper(directory=destination)
                    # file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        temp_res.append(
                            self.upload_file(source=source, filename=f,
                                             parent_it=file_parent_id))
                # return self.update_dict(temp_res)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.service.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir_helper(directory=destination)
                    # file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    # file_parent_id = sourceid['files'][0]['id']

                # res = self.upload_file(source=None, filename=source,
                #                        parent_it=file_parent_id)
                # return self.update_dict(res)
        else:
            if os.path.isdir(source):
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.service.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                temp_res = []
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir_helper(directory=destination)
                    file_parent_id = parent_file[0].get('id')
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                for f in os.listdir(source):
                    if os.path.isfile(os.path.join(source, f)):
                        temp_res.append(
                            self.upload_file(source=source, filename=f,
                                             parent_it=file_parent_id))
                # return self.update_dict(temp_res)
            else:
                query_params = "name='" + destination + "' and trashed=false"
                sourceid = self.service.files().list(
                    q=query_params,
                    fields="nextPageToken, files(id, name, mimeType)").execute()
                file_parent_id = None
                print(sourceid)
                if len(sourceid['files']) == 0:
                    parent_file = self.create_dir_helper(directory=destination)
                    # file_parent_id = parent_file['id']
                else:
                    print(sourceid['files'][0]['id'])
                    file_parent_id = sourceid['files'][0]['id']

                # res = self.upload_file(source=None, filename=source,
                #                        parent_it=file_parent_id)
                # return self.update_dict(res)
        specification['status'] = 'completed'
        return specification

    # def get(self, service=None, source=None, destination=None, recursive=False):
    def get_run(self, specification):
        source = specification['source']
        destination = specification['destination']
        recursive = specification['recursive']
        trimmed_source = massage_path(source)
        trimed_dest = massage_path(destination)
        if not os.path.exists(source):
            os.makedirs(source)

        if recursive:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.service.files().list(
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
                query_params = "'" + file_id + "' in parents"
                results = self.service.files().list(
                    q=query_params,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
                items = results.get('files', [])
                print("Items in directory to get: ",items)
                for item in items:
                    print("Type of item", type(item))
                    print("Item is:",item)
                    if item['mimeType'] != 'application/vnd.google-apps.folder':
                        self.download_file(source, item['id'], item['name'],
                                           item['mimeType'])
                        tempres.append(item)
            else:
                self.download_file(source, file_id, file_name, mime_type)
                tempres.append(sourceid['files'][0])
            # return self.update_dict(tempres)
        else:
            query_params = "name='" + destination + "' and trashed=false"
            sourceid = self.service.files().list(
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
                query_params = "'" + file_id + "' in parents"
                results = self.service.files().list(
                    q=query_params,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
                items = results.get('files', [])
                print("Items in directory to get: ",items)
                for item in items:
                    print("Type of item", type(item))
                    print("Item is:",item)
                    if item['mimeType'] != 'application/vnd.google-apps.folder':
                        self.download_file(source, item['id'], item['name'],
                                           item['mimeType'])
                        tempres.append(item)
            else:
                self.download_file(source, file_id, file_name, mime_type)
                tempres.append(sourceid['files'][0])
            # return self.update_dict(tempres)
        specification['status'] = 'completed'
        return specification

    def delete_run(self, specification): # works, deleted dir and sub-dirs in gdrive, seen in mongodb too
        source = specification['path']
        recursive = specification['recursive']

        file_id = ""
        file_rec = None
        if recursive:
            items = self.service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = items['files']
            for i in range(len(items)):
                if items[i]['name'] == source:
                    file_rec = items[i]
                    file_id = items[i]['id']

            try:
                self.service.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                Console.error('No file found')
                return 'No file found'
        else:
            items = self.service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            items = items['files']
            for i in range(len(items)):
                if items[i]['name'] == source:
                    file_rec = items[i]
                    file_id = items[i]['id']
            try:
                self.service.files().delete(fileId=file_id).execute()
            except:  # errors.HttpError, error:
                Console.error('No file found')
                return 'No file found'

        # return self.update_dict(file_rec)
        specification['status'] = 'completed'
        return specification

    def mkdir_run(self, specification):
        directory = specification['path']
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
            file = self.service.files().create(
                body=file_metadata,
                fields='id, name, mimeType, parents, size, modifiedTime, createdTime').execute()
            files.append(file)
            print('Folder ID: %s' % file.get('id'))
            id = file.get('id')
        return files

    def create_dir_helper(self, service=None, directory=None):
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
            file = self.service.files().create(
                body=file_metadata,
                fields='id, name, mimeType, parents, size, modifiedTime, createdTime').execute()
            files.append(file)
            print('Folder ID: %s' % file.get('id'))
            id = file.get('id')
        return files

    # def search(self, service=None, directory=None, filename=None,
    #            recursive=False):
    def search_run(self, specification):
        directory = specification['path']
        filename = specification['filename']
        recursive = specification['recursive']
        if recursive:
            found = False
            res_file = None
            list_of_files = self.service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime,createdTime)").execute()
            for file in list_of_files['files']:
                # print(file)
                if file['name'] == filename:
                    print(file)
                    res_file = file
                    found = True
                    break
                else:
                    continue
            # return self.update_dict(res_file)
        else:
            found = False
            list_of_files = self.service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, parents,size,modifiedTime, createdTime)").execute()
            for file in list_of_files['files']:
                # print(file)
                if file['name'] == filename:
                    print(file)
                    res_file = file
                    found = True
                    break
                else:
                    continue
            # return self.update_dict(res_file)
        specification['status'] = 'completed'
        return specification

    def upload_file(self, source, filename, parent_it):
        file_metadata = {'name': filename, 'parents': [parent_it]}
        self.service = self.service
        if source is None:
            filepath = filename
        else:
            filepath = source + '/' + filename
        media = MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0])
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, parents,size,modifiedTime,createdTime').execute()
        return file

    def download_file(self, source, file_id, file_name, mime_type):
        filepath = source + '/' + file_name # removed mime_type
        request = self.service.files().get_media(fileId=file_id)
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

if __name__ == "__main__":
    print()
    p = Provider(service="parallelgdrive")
    # p.create_dir(directory="gdrive_cloud4") # works
    p.list(source='gdrive_kids', dir_only=False, recursive=False) # works
    p.search(directory="/", filename="gift_on_sub_dir.docx") # works
    p.delete(source='gdrive_cloud4', recursive=True) # works.  The other day gave errors, but now works w/o chgs
    p.search(filename='gifts_at_1st_level.docx', recursive=False) # works
    p.get(source='C:/Users/sara/new_emp', destination='gift_on_sub_dir.docx', recursive=False) # works
    # p.get(source='C:/Users/sara/new_emp', destination='sub_gdrive_cloud', recursive=False) # works
    # p.get(source='C:/Users/sara/new_emp', destination='gdrive_cloud', recursive=True) # recursive=True not working
    p.put(source='C:/Users/sara/gdrive_dir', destination='gdrive_cloud2', recursive=False)  # works for either step, but not both
    p.run()
