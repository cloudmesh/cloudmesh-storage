###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no tests/test_storage..py:::TestStorage::<METHODNAME>
###############################################################
import os
from pathlib import Path
from pprint import pprint

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

#
# TODO: all asserts are incomplete
#

Benchmark.debug()

tmp = "/tmp/cloudmesh/storage"

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

cloud = variables.parameter('storage')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("storage is not set")

provider = Provider(service=cloud)
print('provider:', provider, provider.kind)


@pytest.mark.incremental
class TestStorage(object):

    def create_local_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print("TESTDIR:", d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def create_local_source(self, size=1024):
        StopWatch.start(f"create source {size}")
        source = path_expand(f"{tmp}/source/{size}.txt")
        Benchmark.file(source, size)
        StopWatch.stop(f"create source {size}")

        # test if the files are ok
        assert True

    def test_create_local_source(self):
        HEADING()
        for size in [512, 1024]:
            self.create_local_source(size=size)

        # test if the files are ok
        assert True

    def test_put(self):
        HEADING()

        # root="~/.cloudmesh"
        # src = "storage/test/a/a.txt"

        # src = f"local:{src}"
        # dst = f"aws:{src}"
        # test_file = self.p.put(src, dst)

        # src = "storage_a:test/a/a.txt"

        src = f"{tmp}/source/"
        dst = f"{tmp}/destination/"
        StopWatch.start("put")
        test_file = provider.put(src, dst)
        StopWatch.stop("put")

        pprint(test_file)

        assert test_file is not None

    def test_get(self):
        HEADING()
        src = f"{tmp}/source/1024.txt"
        dst = f"{tmp}/destination/new-1024.txt"
        StopWatch.start("get")
        file = provider.get(src, dst)
        StopWatch.stop("get")
        pprint(file)

        assert file is not None

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
