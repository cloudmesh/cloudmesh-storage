###############################################################
# pytest -v --capture=no tests/test_gdrive.py
# pytest -v  tests/test_gdrive.py
# pytest -v --capture=no tests/test_gdrive.py:TestGdrive.<METHIDNAME>
###############################################################

import os
from pathlib import Path
from pprint import pprint

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.run.file import run
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.storage.provider.gdrive.Provider import Provider


def execute(command):
    StopWatch.start(command)
    output = run(command)
    StopWatch.stop(command)
    return output


@pytest.mark.incremental
class TestGdrive(object):

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        d.mkdir(parents=True, exist_ok=True)
        writefile(path_expand(location), content)

    def setup(self):
        self.p = Provider(service="gdrive")
        self.destination = path_expand("/")
        self.source = path_expand("~/.cloudmesh/storage/test/source/")
        self.create_file(
            "~/.cloudmesh/storage/test/source/test/source/sample_source.txt",
            "This is sample test file")
        assert True

    def test_put(self):
        HEADING()
        src = path_expand(
            "~/.cloudmesh/storage/test/source/test/source/sample_source.txt")
        dst = "/"
        # Put files from src into google drive home directory

        test_file = run(f"cms put {src} {dst}")
        # test_file = self.p.put(source=src, destination=dst, recursive=False)

        print(test_file)
        assert test_file is not None

    def test_get(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/source/test/source/")
        dst = 'Useful Links.txt'
        # fetching files from dst to src
        # file = self.p.get(source=src, destination=dst, recursive=False)
        file = run(f"cms get {src} {dst}")

        assert file is not None

    def test_list(self):
        HEADING()
        # Listing files google drive home directory
        # contents = self.p.list(source='/', recursive=True)
        src = '/'
        recursive = True
        contents = execute(f"cms list {src} {recursive}")
        print("check contents")
        print(contents)
        assert len(contents) > 0

    def test_search(self):
        HEADING()
        # Searching sample_source.txt which is created earlier in home directory
        # search_files = self.p.search(
        #                    directory='/',
        #                    filename='Useful Links.txt', recursive=True)
        directory = '/'
        filename = 'Useful Links.txt'
        recursive = True
        search_files = execute(f"cms search {directory} {filename} {recursive}")
        pprint(search_files)
        assert search_files

    def test_create_dir(self):
        HEADING()
        # Creating testdir in home directory of google drive
        # dir = self.p.create_dir(directory='/testdir')
        directory = '/testdir'
        directory = execute(f"cms create_dir {directory}")
        assert directory is not None

    def test_delete(self):
        HEADING()
        # Deleting in google drive home sample_source.txt
        # message = self.p.delete(filname='sample_source.txt')
        filname = 'sample_source.txt'
        message = run(f"cms delete {filname}")

        assert message is not None

    def test_benchmark(self):
        StopWatch.benchmark()
