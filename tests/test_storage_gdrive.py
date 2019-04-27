###############################################################
# pytest -v --capture=no tests/test_gdrive.py
# pytest -v  tests/test_gdrive.py
# pytest -v --capture=no -v --nocapture tests/test_gdrive.py:Test_gdrive.<METHIDNAME>
###############################################################from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
from cloudmesh.storage.provider.gdrive.Provider import Provider

from pathlib import Path
import os
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.storage.provider.gdrive.Provider import Provider
import pytest

@pytest.mark.incremental
class Test_gdrive:

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        d.mkdir(parents=True, exist_ok=True)
        writefile(path_expand(location), content)

    def setup(self):
        self.p = Provider(service="gdrive")
        self.destination = path_expand("/")
        self.source = path_expand("~/.cloudmesh/storage/test/source/")
        self.create_file("~/.cloudmesh/storage/test/source/test/source/sample_source.txt",
                         "This is sample test file")
        assert True

    def test_01_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/source/test/source/sample_source.txt")
        dst = "/"
        # Put files from src into google drive home directory
        test_file = self.p.put(source=src, destination=dst, recursive=False)
        print(test_file)
        assert test_file is not None

    def test_02_get(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/source/test/source/")
        dst = 'getExample.txt'
        # fetching files from dst to src
        file = self.p.get(source=src, destination=dst, recursive=False)
        assert file is not None

    def test_03_list(self):
        HEADING()
        # Listing files google drive home directory
        contents = self.p.list(source='/', recursive=True)
        print("check contents")
        print(contents)
        assert len(contents) > 0

    def test_04_search(self):
        HEADING()
        # Searching sample_source.txt which is created earlier in home directory
        search_files = self.p.search(directory='/', filename='Useful Links.txt', recursive=True)
        pprint(search_files)
        assert search_files is not None

    def test_05_create_dir(self):
        HEADING()
        # Creating testdir in home directory of google drive
        dir = self.p.create_dir(directory='/testdir')
        assert dir is not None

    def test_06_delete(self):
        HEADING()
        # Deleting in google drive home sample_source.txt
        message = self.p.delete(filename='sample_source.txt')

        assert message is not None
