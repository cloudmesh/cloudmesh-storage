# all this code has been taken and modified from 
# https://github.com/samlopezf/google-drive-api-tutorial
# https://developers.google.com/drive/api/v3/manage-uploads

from __future__ import print_function

import os

#
# missing in requirements.txt and setup.py
#
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#
# BUG: WE DO NOT USE argparse but docopts
#

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class Authentication:
    """
        Keeping a separate python file or class just for 
        authentication 
    """

    def __init__(self, scopes, client_secret_file, application_name):

        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name

    def get_credentials(self):
        """
            We have stored the credentials in ".credentials"
            folder and there is a file named 'google-drive-credentials.json'
            that has all the credentials required for our authentication

            If there is nothing stored in it this program creates credentials 
            json file for future authentication
            Here the authentication type is OAuth2

        """
        cwd = os.getcwd()
        #
        # BUG: this is highly insecure and the file must be placed in ~/.cloudmesh/gdrive as credentials coudl be forgotten
        # permissions must be set properly for the dir before a file is placed in it
        # This is even discussed in the getting started page in google.
        #
        credentials_dir = os.path.join(cwd, '.credentials')
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
        credentials_path = os.path.join(credentials_dir,
                                       'google-drive-credentials.json')

        store = Storage(credentials_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file,
                                                  self.scopes)
            flow.user_agent = self.application_name
            if flags:
                credentials = tools.run_flow(flow, store, flags)

        return credentials
