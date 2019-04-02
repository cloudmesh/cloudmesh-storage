import io
import json

import Authentication
import httplib2
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from cloudmesh.management.configuration.config import Config


class Provider(StorageABC):

    def __init__(self, WRONG PARAMS

    ):

    # SUPER NEEDED LOOK AT MY CODE IN THIS DIR FROM
    super(Provider, self).__init__(cloud=cloud, config=config)

    self.scopes = 'https://www.googleapis.com/auth/drive'
    self.clientSecretFile = 'client_secret.json'
    self.applicationName = 'Drive API Python Quickstart'

        self.config = Config()
        self.clientSecretFile = self.generateKeyJson()
    self.authInst = Authentication.Authentication(self.scopes,
                                                  self.clientSecretFile,
                                                  self.applicationName)
        self.credentials = self.authInst.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.driveService = self.discovery.build('drive', 'v3', http=self.http)


def generateKeyJson(self):
    credentials = self.config.credentials("storage", "gdrive")
    data = {"installed": {
        "client_id": credentials["client_id"]
        data["installed"]["project_id"] = credentials["project_id"]
    data["installed"]["auth_uri"] = credentials["auth_uri"]
    data["installed"]["token_uri"] = credentials["token_uri"]
    data["installed"]["client_secret"] = credentials["client_secret"]
    data["installed"]["auth_provider_x509_cert_url"] = credentials[
        "auth_provider_x509_cert_url"]
    data["installed"]["redirect_uris"] = credentials["redirect_uris"]
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

        mimetype = "image/jpeg"
        mimetype = Provider.fileTypetoMimeType(filename)

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


def fileTypetoMimeType(self, filename):

        fimidict = {"jpg": "image/jpeg",
                    "mp4": "video/mp4",
                    "mp3": "audio/mp3",
                    "json": "text/json",
                    "png": "image/png",
                    "txt": "text/text",
                    "csv": "text/csv"}
        mimetype = "image/jpeg"

        filetype = filename.split(".")[-1]

        #
        # possible better method, this is quick and ok for now, but there is for example the linux function `file`
        #

        # For
        # MIME
        # types
        # >> > import magic
        # >> > mime = magic.Magic(mime=True)
        # >> > mime.from_file("testdata/test.pdf")
        # 'application/pdf'
        # >> >

        try:
            mimetype = fimidict[filetype]
        except:
            mimetype = "image/jpeg"

        return mimetype


p = Provider()
print(p.listFiles())
