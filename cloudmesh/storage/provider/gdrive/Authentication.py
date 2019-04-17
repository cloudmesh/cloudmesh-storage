# all this code has been taken and modified from 
# https://github.com/samlopezf/google-drive-api-tutorial
# https://developers.google.com/drive/api/v3/manage-uploads

import os

#
# missing in requirements.txt and setup.py
#
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pathlib import Path
from cloudmesh.common.util import path_expand

class Authentication:

    """
        Keeping a separate python file or class just for 
        authentication 
    """
    def __init__(self, scopes, client_secret_file, application_name, flags=None):

        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name
        self.flags = flags

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
        cwd = '~/.cloudmesh/gdrive/.credentials'
        path = Path(path_expand(cwd)).resolve()
        print(path)
        if not os.path.exists(path):
            print("creating folders")
            os.makedirs(path)
        print("created folders")
        
        credentials_path = os.path.join(path,
                                        'google-drive-credentials.json')
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
