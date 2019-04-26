all: azureblob box gdrive vdir awss3
	echo


azureblob:
	pytest -v --capture=no tests/test_storage_azure.py
	cms set storage=azureblob
	pytest -v --capture=no tests/test_general_storage.py

box:
	pytest -v --capture=no tests/test_storage_box.py
	cms set storage=box
	pytest -v --capture=no tests/test_general_storage.py

gdrive:
	pytest -v --capture=no tests/test_storage_gdrive.py
	cms set storage=gdrive
	pytest -v --capture=no tests/test_general_storage.py

awss3:
	pytest -v --capture=no tests/test_storage_awss3.py
	cms set storage=awss3
	pytest -v --capture=no tests/test_general_storage.py

vdir:
 	pytest -v --capture=no tests/test_vdir.py
