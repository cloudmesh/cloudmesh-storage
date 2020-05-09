###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no tests/test_storage.py::TestStorage::<METHIDNAME>
###############################################################
import os
from pprint import pprint

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables
from cloudmesh.storage.Provider import Provider
from cloudmesh.configuration.Config import Config

Benchmark.debug()

# cms set storage=aws

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

service = variables.parameter('storage')

print(f"Test run for {service}")

if service is None:
    raise ValueError("storage is not set")

provider = Provider(service=service)
print('provider:', provider, provider.kind)


@pytest.mark.incremental
class TestStorage(object):

    @staticmethod
    def create_file(location, content):
        Shell.mkdir(os.path.dirname(path_expand(location)))
        writefile(location, content)

    def test_create_local_source(self):
        HEADING()
        Benchmark.Start()
        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        self.create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        self.create_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        self.create_file(
            "~/.cloudmesh/storage/test/a/b/c/c.txt", "content of c")
        Benchmark.Stop()

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

        src = path_expand("~/.cloudmesh/storage/test/")
        dst = '/'
        Benchmark.Start()
        test_file = provider.put(src, dst)
        provider.run()
        Benchmark.Stop()

        pprint(test_file)

        assert test_file is not None

    def test_put_recursive(self):
        HEADING()

        # root="~/.cloudmesh"
        # src = "storage/test/a/a.txt"

        # source = f"local:{src}"
        # destination = f"aws:{src}"
        # test_file = self.p.put(src, dst)

        # src = "storage_a:test/a/a.txt"

        src = path_expand("~/.cloudmesh/storage/test/")
        dst = '/'
        Benchmark.Start()

        test_file = provider.put(src, dst, True)
        provider.run()
        Benchmark.Stop()
        pprint(test_file)

        assert test_file is not None

    def test_get(self):
        HEADING()
        src = "/a.txt"
        dst = path_expand("~/.cloudmesh/storage/test")
        Benchmark.Start()
        file = provider.get(src, dst)
        provider.run()
        Benchmark.Stop()
        pprint(file)

        assert file is not None

    # Clear everything in database and your cloud
    # Clear ~/.cloudmesh/storage/test directory
    # Then uncomment this code to test it
    # def test_get_recursive(self):
    #     HEADING()
    #     src = "/a"
    #     dst = "~/.cloudmesh/storage/test"
    #     Benchmark.Start()
    #     file = provider.get(src, dst, True)
    #     provider.run()
    #     Benchmark.Stop()
    #     pprint(file)
    #
    #     assert file is not None

    def test_list(self):
        HEADING()
        src = '/'
        Benchmark.Start()
        contents = provider.list(src)
        provider.run()
        Benchmark.Stop()
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_list_recursive(self):
        HEADING()
        src = '/'
        dir = "a"
        Benchmark.Start()
        contents = provider.list(src, dir, True)
        provider.run()
        Benchmark.Stop()
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_search(self):
        HEADING()
        src = '/'
        filename = "a.txt"
        Benchmark.Start()
        search_files = provider.search(src, filename, True)
        provider.run()
        Benchmark.Stop()
        pprint(search_files)
        assert len(search_files) > 0

    def test_create_dir(self):
        HEADING()
        src = 'created_dir'
        Benchmark.Start()
        directory = provider.create_dir(src)
        provider.run()
        Benchmark.Stop()

        pprint(directory)

        assert directory is not None

    def test_delete(self):
        HEADING()
        src = '/created_dir'
        Benchmark.Start()
        provider.delete(src)
        provider.run()
        Benchmark.Stop()

    # queue multiple commands and run together test case
    def test_multiple_run(self):
        HEADING()
        src = '/created_dir'
        Benchmark.Start()
        provider.create_dir(src)
        src1 = '/'
        provider.list(src1)
        provider.delete(src)
        provider.run()
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=True, csv=True, tag=service)
