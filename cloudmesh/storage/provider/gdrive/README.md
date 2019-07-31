# Google drive
## Put and Get in recursive way is still not working as expected. Delete, List, Search, Make Directory are working fine.

## cloudmesh.yaml file entries for gdrive storage
```
    gdrive: 
      cm: 
        heading: GDrive
        host: dgrive.google.com
        kind: gdrive
        label: GDrive
        version: TBD
      credentials: 
        auth_host_name: localhost
        auth_host_port: 
          - ****
          - ****
        auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
        auth_uri: "https://accounts.google.com/o/oauth2/auth"
        client_id: ********************************
        client_secret: ****************************
        project_id: *********************
        scopes: 'https://www.googleapis.com/auth/drive'
        application_name: '**********************'
        location_secret: '~/.cloudmesh/gdrive/client_secret.json'
        location_gdrive_credentials: '~/.cloudmesh/gdrive/.credentials'
        maxfiles: 1000
        redirect_uris: 
          - "urn:ietf:wg:oauth:2.0:oob"
          - "http://localhost"
        token_uri: "https://oauth2.googleapis.com/token"
      default: 
        directory: TBD
```

The Google Drive API needs the following two 2 credentials files. 
* `client_secret.json` 
* `google-drive-credentials.json`  

If we run the Google Drive `Provider.py` for the **First time** then the 
required keys, tokens are taken from the `cloudmesh.yaml` file and creates a 
`client_secret.json` file in the following path `~/.cloudmesh/gdrive/`  

The `Authentication.py` creates a `.credentials` folder under the following 
path `~/.cloudmesh/gdrive/` if it does not exist and creates a 
`google-drive-credentials.json` file under the following folder 
`~/.cloudmesh/gdrive/.credentials/` 


So, for the **First time** browser will be opened up automatically and asks 
for the Google Drive(gmail) credentials i.e., login email and  password. If 
you provide these 2 then the Authentication step is completed and then it 
will create the  `google-drive-credentials.json` and place it in 
`~/.cloudmesh/gdrive/.credentials/` folder. 
 
These steps are to be followed for the first time or initial run. Once it is
done then our program is set. After these steps then the program will run
automatically by using these credentials stored in the respective files.

## Note

The Google Drive API accepts these 2 files in the form of **.json file format**
and not in the form of a dictionary.

## Links

Link for additional information:

* <https://github.com/cloudmesh/cloudmesh-manual/blob/master/docs-source/source/accounts/storage-gdrive.md>
