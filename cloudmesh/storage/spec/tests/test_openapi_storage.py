###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_cloud_openapi_azure_storage.py:Test_cloud_openapi_azure_storage.test_001
# pytest -v --capture=no tests/test_openapi_azure_storage.py
# pytest -v  tests/test_openapi_azure_storage.py
###############################################################

from __future__ import print_function

import os
import time
import requests
import subprocess

import pytest
from cloudmesh.common.run.background import run
from cloudmesh.common.util import banner
from cloudmesh.shell.variables import Variables
from cloudmesh.common.parameter import Parameter

pytest.storage = None
pytest.openapi = None

# noinspection PyPep8
@pytest.mark.incremental
class Test_cloud_storage:
    """

    see: https://github.com/cloudmesh/cloudmesh-common/blob/master/cloudmesh/common/run/background.py
    the code in thel link has not bean tested
    make this s function execute the server in the back ground not in a termina,
    get the pid and kill it after the test is done
    UNAME := $(shell uname)
    ifeq ($(UNAME), Darwin)
    define terminal
      osascript -e 'tell application "Terminal" to do script "cd $(PWD); $1"'
    endef
    endif
    ifeq ($(UNAME), Linux)
    define terminal
      gnome-terminal --command 'bash -c "cd $(PWD); $1"'
    endef
    endif
    """

    def test_setup(self):
        self.variables = Variables()
        self.storages = Parameter.expand(self.variables['storage'])
        pytest.storage = self.storages[0]
        command = ['python', 'server.py']
        pytest.openapi = run(command)
        pytest.openapi.execute()
        print(pytest.openapi.pid)
        time.sleep(5)
        
    def test_create_dir(self):
        path = "tmp"
        try:
            os.mkdir(path)
        except OSError:
            print(f"Creation of the directory {path} failed")
        else:
            print(f"Successfully created the directory {path}")

        assert True

    def test_install(self):
        # $(call terminal, python server.py)
        #self.pytest_setup()
        #print(self.openapi.pid)
        time.sleep(3)

    def test_openapi_azure_storage_search(self):
        banner('search the blobs')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/search_blob?service={storage}&directory=%2ftest&filename=mp1%2ejpg&recursive=True")
        print(response)
        print()

    def test_openapi_azure_storage_list(self):
        banner('List the blobs')
        stor = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/list_blob?service={storage}&directory=%2ftest&recursive=True")
        print(response)
        print()

    def test_kill_pid(self):
        pytest.openapi.kill()

