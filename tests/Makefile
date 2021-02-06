#
# TODO: this may be outdated
#

PYTEST=pytest -v --capture=no


all: local azure box google aws vdir
	echo

local:
	$(PYTEST) test_01_storage_size.py
	$(PYTEST) test_02_storage_installer.py
	$(PYTEST) test_03_storage_local.py
	$(PYTEST) test_04_storage_copy.py

azure:
	$(PYTEST) tests/azure/test_storage_azure.py
	cms set storage=azureblob
	$(PYTEST) tests/test_general_storage.py

box:
	$(PYTEST) tests/box/test_storage_box.py
	cms set storage=box
	$(PYTEST) tests/test_general_storage.py

google:
	$(PYTEST) tests/gdrive/test_storage_gdrive.py
	cms set storage=gdrive
	$(PYTEST) tests/test_general_storage.py

aws:
	$(PYTEST) tests/awss3/test_storage_awss3.py
	cms set storage=awss3
	$(PYTEST) tests/test_general_storage.py

vdir:
	$(PYTEST) tests/test_vdir.py

