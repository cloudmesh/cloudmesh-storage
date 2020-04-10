###############################################################
# pytest -v --capture=no tests/test_local.py
# pytest -v  tests/test_local.py
# pytest -v --capture=no tests/test_local..py::TestLocal.<METHIDNAME>
###############################################################
import os
from pathlib import Path

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

key = variables['key']

cloud = variables.parameter('storage')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("storage is not set")

provider = Provider(service=cloud)
print('provider:', provider, provider.kind)


def create_file(location, content):
    d = Path(os.path.dirname(path_expand(location)))
    print()
    print("TESTDIR:", d)

    d.mkdir(parents=True, exist_ok=True)

    writefile(path_expand(location), content)


@pytest.mark.incremental
class TestLocal(object):

    def setup_class(self):
        # variables = Variables()
        # service = Parameter.expand(variables['storage'])[0]

        self.service = "local"
        self.p = Provider(service=self.service)

    def test_00__config(self):
        VERBOSE(self.p)
        VERBOSE(self.p.kind)
        assert self.p.kind == self.service

    def test_01_create_source(self):
        HEADING()

        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        create_file("~/.cloudmesh/storage/README-old.md", "content of a")
        create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        create_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        create_file("~/.cloudmesh/storage/test/a/b/c/c.txt", "content of c")

        # test if the files are ok
        assert True

    def test_02_list(self):
        HEADING()
        StopWatch.start("list")
        src = '/'
        contents = self.p.list(source=src)

        VERBOSE(contents, label="c")

        for c in contents:
            VERBOSE(c)
        StopWatch.stop("list")

    def test_05_search(self):
        HEADING()
        StopWatch.start("search")
        src = '/'
        filename = 'a.txt'
        #
        # bug use named arguments
        #
        files = self.p.search(directory=src, filename=filename, recursive=True)
        #pprint(files)
        StopWatch.stop("search")

        assert len(files) > 0

    def test_02_put(self):
        HEADING()
        StopWatch.start("put")
        src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
        dst = "~/"
        test_file = self.p.put(src, dst)
        #pprint(test_file)
        StopWatch.stop("put")

        assert test_file is not None

    def test_03_get(self):
        HEADING()
        StopWatch.start("get")
        src = path_expand("~/a.txt")
        dst = path_expand("~/test.txt")
        file = self.p.get(src, dst)
        #pprint(file)
        StopWatch.stop("get")

        assert file is not None

        #assert len(content) > 0

    def test_06_create_dir(self):
        HEADING()
        StopWatch.start("create_dir")
        src = path_expand("~/created_dir")
        directory = self.p.create_dir(src)
        #pprint(directory)
        StopWatch.stop("create_dir")

        assert directory is not None

    def test_07_delete(self):
        HEADING()
        StopWatch.start("delete")
        src = path_expand("~/created_dir")
        self.p.delete(src)
        StopWatch.stop("delete")

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
