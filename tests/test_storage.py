###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no -v --nocapture tests/test_storage.py:Test_storage.<METHIDNAME>
###############################################################
import os
from pprint import pprint
from cloudmesh.common.StopWatch import StopWatch
from  cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.common.parameter import Parameter
import pytest


@pytest.mark.incremental
class Test_storage:

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

    def test_create_source(self):
        HEADING()
        StopWatch.start("create source")
        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        self.create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        self.create_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        self.create_file("~/.cloudmesh/storage/test/a/b/c/c.txt", "content of c")
        StopWatch.stop("create source")

        # test if the files are ok
        assert True

    def test_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
        dst = "/"
        StopWatch.start("put")
        test_file = self.p.put(src, dst)
        StopWatch.stop("put")

        pprint(test_file)

        assert test_file is not None

    def test_get(self):
        HEADING()
        src = path_expand("/a.txt")
        dst = path_expand("~/test.txt")
        StopWatch.start("get")
        file = self.p.get(src, dst)
        StopWatch.stop("get")
        pprint(file)

        assert file is not None

    def test_list(self):
        HEADING()
        src = '/'
        StopWatch.start("list")
        contents = self.p.list(src)
        StopWatch.stop("list")
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_search(self):
        HEADING()
        src = '/'
        filename = 'test.txt'
        #
        # bug use named arguments
        #
        StopWatch.start("search")
        search_files = self.p.search(src, filename, True)
        StopWatch.stop("serach")
        pprint(search_files)
        assert len(search_files) > 0

    def test_create_dir(self):
        HEADING()
        src = '/created_dir'
        StopWatch.start("create dir")
        dir = self.p.create_dir(src)
        StopWatch.stop("create dir")

        pprint(dir)

        assert dir is not None

    def test_delete(self):
        HEADING()
        src = '/created_dir'
        StopWatch.start("delete")
        self.p.delete(src)
        StopWatch.stop("delete")


    def test_benchmark(self):
        StopWatch.benchmark()
















