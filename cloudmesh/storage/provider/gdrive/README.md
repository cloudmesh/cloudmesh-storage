## Documentation
## Google drive

For the Google Drive program to work we need 2 credentials files. <br />
### 1) client_secret.json  <br />
### 2) google-drive-credentials.json  <br />

If you call or run the Google Drive provider.py for the **First time** then the program will automatically create <br />
these 2 files.<br />


client_secret.json credentials will be taken from cloudmesh4.yaml and it will create a client_secret.json file <br />
saves it in the gdrive folder. <br />

Then the Provider.py file will call the Authentication.py file and creates a ".credentials" folder in gdrive <br />
folder and with in that folder it will try to create google-drive-credentials.json. So, at this point of time your<br />
browser will be opened up automatically and asks for the Google Drive(gmail) credentials i.e., login email and <br />
password. If you provide these 2 then the Authentication step is completed and then it will download the <br />
google-drive-credentials.json and place it in gdrive/.credentials folder. <br />
 
These steps are to be followed for the first time or initial run .Once it is done then our program is set.<br />
After these steps then the program will run automatically by using these credentials stored in the <br />
respective files. <br />

### Note:

The Google Drive API accepts these 2 files in the form of **.json file format** and not in the form of a dictionary.

### For further documentation go through the link provided below
https://github.com/cloudmesh-community/sp19-516-130/blob/master/gdrive.md
