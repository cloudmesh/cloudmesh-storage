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
from cloudmesh.common.util import banner
from cloudmesh.common.console import Console

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
#VERBOSE(variables.dict())

key = variables['key']

# cloud = variables.parameter('storage')
#
# print(f"Test run for {cloud}")
#
# if cloud is None:
#     raise ValueError("storage is not set")
#
# provider = Provider(service=cloud)
# print('provider:', provider, provider.kind)

benchmark_tag = "storage copy"


@pytest.mark.incremental
class TestStorage(object):

    def test_create_local_source(self):
        HEADING()
        sizes = [1, 2, 3]

        for size in sizes:
            texttag = f"create size-{size} file"
            StopWatch.start(texttag)
            source = path_expand(f"~/.cloudmesh/storage/test/size-"
                                 f"{size}-file.txt")

            d = Path(os.path.dirname(path_expand(source)))
            d.mkdir(parents=True, exist_ok=True)

            Benchmark.file(source, size)
            StopWatch.stop(texttag)

        assert True

    def test_copy(self):
        HEADING()
        # sources = ['local', 'awss3', 'azure', 'oracle', 'google']
        sources = ['local', 'azure']
        local_source = "~/.cloudmesh/storage/test"

        size = 1
        file = f"size-{size}-file.txt"
        pass_flag = True

        for source in sources:
            targets = sources.copy()
            targets.remove(source)

            for target in targets:

                storage = target

                if source == "local":
                    src = str(Path(Path(local_source) / file))
                else:
                    src = file

                if target == "local":
                    dst = str(Path(Path(local_source) / file))
                    storage = source
                else:
                    dst = file

                print("==================================> ", storage)
                provider = Provider(service=storage)

                banner(f"copy {source}:{src} to {target}:{dst}")
                texttag = f"copy {source}:{src} to {target}:{dst}"

                StopWatch.start(texttag)

                response = provider.copy(f'{source}:{src}', f'{target}:{dst}')
                if response is None:
                    Console.error(f"NULL reposnse for copy {source}:{src} to "
                                  f"{target}:{dst}")
                    pass_flag = False

                StopWatch.stop(texttag)

        assert pass_flag

    # def create_local_source(self, size=1024):
    #     StopWatch.start(f"create source {size}")
    #     source = path_expand(f"~/.cloudmesh/storage/temp/{size}.txt")
    #     Benchmark.file(source, size)
    #     StopWatch.stop(f"create source {size}")
    #
    #     # test if the files are ok
    #     assert True
    #
    #
    # def test_copy_local(self):
    #     HEADING()
    #     src = "/a.txt"
    #     dst = "~/.cloudmesh/storage/test"
    #     tag = f"copy {cloud} to local"
    #     StopWatch.start(tag)
    #     file = provider.copy(f'{cloud}:{src}', f'local:{dst}')
    #     StopWatch.stop(tag)
    #     pprint(file)
    #     assert file is not None
    #
    #     dst = "/"
    #     src = "~/.cloudmesh/storage/test/a.txt"
    #     tag = f"copy local to {cloud}"
    #     StopWatch.start(tag)
    #     file = provider.copy(f'local:{src}', f'{cloud}:{dst}')
    #     StopWatch.stop(tag)
    #     pprint(file)
    #     assert file is not None
    #
    # def test_copy_cloud(self):
    #     # if storage = 'aws'   set storage2 = 'azure'
    #     # if storage = 'azure' set storage2 = 'aws'
    #     # cms set storage2='azure'
    #
    #     HEADING()
    #     try:
    #         cloud2 = variables.parameter('storage2')
    #     except KeyError as e:
    #         raise ValueError("Parameter 'storage2' is not set. "
    #                          "Please use 'cms set storage2='azure'")
    #     except Exception as e:
    #         cloud2 = None
    #         raise ValueError("Error occurred: ", e)
    #
    #     src = "a1.txt"
    #     dst = "/"
    #     tag = f"copy {cloud2} to {cloud}"
    #
    #     print(f"Test run for copy {cloud2}:{src} {cloud}:{dst}")
    #     StopWatch.start(tag)
    #     file = provider.copy(f'{cloud2}:{src}', f'{cloud}:{dst}')
    #     StopWatch.stop(tag)
    #     pprint(file)
    #     assert len(file) > 0
    #
    #     # copy command uses provider of target CSP hence __init__ of target
    #     # provider
    #     provider2 = Provider(service=cloud2)
    #
    #     print('provider2:', provider2, provider2.kind)
    #
    #     src = "a1.txt"
    #     dst = "/"
    #     tag = f"copy {cloud} to {cloud2}"
    #     print(f"Test run for copy {cloud}:{src} {cloud2}:{dst}")
    #
    #     StopWatch.start(tag)
    #     file = provider2.copy(f'{cloud}:{src}', f'{cloud2}:{dst}')
    #     StopWatch.stop(tag)
    #     pprint(file)
    #
    #     assert len(file) > 0

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=benchmark_tag)
