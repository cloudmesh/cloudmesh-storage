#
# this manager stors directk=ly into the db wit Database update

from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.storage.provider.storage import Provider
from cloudmesh.common.console import Console
from pprint import pprint
import os
from datetime import datetime


class Vdir(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))
        self.cm = CmDatabase()
        self.col = self.cm.db['local-vdir']
        self.storage = Provider()


    @DatabaseUpdate()
    def mkdir(self):
        pass

    def ls(self, directory):
        print("list", directory)
        cloudmesh = self.col.find({})
        count = self.col.count_documents({})
        for i in range(0, count):
            print(cloudmesh[i]['cm']['name'])

    @DatabaseUpdate()
    def add(self, endpoint, dir_and_name):
        try:
            file_dict = dict()
            file_dict['cm'] = {}
            cm = file_dict['cm']
            cm['name'] = endpoint
            cm['kind'] = 'vdir'
            cm['cloud'] = 'local'
            cm['directory'] = os.path.dirname(dir_and_name).split(':')[1]
            cm['filename'] = os.path.basename(dir_and_name)
            cm['provider'] = os.path.dirname(dir_and_name).split(':')[0]
            cm['created'] = datetime.utcnow()
            cm['modified'] = datetime.utcnow()
            return file_dict
        except Exception as e:
            print(e)

    def get(self, name):
        doc = self.col.find_one({'cm.name':name})
        if doc is not None:
            cm = doc['cm']
            service = cm['provider']
            path = os.path.join(cm['directory'], cm['filename'])
