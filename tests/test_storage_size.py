# fix names
###############################################################
# pytest -v --capture=no tests/test_storage.py
# pytest -v  tests/test_storage.py
# pytest -v --capture=no tests/test_storage.py::TestStorage::<METHIDNAME>
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
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.debug import VERBOSE

# sizes = [512, 1024]
#

sizes = [512]

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
class TestStorageSize(object):

    def size_example_put(n):
        path = path_expand("~/.cloudmesh/tmp/put")
        # creat dir inpath

        Benchmark.file(f"{path}/{n}",n)
        # now put the file to the cloud probvider


    def size_example_get(n):
        path = path_expand("~/.cloudmesh/tmp/get")
        # creat dir inpath

        Benchmark.file(f"{path}/{n}", n)
        # now put the file to the cloud probvider

    def test_size_put(self):
        for size in sizes: # do some reasonable stuff here
            # trick now is that we use STorpwatch for nameing the timer
            Stopwatch.start(f"put {size}")
            slef.size_rexample_put(size)
            Stopwatch.stop(f"put {size}")
            # find a way on to see if you can get the file size from the provider
            # may be a missing function ... in the provider
            # maybe we can also create a hash function?
            # look into the dict that you get from the file for your provider to see what they have
            # look into the api ...

    def test_size_get(self):
        for size in sizes: # do some reasonable stuff here
            # trick now is that we use STorpwatch for nameing the timer
            Stopwatch.start(f"get {size}")
            slef.size_rexample_get(size)
            Stopwatch.stop(f"get {size}")
            # assert check if files in put and get dir on local machine are the same

    def test_cleanup(self):
        # delelte all the files form ths test

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
