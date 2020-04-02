###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no tests/test_storage..py:::TestStorage::<METHIDNAME>
###############################################################
import shutil
from pprint import pprint

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider

#
# cms set storage=gdrive
#

ASSERT_MISSING = False

Benchmark.debug()

location = "/tmp/cloudmesh/storage"

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

    def create_file(self, location, content):
        print(f"create: {location}")
        Shell.mkdir(location)
        writefile(location, content)

    def test_clean(self):
        HEADING()

        try:
            shutil.rmtree(location)
        except OSError as e:
            print(e.strerror)
            assert False, "Directory {location} could not be deleted"

    def test_create_local_source(self):
        HEADING()
        Benchmark.Start()
        self.sourcedir = path_expand(f"{location}/storage/source/test/")

        tree = [
            "a/a.txt",
            "a/b/b.txt",
            "a/b/c/c.txt"
        ]

        for file in tree:
            self.create_file(f"{location}/test/file", f"content of {file}")

        Benchmark.Stop()

        # test if the files are ok
        assert True

    def test_put(self):
        HEADING()

        src = f"{location}/storage/source/test/a.txt"
        dst = f"{location}/storage/destination/a.txt"
        Benchmark.Start()
        test_file = provider.put(src, dst)
        Benchmark.Stop()

        pprint(test_file)

        assert test_file is not None

    def test_get(self):
        HEADING()
        src = f"{location}/storage/source/test/a.txt"
        dst = f"{location}/storage/destination/a.txt"
        Benchmark.Start()
        file = provider.get(src, dst)
        Benchmark.Stop()
        pprint(file)

        assert file is not None

    def test_put_recursive(self):
        HEADING()

        src = f"{location}/storage/source/test/"
        dst = f"{location}/storage/destination"

        Benchmark.Start()
        test_file = provider.put(src, dst, True)
        Benchmark.Stop()

        pprint(test_file)

        assert test_file is not None

    def test_get_recursive(self):
        home = self.sourcedir
        src = f"{location}/storage/source/test/a"
        dst = f"{location}/storage/destination/get"
        Benchmark.Start()
        test_files = self.p.get(src, dst, True)
        Benchmark.Stop()
        pprint(test_files)

        assert test_files is not None

    def test_list(self):
        HEADING()
        src = f"{location}/storage/source/test/"
        Benchmark.Start()
        contents = provider.list(src)
        Benchmark.Stop()
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_list_dir_only(self):
        HEADING()
        src = f"{location}/storage/source/test/a"
        Benchmark.Start()
        contents = provider.list(src, dir, True)
        Benchmark.Stop()
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_search(self):
        HEADING()
        src = f"{location}/storage/source/test/"
        filename = "a.txt"
        Benchmark.Start()
        search_files = provider.search(src, filename, True)
        Benchmark.Stop()
        pprint(search_files)
        assert len(search_files) > 0
        # assert filename in search_files[0]['cm']["name"]

    def test_create_dir(self):
        HEADING()
        src = f"{location}/storage/source/test/created_dir"
        Benchmark.Start()
        directory = provider.create_dir(src)
        Benchmark.Stop()

        pprint(directory)

        assert directory is not None

    def test_delete(self):
        HEADING()
        src = f"{location}/storage/source/test/created_dir"
        Benchmark.Start()
        provider.delete(src)
        Benchmark.Stop()

        assert ASSERT_MISSING

    def test_benchmark(self):
        Benchmark.print()
