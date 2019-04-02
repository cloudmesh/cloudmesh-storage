# all this code has been taken and modified from 
#https://github.com/samlopezf/google-drive-api-tutorial
#https://developers.google.com/drive/api/v3/manage-uploads

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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

    def __init__(self, scopes, clientSecretFile, applicationName):
        
        self.scopes = scopes
        self.clientSecretFile = clientSecretFile
        self.applicationName = applicationName

    def get_credentials(self):
        """
            We have stored the credentials in ".credentials"
            folder and there is a file named 'google-drive-credentials.json'
            that has all the credentials required for our authentication

            If there is nothing stored in it this program creates credentials 
            json file for future authentication
            Here the authentication type is OAuth2

        """
        cwDir = os.getcwd()
        credentialsDir = os.path.join(cwDir, '.credentials')
        if not os.path.exists(credentialsDir):
            os.makedirs(credentialsDir)
        credentialsPath = os.path.join(credentialsDir,'google-drive-credentials.json')
                                       

        store = Storage(credentialsPath)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.clientSecretFile, self.scopes)
            flow.user_agent = self.applicationName
            if flags:
                credentials = tools.run_flow(flow, store, flags)

        return credentials