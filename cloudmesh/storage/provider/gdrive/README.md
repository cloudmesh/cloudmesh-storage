# Google drive

The Google Drive API needs the following two 2 credentials files. 
* `client_secret.json` 
* `google-drive-credentials.json`  

If we run the Google Drive `Provider.py` for the **First time** then the required keys, tokens are taken from the `cloudmesh4.yaml` file and creates a `client_secret.json` file in the follwing path `~/.cloudmesh/gdrive/`

The `Authentication.py` creates a `.credentials` folder under the following path `~/.cloudmesh/gdrive/` if it doesn't exist and creates a `google-drive-credentials.json` file under the following folder `~/.cloudmesh/gdrive/.credentials/`



So, for the **First time**
browser will be opened up automatically and asks for the Google Drive(gmail)
credentials i.e., login email and  password. If you provide these 2 then
the Authentication step is completed and then it will create the 
`google-drive-credentials.json` and place it in `~/.cloudmesh/gdrive/.credentials/` folder. 
 
These steps are to be followed for the first time or initial run. Once it is
done then our program is set. After these steps then the program will run
automatically by using these credentials stored in the respective files.

## Note

The Google Drive API accepts these 2 files in the form of **.json file format**
and not in the form of a dictionary.

## Links

Link for additional information:

* <https://github.com/cloudmesh-community/sp19-516-130/blob/master/gdrive.md>
