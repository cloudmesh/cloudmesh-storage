# pytest -v --capture=no tests/test_storage.py
# nosetests -v --nocapture tests/test_storage.py
# nosetests -v tests/test_storage.py

import os
from pprint import pprint

import cloudmesh.storage.provider.Provider as Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.shell.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.common.parameter import Parameter

class TestBox:

    def create_file(self, location, content):

        d = Path(os.path.dirname(path_expand(location)))
        print()
        print ("TESTDIR:",  d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def setup(self):
        variables = Variables()
        service = Parameter.expand(variables['storage'])[0]

        self.p = Provider(service=service)

    def test_01_create_source(self):
        HEADING()

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



















