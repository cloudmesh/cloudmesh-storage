##############################################################################
# pytest -v --capture=no tests/test_storage_awss3.py
# pytest -v  tests/test_storage_awss3.py
# pytest -v --capture=no -v --nocapture tests/test_storage_awss3.py:Test_storage_awss3.<METHIDNAME>
################################################################################
import os
from pprint import pprint

import cloudmesh.storage.provider.awss3.Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.common.StopWatch import StopWatch
import pytest
import time

@pytest.mark.incremental
class Test_storage_awss3:

      def create_file(self, location, content):

        d = Path(os.path.dirname(path_expand(location)))
        print()
        print ("TESTDIR:",  d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def setup(self):
        StopWatch.start("awss3 setup")        
        self.p = cloudmesh.storage.provider.awss3.Provider.Provider(service="awss3")
        StopWatch.stop("awss3 setup")

        print('Success')
        assert Fasle # no assertion provided


    def test_01_create_source(self):
        StopWatch.start("awss3 create source")

        self.destination = path_expand("~/.cloudmesh/storage/stest/")
        self.sourcedir = path_expand("~/.cloudmesh/storage/stest/")

        self.create_file("~/.cloudmesh/storage/stest/stest.txt", "content of stest")
        self.create_file("~/.cloudmesh/storage/stest/stest1.txt", "content of stest1")
        StopWatch.stop("awss3 create source")

        # test if the files are ok
        assert False # no assertion provided


    def test_01_create_dir(self):
        HEADING()
        src = 'created_dir123'
        src1 = 'created_dir123/subdir_create123'

        StopWatch.start("awss3 create dir")
        dir = self.p.create_dir(self.p.service, src)
        dir = self.p.create_dir(self.p.service, src1)
        StopWatch.stop("awss3 create dir")
        pprint(dir)

        assert dir is not None

    def test_02_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/stest/stest.txt")
        print(src)
        dst = "/created_dir123"
        print(dst)
        StopWatch.start("awss3 put")
        test_file = self.p.put(self.p.service, src, dst)
        StopWatch.stop("awss3 put")
        pprint(test_file)
        assert test_file is not None

    def test_03_get(self):
        HEADING()
        src = path_expand("/created_dir123/stest.txt")
        print(src)
        dst = path_expand("~/.cloudmesh/storage/stest/testget.txt")
        print(dst)
        StopWatch.start("awss3 get")
        file = self.p.get(self.p.service, src, dst)
        StopWatch.stop("awss3 get")
        pprint(file)
        assert file is not None

    def test_04_list(self):
        HEADING()
        src = '/created_dir123'
        StopWatch.start("awss3 list")
        contents = self.p.list(self.p.service, src)
        StopWatch.stop("awss3 list")

        for c in contents:
            pprint(c)
        assert len(contents) > 0

    def test_05_search(self):
        HEADING()
        src = '/created_dir123'
        filename = 'stest.txt'
        StopWatch.start("awss3 search")
        search_files = self.p.search(self.p.service,    src, filename, True)
        StopWatch.stop("awss3 search")
        pprint(search_files)
        assert len(search_files) > 0

    def test_06_delete(self):
        HEADING()
        src = '/created_dir123/subdir_create123'
        StopWatch.start("awss3 delete")
        self.p.delete(self.p.service, src)
        StopWatch.stop("awss3 delete")

    def test_results(self):
        HEADING()

        StopWatch.benchmark()
