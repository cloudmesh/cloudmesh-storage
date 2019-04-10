import os
from pprint import pprint
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.provider.box.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from pathlib import Path
import os


# nosetest -v --nopature
# nosetests -v --nocapture tests/test_box.py

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

    def test_00_config(self):
        config = Config()
        storage = config['cloudmesh.storage']
        print(storage)

    def test_01_provider(self):
        self.p = Provider(service="box")
        os.makedirs(os.path.join(path_expand('~/.cloudmesh'), 'storage', 'test', 'box'), exist_ok=True)
        writefile(os.path.join(path_expand('~/.cloudmesh/storage/test/box'), 'test.txt'), 'Test content')
        self.destination = "/"
        self.source = path_expand('~/.cloudmesh/storage/test/box/test.txt')
        file = open(self.source)

        assert file.read() == 'Test content'

    def test_02_put(self):
        HEADING()
        test_file = self.p.put(service=self.p.service, source=self.source_file, destination=self.destination, recursive=False)
        pprint(test_file)

        assert test_file is not None

    def test_03_get(self):
        HEADING()
        file = self.p.get(service=self.p.service, source=self.destination_file, destination=self.source, recursive=False)
        pprint(file)

        assert file is not None

    def test_04_list(self):
        HEADING()
        contents = self.p.list(service=self.p.service, source=self.destination, recursive=False)
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_04_search(self):
        HEADING()
        search_files = self.p.search(service=self.p.service, directory=self.destination, filename=self.filename, recursive=False)
        pprint(search_files)

        assert len(search_files) > 0

class Junk:

    def test_05_create_dir(self):
        HEADING()
        # TODO use named arguments
        dir = self.p.create_dir('/testdir')
        pprint(dir)

        assert dir is not None

    def test_06_delete(self):
        HEADING()
        # TODO use named arguments
        self.p.delete('testdir')
