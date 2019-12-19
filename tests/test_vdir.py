###############################################################
# pytest -v --capture=no tests/test_vdir.py
# pytest -v  tests/test_vdir.py
# pytest -v --capture=no tests/test_vdir.py:TestVdir.<METHODNAME>
###############################################################
import os
from pathlib import Path

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables
from cloudmesh.storage.Provider import Provider
from cloudmesh.vdir.api.manager import Vdir


@pytest.mark.incremental
class TestVdir(object):

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print("TESTDIR:", d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def setup(self):
        StopWatch.start("vdir setup")
        self.vdir = Vdir()
        self.endpoint = 'box:/test.txt'
        self.directory_and_name = '/testdir/test'
        self.directory = 'testdir'
        self.file = 'test'
        self.create_file('~/.cloudmesh/vdir/test/test.txt', 'test file')
        self.destination = path_expand("~/.cloudmesh/vdir/test")
        variables = Variables()
        service = Parameter.expand(variables['storage'])[0]
        self.p = Provider(service=service)
        self.p.put(source='~/.cloudmesh/vdir/test/test.txt', destination='/',
                   recursive=False)
        StopWatch.stop("vdir setup")

    def test_collection(self):
        HEADING()
        StopWatch.start("vdir collection")
        col = self.vdir.col
        StopWatch.stop("vdir collection")

        assert col.name == 'local-vdir'

    @pytest.fixture(scope='class')
    def dummy_file(self):
        self.endpoint = 'box:/test.txt'
        self.directory_and_name = 'test'

        StopWatch.start("vdir add")
        self.vdir = Vdir()
        testfile = self.vdir.add(endpoint=self.endpoint,
                                 dir_and_name=self.directory_and_name)
        StopWatch.stop("vdir add")
        return testfile

    @pytest.fixture(scope='class')
    def dummy_dir(self):
        self.directory = 'testdir'

        StopWatch.start("vdir mkdir")
        self.vdir = Vdir()
        testdir = self.vdir.mkdir(dirname=self.directory)
        StopWatch.stop("vdir mkdir")
        return testdir

    def test_mkdir(self, dummy_dir):
        HEADING()

        assert dummy_dir is not None

    def test_add(self, dummy_file):
        HEADING()

        assert dummy_file is not None

    def test_ls(self):
        HEADING()
        StopWatch.start("vdir ls")
        results = self.vdir.ls(directory=None)
        StopWatch.stop("vdir ls")

        assert results is not None

    def test_get(self):
        HEADING()
        StopWatch.start("vdir get")
        file = self.vdir.get(name=self.file, destination=self.destination)
        StopWatch.stop("vdir get")
        print(file)

        assert file is not None

    def test_status(self):
        HEADING()
        StopWatch.start("vdir status")
        file = self.vdir.status(dir_or_name=self.file)
        StopWatch.stop("vdir status")

        assert file is not None

    def test_cd(self):
        HEADING()
        StopWatch.start("vdir cd")
        self.vdir.cd(dirname=self.directory)
        StopWatch.stop("vdir cd")

        assert self.vdir.directory == self.directory

    def test_delete(self):
        HEADING()
        StopWatch.start("vdir delete")
        file = self.vdir.delete(dir_or_name=self.file)
        directory = self.vdir.delete(dir_or_name=self.directory)
        StopWatch.stop("vdir delete")

        assert all(obj is not None for obj in [file, directory])

    def test_results(self):
        HEADING()

        StopWatch.benchmark()
