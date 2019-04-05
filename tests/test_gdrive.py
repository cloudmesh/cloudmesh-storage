##################################################
#
# nosetests -v --nocapture tests/test_gdrive.py
##################################################
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
from cloudmesh.storage.provider.gdrive.Provider import Provider


class TestConfig:

    def setup(self):
        self.config = Config()

    def test_00_config(self):
        HEADING()

        pprint(self.config.dict())

        assert self.config is not None

    def test_01_list(self):
        HEADING()
        p = Provider()
        print(p.listFiles())

        # data = self.config["cloudmesh"]["data"]["mongo"]
        # assert data is not None
