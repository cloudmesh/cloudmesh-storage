# pytest -v --capture=no tests/test_azure.py
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_azure.py

import os
from pprint import pprint

import cloudmesh.storage.provider.azureblob.Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile

class TestBox:

    def create_file(self, location, content):

        d = Path(os.path.dirname(path_expand(location)))
        print()
        print ("TESTDIR:",  d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def setup(self):
        self.p = cloudmesh.storage.provider.azureblob.Provider.Provider(service="azure")

    def test_01_create_source(self):
        # create source dir

        # BUG
        self.destination = "set the destination location here and use in tests" # TODO

        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")

        self.create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        self.create_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        self.create_file("~/.cloudmesh/storage/test/a/b/c/c.txt", "content of c")

        # test if the files are ok
        assert True

    def test_01_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
        dst = "/"
        test_file = self.p.put(src, dst)
        pprint(test_file)

        assert test_file is not None

    def test_02_get(self):
        HEADING()
        src = path_expand("/a.txt")
        dst = path_expand("~/test.txt")
        file = self.p.get(src, dst)
        pprint(file)

        assert file is not None

    def test_03_list(self):
        HEADING()
        src = '/'
        contents = self.p.list(src)
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_04_search(self):
        HEADING()
        src = '/'
        filename = 'test.txt'
        #
        # bug use named arguments
        #
        search_files = self.p.search(src, filename, True)
        pprint(search_files)

        assert len(search_files) > 0

    def test_05_create_dir(self):
        HEADING()
        src = '/created_dir'
        dir = self.p.create_dir(src)
        pprint(dir)

        assert dir is not None

    def test_06_delete(self):
        HEADING()
        src = '/created_dir'
        self.p.delete(src)



















