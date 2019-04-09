# Google drive

:o: please modify your code  and documentation. the credential smust be stored somewhere 
under `~/.cloudmesh/`. Ifgoogle stores it by default somewhere else this needs to be discussde with us

:o: we do not know what gdirev means here as it is not relative to tehe home dir, so we are a bit confused. Please clarify

:o: sould it be `~/.cloud,esh/gdrive/.credentials` ? please be more specific in your documentation

For the Google Drive program to work we need 2 credentials files. 

* `client_secret.json` 
* `google-drive-credentials.json`  

If you call or run the Google Drive `provider.py` for the **First time** then the
program will automatically create  these 2 files.


`client_secret.json` credentials will be taken from `cloudmesh4.yaml` and it will
create a `client_secret.json` file saves it in the gdrive folder.

Then the `Provider.py` file will call the Authentication.py file and creates a
`.credentials` folder in gdrive folder and with in that folder it will
try to create `google-drive-credentials.json`. So, at this point of time your
browser will be opened up automatically and asks for the Google Drive(gmail)
credentials i.e., login email and  password. If you provide these 2 then
the Authentication step is completed and then it will download the 
`google-drive-credentials.json` and place it in `gdrive/.credentials` folder. 
 
These steps are to be followed for the first time or initial run. Once it is
done then our program is set. After these steps then the program will run
automatically by using these credentials stored in the respective files.

## Note

The Google Drive API accepts these 2 files in the form of **.json file format**
and not in the form of a dictionary.

## Links

Link for additional information:

* <https://github.com/cloudmesh-community/sp19-516-130/blob/master/gdrive.md>
