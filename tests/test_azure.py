###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_box.py:Test_box.test_001
# pytest -v --capture=no tests/test_boxr.py
# pytest -v  tests/test_installer.py
###############################################################
import os
from pprint import pprint

import cloudmesh.storage.provider.azureblob.Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
import pytest

@pytest.mark.incremental
class TestAzure:

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print ("TESTDIR:",  d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def setup(self):
        self.p = cloudmesh.storage.provider.azureblob.Provider.Provider(service="azureblob")

    def test_01_create_source(self):
        HEADING()
        # create source dir

        self.destination = '/azstor_test'

        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")

        self.create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")

        # test if the files are ok
        assert True

    def test_02_create_dir(self):
        HEADING()
        src = '/azstor_test'
        dir = self.p.create_dir(self.p.service, src)
        src2 = '/azstor_test/test'
        dir2 = self.p.create_dir(self.p.service, src2)
        pprint(dir)

        assert dir is not None

    def test_03_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
        dst = "/azstor_test"
        test_file = self.p.put(self.p.service, src, dst)
        pprint(test_file)

        assert test_file is not None

    def test_04_get(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test")
        dst = "/azstor_test/a.txt"
        file = self.p.get(self.p.service, src, dst)
        pprint(file)

        assert file is not None

    def test_05_list(self):
        HEADING()
        src = '/'
        contents = self.p.list(self.p.service, src)
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_06_search(self):
        HEADING()
        src = '/'
        filename = 'a.txt'
        search_files = self.p.search(self.p.service, src, filename, True)
        pprint(search_files)

        assert len(search_files) > 0

    def test_07_delete(self):
        HEADING()
        src = '/azstor_test/test'
        self.p.delete(self.p.service, src)
