from cloudmesh.common.util import HEADING
from cloudmesh.vdir.api.manager import Vdir
import pytest

@pytest.mark.incremental
class Test_vdir:

    def setup(self):
        self.vdir = Vdir()
        self.endpoint = 'box:/test.txt'
        self.dir_and_name = '/testdir/test'
        self.dir = 'testdir'
        self.file = 'test'

    def test_collection(self):
        HEADING()
        col = self.vdir.col

        assert col.name == 'local-vdir'

    @pytest.fixture(scope='class')
    def dummy_file(self):
        self.vdir = Vdir()
        self.endpoint = 'box:/test.txt'
        self.dir_and_name = 'test'
        testfile = self.vdir.add(endpoint=self.endpoint, dir_and_name=self.dir_and_name)
        return testfile

    @pytest.fixture(scope='class')
    def dummy_dir(self):
        self.vdir = Vdir()
        self.dir = 'testdir'
        testdir = self.vdir.mkdir(dirname=self.dir)
        return testdir


    def test_mkdir(self, dummy_dir):
        HEADING()

        assert dummy_dir is not None

    def test_add(self, dummy_file):
        HEADING()

        assert dummy_file is not None

    def test_ls(self):
        HEADING()
        results = self.vdir.ls(directory=None)

        assert results is not None

    def test_get(self):
        HEADING()
        file = self.vdir.get(name=self.file, destination=None)

        assert file is not None

    def test_status(self):
        HEADING()
        file = self.vdir.status(dir_or_name=self.file)

        assert file is not None

    def test_cd(self):
        HEADING()
        self.vdir.cd(dirname=self.dir)

        assert self.vdir.directory == self.dir

    def test_delete(self):
        HEADING()

        self.vdir.delete(dir_or_name=self.file)
        self.vdir.delete(dir_or_name=self.dir)






