###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no -v --nocapture tests/test_storage.py:Test_storage.<METHIDNAME>
###############################################################
import os
from pprint import pprint

from  cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.common.parameter import Parameter
import pytest
from cloudmesh.variables import Variables
from cloudmesh.common.util import readfile

def create_dir(self, location):
    d = Path(os.path.dirname(path_expand(location)))
    d.mkdir(parents=True, exist_ok=True)

def create_file(self, location, content):
    create_dir(location)
    writefile(path_expand(location), content)


@pytest.mark.incremental
class Test_storage:

    def setup(self):
        variables = Variables()
        service = Parameter.expand(variables['storage'])[0]
        self.p = Provider(service=service)
        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        print()

    def test_create_source(self):
        HEADING()
        home = self.sourcedir
        # Setup a dir
        self.content = []
        self.files = ["a/a1.txt", "a/a2.txt", "a/a3.txt",
                  "a/b/b1.txt", "a/b/b2.txt", "a/b/b3.txt",
                  "a/b/c/c1.txt", "a/b/c/c2.txt", "a/b/c/c3.txt",
                  "a/b/d/d1.txt", "a/b/d/d2.txt", "a/b/d/d3.txt", "a/b/d/a1.txt"]

        for f in self.files:
            location = f"{home}/{f}"
            self.create_file(location, f"content of {f}")
            self.content.append(location)

        # setup empty dir in a
        self.create_dir(f"{home}/a/empty")

        for f in self.files:
            assert os.path.isfile(f)

        assert os.path.isdir(f"{home}/a/empty")




    def test_put_and_get(self):
        HEADING()
        home = self.sourcedir
        test_file = self.p.put(f"{home}/a/a1.txt", "/")
        assert test_file is not None

        test_file = self.p.get(f"/a/a1.txt", "f{home}/hello.txt")
        assert test_file is not None

        content = readfile("f{home}/hello.txt")
        assert "a1.txt" in content

    def test_list(self):
        HEADING()
        contents = self.p.list("/")
        for c in contents:
            pprint(c)

        assert len(contents) > 0
        found = False
        for entry in contents:
            if entry["name"] == "a/a1.txt":
                found = True


    def test_search(self):
        HEADING()
        src = '/'
        filename = '"a/a1.txt"'
        search_files = self.p.search("/", filename, True)
        pprint(search_files)
        assert len(search_files) > 0
        assert search_files[0]["name"] == filename

    def test_create_dir(self):
        HEADING()
        src = '/a/created_dir'
        directory = self.p.create_dir(src)
        pprint(directory)

        assert dir is not None
        assert directory["name"] == "/a/created_dir"


    def test_delete(self):
        HEADING()
        src = '/a/created_dir'
        self.p.delete(src)
        contents = self.p.list("/a")
        found = False
        for entry in contents:
            if entry["name"] == "created_dir":
                found = True
        assert found


    def test_recursive_put(self):
        # must be implemented by student from ~/.cloudmesh/storage/test
        # make sure all files are in the list see self.content which contains all files
        assert False

    def test_recursive_get(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/get
        # see self.content which contains all files but you must add get/
        assert False

    def test_recursive_delete(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/get
        # see self.content which contains all files but you must add get/
        assert False

    def test_exhaustive_list(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/
        # see self.content which contains all files that you can test against
        # in the list return. all of them must be in there
        assert False

    def test_selective_list(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/a/b
        # see self.content which contains all files that you can test against
        # in the list return. all of them must be in there but not more?
        # I am unsure if we implemented a secive list. If not let us know
        # full list for now is fine
        assert False

    def test_search_b1(self):
        # search for b1.txt
        assert False

    def test_search_b1_dir(self):
        # search for b/b2.txt see that this one has even the dir in the search
        assert False

    def test_search_a1(self):
        # search for a1.txt which shold return 2 entries
        assert False




















