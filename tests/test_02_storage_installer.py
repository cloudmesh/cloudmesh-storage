###############################################################
# pytest -v --capture=no tests/test_storage_installer.py
# pytest -v  tests/test_storage_installer.py
# pytest -v --capture=no tests/test_storage_installer..py::TestStorageInstaller::<METHODNAME>
###############################################################

import os
import shutil

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class TestStorageInstaller:

    def test_create_dir(self):
        HEADING()
        path = "tmp"
        try:
            os.mkdir(path)
        except OSError:
            print(f"Creation of the directory {path} failed")
        else:
            print(f"Successfully created the directory {path}")

        assert True

    def test_info(self):
        HEADING()
        cmd = "cloudmesh-installer info"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "Package" in str(result)

    def test_clone_cloud(self):
        HEADING()
        cmd = "cd tmp; cloudmesh-installer git clone storage"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5")

    def test_install_cms(self):
        HEADING()
        cmd = "cd tmp; cloudmesh-installer install storage -e"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5/cloudmesh_cmd5.egg-info")
        assert os.path.isdir("tmp/cloudmesh-cloud/cloudmesh_cloud.egg-info")
        assert os.path.isdir("tmp/cloudmesh-storage/cloudmesh_storage.egg-info")

    def test_cms_help(self):
        HEADING()
        cmd = "cms help"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "quit" in result
        assert "storage" in result

    def test_help_torage(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help storage", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "storage config list [--output=OUTPUT]" in result

    def test_cms_info(self):
        HEADING()
        cmd = "cms info"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result
        assert "cloudmesh.cloud" in result
        assert "cloudmesh.storage" in result

    def test_cms_version(self):
        HEADING()
        cmd = "cms version"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result
        assert "cloudmesh.cloud" in result
        assert "cloudmesh.storage" in result


class Other:
    def test_delete_dir(self):
        path = "tmp"
        shutil.rmtree(path)
        assert True
