# pytest -v --capture=no tests/benchmark/test_cms.py
# pytest -v  tests/benchmark/test_cms.py
# pytest -v --capture=no tests/benchmark/test_cms..py::Test_cms::<METHODNAME>
###############################################################

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING

cloud = "local"


@pytest.mark.incremental
class TestConfig:

    def test_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_vm(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help vm", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "['sample1', 'sample2', 'sample3', 'sample18']" in result

    def test_storage(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help vm", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "vm" in result

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
