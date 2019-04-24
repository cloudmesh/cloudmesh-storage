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
    def __init__(self,
                 scopes,
                 credential_file,
                 client_secret_file,
                 application_name,
                 flags=None):

        self.scopes = scopes
        self.credential_file = credential_file
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
        #
        # Why is this not read from the yaml file?
        path = Path(path_expand(self.credential_file)).resolve()
        if not os.path.exists(path):
            os.makedirs(path)

        credentials_path = (path / 'google-drive-credentials.json').resolve()
        print(credentials_path)

        store = Storage(credentials_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file,
                                                  self.scopes)
            flow.user_agent = self.application_name
            #
            # SHOUDL THE FLAGS NOT BE SET IN THE YAML FILE OR DOCOPTS OFTHE COMMAND?
            #
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)

        return credentials
