###############################################################
# pytest -v --capture=no tests/test_storage_copy.py
# pytest -v  tests/test_storage_copy.py
# pytest -v --capture=no tests/test_storage_copy.py::TestStorage::<METHIDNAME>
###############################################################
import os
from pathlib import Path
from pprint import pprint

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.debug import VERBOSE

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


@pytest.mark.incremental
class TestStorage(object):

    def create_local_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print("TESTDIR:", d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def test_create_local_source(self):
        HEADING()
        StopWatch.start("create source")
        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        self.create_local_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        self.create_local_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        self.create_local_file("~/.cloudmesh/storage/test/a/b/c/c.txt",
                               "content of c")
        StopWatch.stop("create source")

        # test if the files are ok
        assert True

    def test_copy_local(self):
        HEADING()
        src = "/a.txt"
        dst = "~/.cloudmesh/storage/test"
        tag = f"copy {cloud} to local"
        StopWatch.start(tag)
        file = provider.copy(f'{cloud}:{src}', f'local:{dst}')
        StopWatch.stop(tag)
        pprint(file)
        assert file is not None

        dst = "/"
        src = "~/.cloudmesh/storage/test/a.txt"
        tag = f"copy local to {cloud}"
        StopWatch.start(tag)
        file = provider.copy(f'local:{src}', f'{cloud}:{dst}')
        StopWatch.stop(tag)
        pprint(file)
        assert file is not None

    def test_copy_cloud(self):
        # if storage = 'aws'   set storage2 = 'azure'
        # if storage = 'azure' set storage2 = 'aws'
        # cms set storage2='azure'

        HEADING()
        try:
            cloud2 = variables.parameter('storage2')
        except KeyError as e:
            raise ValueError("Parameter 'storage2' is not set. "
                             "Please use 'cms set storage2='azure'")
        except Exception as e:
            cloud2 = None
            raise ValueError("Error occurred: ", e)

        src = "a1.txt"
        dst = "/"
        tag = f"copy {cloud2} to {cloud}"

        print(f"Test run for copy {cloud2}:{src} {cloud}:{dst}")
        StopWatch.start(tag)
        file = provider.copy(f'{cloud2}:{src}', f'{cloud}:{dst}')
        StopWatch.stop(tag)
        pprint(file)
        assert len(file) > 0

        # copy command uses provider of target CSP hence __init__ of target
        # provider
        provider2 = Provider(service=cloud2)

        print('provider2:', provider2, provider2.kind)

        src = "a1.txt"
        dst = "/"
        tag = f"copy {cloud} to {cloud2}"
        print(f"Test run for copy {cloud}:{src} {cloud2}:{dst}")

        StopWatch.start(tag)
        file = provider2.copy(f'{cloud}:{src}', f'{cloud2}:{dst}')
        StopWatch.stop(tag)
        pprint(file)

        assert len(file) > 0

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
