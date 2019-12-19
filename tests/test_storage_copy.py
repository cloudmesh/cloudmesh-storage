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
        sizes = [1, 10]

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
        sources = ['local', 'awss3', 'azure', 'oracle', 'google']
        # sources = ['local', 'oracle']
        local_source = "~/.cloudmesh/storage/test"

        sizes = [1, 10]
        for size in sizes:
            file = f"size-{size}-file.txt"
            print("0" * 100)
            print(file)
            print("0" * 100)
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
                    elif target == "azure":
                        dst = '/'
                    else:
                        dst = file

                    print("0"*100)
                    provider = Provider(service=storage)

                    banner(f"copy {source}:{src} to {target}:{dst}")
                    texttag = f"copy {source}:{src} to {target}:{dst}"

                    StopWatch.start(texttag)
    #TODO : add try
                    response = provider.copy(f'{source}:{src}',
                                             f'{target}:{dst}')
                    if response is None:
                        Console.error(f"NULL response for copy {source}:{src}"
                                      f"to {target}:{dst}")
                        pass_flag = False

                    StopWatch.stop(texttag)
                    print("0" * 100)

        assert pass_flag

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=benchmark_tag)
