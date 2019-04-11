###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_storage_installer.py:Test_storage_installer.test_001
# pytest -v --capture=no tests/test_storage_installerr.py
# pytest -v  tests/test_installer.py
###############################################################

from __future__ import print_function
import shutil

import os
import pytest
from cloudmesh_installer.install.test import readfile, run


@pytest.mark.incremental
class Test_storage_installer:

    def test_create_dir(self):
        path = "tmp"
        try:
            os.mkdir(path)
        except OSError:
            print(f"Creation of the directory {path} failed")
        else:
            print(f"Successfully created the directory {path}")

        assert True

    def test_info(self):
        cmd = "cloudmesh-installer info"
        result = run(cmd)
        print(result)
        assert "Package" in str(result)

    def test_clone_cloud(self):
        cmd = "cd tmp; cloudmesh-installer git clone storage"
        result = run(cmd)
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5")

    def test_install_cms(self):
        cmd = "cd tmp; cloudmesh-installer install storage -e"
        result = run(cmd)
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5/cloudmesh_cmd5.egg-info")
        assert os.path.isdir("tmp/cloudmesh-cloud/cloudmesh_cloud.egg-info")
        assert os.path.isdir("tmp/cloudmesh-storage/cloudmesh_storage.egg-info")

    def test_cms_help(self):
        cmd = "cms help"
        result = run(cmd)
        print(result)
        assert "quit" in result
        assert "storage" in result
        assert "vm" in result

    def test_cms_info(self):
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result
        assert "cloudmesh.cloud" in result
        assert "cloudmesh.storage" in result

    def test_cms_version(self):
        cmd = "cms version"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result
        assert "cloudmesh.cloud" in result
        assert "cloudmesh.storage" in result




class other:
    def test_delete_dir(self):
        path = "tmp"
        shutil.rmtree(path)
        assert True
