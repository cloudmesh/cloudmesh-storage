import cloudmesh.storage.provider.box.Provider
from pprint import pprint
from cloudmesh.common.util import path_expand
import os

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_box.py

class TestBox:

    def setup(self):
        self.p = cloudmesh.storage.provider.box.Provider.Provider()

    def test_01_put(self):
        src_path = path_expand('~/test_folder')
        if not os.path.exists(src_path):
            os.makedirs(src_path)
        f = open(src_path+'/test.txt', 'w')
        test_file = self.p.put('~/test_folder/test.txt', '/')
        pprint(test_file)

        assert test_file is not None

    def test_02_get(self):
        self.test_01_put()
        file = self.p.get('/test.txt', '~/test_folder')
        pprint(file)

        assert file is not None

    def test_03_list(self):
        contents = self.p.list('/')
        for c in contents:
            pprint(c)

        assert len(contents) > 0

    def test_04_search(self):
        search_files = self.p.search('/', 'test.txt', True)
        pprint(search_files)

        assert len(search_files) > 0

    def test_05_create_dir(self):
        dir = self.p.create_dir('/testdir')
        pprint(dir)

        assert dir is not None

    def test_06_delete(self):
        self.p.delete('testdir')



















