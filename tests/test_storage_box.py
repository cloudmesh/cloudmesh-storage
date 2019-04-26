###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_storage_box.py:Test_box.test_001
# pytest -v --capture=no tests/test_storage_box.py
# pytest -v  tests/test_installer.py
###############################################################
from pprint import pprint
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.provider.box.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.StopWatch import StopWatch
import os
import pytest
from pathlib import Path
import time

@pytest.mark.incremental
class Test_box:

    def setup(self):
        StopWatch.start("test setup")
        self.p = Provider(service="box")
        self.source = location = path_expand('~/.cloudmesh/storage/test/box')
        self.source_file = source = path_expand(f'{location}/test.txt')

        os.makedirs(self.source, exist_ok=True)
        writefile(Path(source), 'Test content')
        self.destination = "/"
        self.destination_file = '/test.txt'
        self.filename = 'test.txt'
        self.testdir = '/testdir'
        StopWatch.stop("test setup")

    @pytest.fixture(scope='class')
    def dummy_dir(self):
        StopWatch.start("box create dir")
        self.p = Provider(service="box")
        destination = self.destination = "/"
        test_dir = self.p.create_dir(service=self.p.service,
                                     directory=f"{destination}testdir")
        StopWatch.stop("box create dir")
        return test_dir


    def test_config(self):
        StopWatch.start("test config")
        config = Config()
        storage = config['cloudmesh.storage']
        StopWatch.stop("test config")
        print(storage)

    def test_provider(self):
        StopWatch.start("test provider")
        file = open(self.source_file)
        StopWatch.stop("test provider")

        assert file.read() == 'Test content'

    def test_put(self):
        HEADING()
        StopWatch.start("box put")
        test_file = self.p.put(service=self.p.service,
                               source=self.source_file,
                               destination=self.destination,
                               recursive=False)
        pprint(test_file)
        StopWatch.stop("box put")

        assert test_file is not None

    def test_get(self):
        HEADING()
        StopWatch.start("box get")
        file = self.p.get(service=self.p.service,
                          source=self.destination_file,
                          destination=self.source,
                          recursive=False)
        pprint(file)
        StopWatch.stop("box get")

        assert file is not None

    def test_list(self):
        HEADING()
        StopWatch.start("box list")
        contents = self.p.list(service=self.p.service,
                               source=self.destination,
                               recursive=False)
        for c in contents:
            pprint(c)
        StopWatch.stop("box list")

        assert len(contents) > 0

    def test_search(self):
        HEADING()
        StopWatch.start("box search")
        search_files = self.p.search(service=self.p.service,
                                     directory=self.destination,
                                     filename=self.filename,
                                     recursive=False)
        while search_files is None:
            time.sleep(90)
            search_files = self.p.search(service=self.p.service,
                                         directory=self.destination,
                                         filename=self.filename,
                                         recursive=False)
        pprint(search_files)
        StopWatch.start("box search")

        assert len(search_files) > 0

    def test_create_dir(self, dummy_dir):
        HEADING()

        assert len(dummy_dir) > 0

    def test_delete(self):
        HEADING()
        del_dir = self.p.delete(service=self.p.service, source=self.testdir, recursive=False)
        while del_dir is None:
            time.sleep(90)
            del_dir = self.p.delete(service=self.p.service, source=self.testdir, recursive=False)

        assert del_dir is not None




