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
key = variables['key']

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

                # print("==================================> ", storage)
                provider = Provider(service=storage)

                banner(f"copy {source}:{src} to {target}:{dst}")
                texttag = f"copy {source}:{src} to {target}:{dst}"

                StopWatch.start(texttag)

                response = provider.copy(f'{source}:{src}', f'{target}:{dst}')
                if response is None:
                    Console.error(f"NULL response for copy {source}:{src} to "
                                  f"{target}:{dst}")
                    pass_flag = False

                StopWatch.stop(texttag)

        assert pass_flag

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=benchmark_tag)
