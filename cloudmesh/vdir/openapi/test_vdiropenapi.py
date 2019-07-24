###############################################################
# pytest -v --capture=no tests/test_vdiropenapi.py
# pytest -v  tests/test_vdiropenapi.py
###############################################################
import os
import time
import requests

import pytest
from cloudmesh.common.run.background import run
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.storage.Provider import Provider


# noinspection PyPep8
@pytest.mark.incremental
class Test_vdir_openapi:
    """

    see: https://github.com/cloudmesh/cloudmesh-common/blob/master/cloudmesh/common/run/background.py
    the code in the link has not bean tested
    make this s function execute the server in the back ground not in a terminal,
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

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print("TESTDIR:", d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def test_setup(self):
        command = ['python', 'server.py']
        self.openapi = run(command).execute()
        time.sleep(5)

    def test_install(self):
        time.sleep(3)

    def test_create_source(self):
        # create source dir and upload it to provider
        self.create_file('~/.cloudmesh/test.txt', 'test file')
        Provider(service='box').put(source='~/.cloudmesh/test.txt', destination='/', recursive=False)

        assert True

    def test_vdir_openapi_mkdir(self):
        banner('Create directory')
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"dir": "testdir"}'
        response = requests.post('http://localhost:8080/cloudmesh/vdir/mkdir', headers=headers, data=data)
        print(response)
        print()

    def test_vdir_openapi_ls(self):
        banner('Print contents')
        response = requests.get(
            f"http://localhost:8080/cloudmesh/vdir/ls")
        print(response)
        print()

    def test_vdir_openapi_cd(self):
        banner('Navigate to test directory')
        response = requests.get(
            f"http://localhost:8080/cloudmesh/vdir/cd?dir=testdir")
        print(response)
        print()

    def test_vdir_openapi_add(self):
        banner('Add file link')
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"endpoint": "box:/test.txt", "dir_and_name": "test"}'
        response = requests.post('http://localhost:8080/cloudmesh/vdir/add', headers=headers, data=data)
        print(response)
        print()

    def test_vdir_openapi_status(self):
        banner('Get status of link')
        response = requests.get(
            f"http://localhost:8080/cloudmesh/vdir/status?dir_or_name=test")
        print(response)
        print()

    def test_vdir_openapi_get(self):
        banner('Get the file')
        response = requests.get(
            f"http://localhost:8080/cloudmesh/vdir/get?name=test'&'destination=~%2F.cloudmesh")
        print(response)
        print()

    def test_vdir_openapi_delete(self):
        banner('Delete link')
        response = requests.get(
            f"http://localhost:8080/cloudmesh/vdir/delete?dir_or_name=test")
        print(response)
        print()

