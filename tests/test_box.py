###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_box.py:Test_box.test_001
# pytest -v --capture=no tests/test_boxr.py
# pytest -v  tests/test_installer.py
###############################################################
from pprint import pprint
from cloudmesh.management.configuration.config import Config
from cloudmesh.storage.provider.box.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
import os
import pytest
from pathlib import Path

@pytest.mark.incremental
class Test_box:

    def setup(self):
        self.p = Provider(service="box")
        self.source = location = path_expand('~/.cloudmesh/storage/test/box')
        self.source_file = source = path_expand(f'{location}/test.txt')

        os.makedirs(self.box_location, exist_ok=True)
        writefile(Path(source, 'Test content'))
        self.destination = "/"
        self.destination_file = '/test.txt'
        self.filename = 'test.txt'

    @pytest.fixture(scope='class')
    def dummy_dir(self):
        self.p = Provider(service="box")
        destination = self.destination = "/"
        test_dir = self.p.create_dir(service=self.p.service,
                                     directory=f"destination/testdir")
        return test_dir
        # bug assertion missing

    def test_config(self):
        config = Config()
        storage = config['cloudmesh.storage']
        print(storage)

    def test_provider(self):
        file = open(self.source_file)

        assert file.read() == 'Test content'

    def test_put(self):
        HEADING()
        test_file = self.p.put(service=self.p.service,
                               source=self.source_file,
                               destination=self.destination,
                               recursive=False)
        pprint(test_file)

        assert test_file is not None

    def test_get(self):
        HEADING()
        file = self.p.get(service=self.p.service,
                          source=self.destination_file,
                          destination=self.source,
                          recursive=False)
        pprint(file)

        assert file is not None

    def test_list(self):
        HEADING()
        contents = self.p.list(service=self.p.service,
                               source=self.destination,
                               recursive=False)
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_search(self):
        HEADING()
        search_files = self.p.search(service=self.p.service,
                                     directory=self.destination,
                                     filename=self.filename,
                                     recursive=False)
        pprint(search_files)

        assert len(search_files) > 0

    def test_create_dir(self, test_dir):
        HEADING()

        assert len(test_dir) > 0

    def test_delete(self, test_dir):
        HEADING()
        self.p.client.folder(test_dir[0]['id']).delete()




