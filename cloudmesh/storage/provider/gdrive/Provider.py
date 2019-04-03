import io
import json

from cloudmesh.storage.provider.gdrive.Authentication import Authentication
import httplib2
#
# TODO: why can we not use requests?
#
# missing in requirements.txt and setup.py
# for some reson this gives an error
#
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.storage.StorageABC import StorageABC
import magic

#
# BUG: des not follow named arguments in abc class
#
class Provider(StorageABC):

    def __init__(self, cloud=None, config="~/.cloudmesh/cloudmesh4.yaml"):

        super(Provider, self).__init__(cloud=cloud, config=config)

        self.scopes = 'https://www.googleapis.com/auth/drive'
        self.clientSecretFile = path_expand(
            '~/.cloudmesh/gdrive/client_secret.json')
        self.applicationName = 'Drive API Python Quickstart'

        self.config = Config()
        self.clientSecretFile = self.generateKeyJson()
        self.authInst = Authentication(self.scopes,
                                       self.clientSecretFile,
                                       self.applicationName)
        self.credentials = self.authInst.get_credentials()
        #
        # TODO: is thi secure? http?
        #
        self.http = self.credentials.authorize(httplib2.Http())
        self.driveService = self.discovery.build('drive', 'v3', http=self.http)
        self.mime = magic.Magic(mime=True)

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

        #
        # BUG: MUST BE IN ~/.cloudmesch/gdrive/
        #
        with open(self.clientSecretFile, 'w') as fp:
            json.dump(data, fp)

    def put(self, filename):
        file_metadata = {'name': filename}

        # BUG: linux has a command file that finds the mimetyp, see if this is better,
        # mimetipse shoudl not just depend on filenames if possible

        mimetype = self.mime.from_file(filename)

        filepath = filename
        media = MediaFileUpload(filepath,
                                mimetype=mimetype)
        file = self.driveService.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
        print('File ID: %s' % file.get('id'))
        print("put", filename)

    def get(self, filename):
        """
                    Searching all the files in GDrive
                    and then comparing the given filename with
                    the file in cloud and then downloading it
                """

        file_id = ""

        items = Provider.listFiles(self)
        next = str(len(items))

        for i in range(len(items)):
            if items[i]['name'] == filename:
                file_id = items[i]['id']

        # bug mimetype should be found differntly not with .

        try:

            filetype = filename.split(".")[-1]
        except:
            filetype = ".jpg"

        # possible bug: filepath prefix can be determined in yaml file
        filepath = "google_download" + next + filetype  # file name in our local folder

        request = self.driveService.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
            # print("Download ")
        with io.open(filepath, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        print("gdrive provider get", filename)

    def delete(self, filename):
        file_id = ""

        items = Provider.listFiles(self)
        next = str(len(items))

        for i in range(len(items)):
            if items[i]['name'] == filename:
                file_id = items[i]['id']

        try:
            self.driveService.files().delete(fileId=file_id).execute()
        except:  # errors.HttpError, error:
            print('An error occurred:')  # %s' % error
        print("delete", filename, file_id)

    def createFolder(self, name):
        file_metadata = {'name': name,
                         'mimeType': 'application/vnd.google-apps.folder'}
        file = self.driveService.files().create(body=file_metadata,
                                                fields='id').execute()

        # needs to store this in a mongoDB
        print('Folder ID: %s' % file.get('id'))

    def listFiles(self, size=10):
        self.size = size
        results = self.driveService.files().list(pageSize=size,
                                                 fields="nextPageToken, files(id, name,mimeType)").execute()
        items = results.get('files', [])
        # print(items)
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                # print('{0} ({1})'.format(item['name'], item['id']))
                print(
                    "FileId : {id}, FileName : {name}, FileType : {mimeType}  ".format(
                        **item))
        return items
