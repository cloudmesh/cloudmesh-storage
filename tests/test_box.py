from pprint import pprint
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.provider.box.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
import os
import pytest


# nosetest -v --nopature
# nosetests -v --nocapture tests/test_box.py
# pytest tests/test_box.py

@pytest.mark.incremental
class TestBox:

    def setup(self):
        self.p = Provider(service="box")
        os.makedirs(os.path.join(path_expand('~/.cloudmesh'), 'storage', 'test', 'box'), exist_ok=True)
        writefile(os.path.join(path_expand('~/.cloudmesh/storage/test/box'), 'test.txt'), 'Test content')
        self.destination = "/"
        self.destination_file = '/test.txt'
        self.source = path_expand('~/.cloudmesh/storage/test/box')
        self.source_file = path_expand('~/.cloudmesh/storage/test/box/test.txt')
        self.filename = 'test.txt'

    @pytest.fixture(scope='class')
    def test_dir(self):
        self.p = Provider(service="box")
        self.destination = "/"
        test_dir = self.p.create_dir(service=self.p.service, directory=os.path.join(self.destination, 'testdir'))
        return test_dir

    def test_00_config(self):
        config = Config()
        storage = config['cloudmesh.storage']
        print(storage)

    def test_01_provider(self):
        file = open(self.source_file)

        assert file.read() == 'Test content'

    def test_02_put(self):
        HEADING()
        test_file = self.p.put(service=self.p.service, source=self.source_file,
                               destination=self.destination, recursive=False)
        pprint(test_file)

        assert test_file is not None

    def test_03_get(self):
        HEADING()
        file = self.p.get(service=self.p.service, source=self.destination_file,
                          destination=self.source, recursive=False)
        pprint(file)

        assert file is not None

    def test_04_list(self):
        HEADING()
        contents = self.p.list(service=self.p.service, source=self.destination, recursive=False)
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_05_search(self):
        HEADING()
        search_files = self.p.search(service=self.p.service, directory=self.destination,
                                     filename=self.filename, recursive=False)
        pprint(search_files)

        assert len(search_files) > 0

    def test_06_create_dir(self, test_dir):
        HEADING()

        assert len(test_dir) > 0

    def test_07_delete(self, test_dir):
        HEADING()
        self.p.client.folder(test_dir[0]['id']).delete()

