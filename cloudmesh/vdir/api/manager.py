#
# this manager stors directk=ly into the db wit Database update

from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
import os


class Vdir(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    @DatabaseUpdate()
    def mkdir(self):
        pass

    def list(self, parameter):
        print("list", parameter)


    def add(self, endpoint, address):
        print("add", endpoint, address)
        file_dict = {}
        file_dict['cm'] = {}
        cm = file_dict['cm']
        cm['name'] = endpoint
        cm['kind'] = 'vdir'
        cm['cloud'] = 'local'
        cm['directory'] = os.path.dirname(address).split(':')[1]
        cm['filename'] = os.path.basename(address)
        cm['provider'] = os.path.dirname(address).split(':')[0]



'''
cm:
                    name: the unique name of the file
                    kind: vdir
                    cloud: local
                    directory: directory
                    filename: filename
                    provider: provider
                    created: date
                    modified: date
'''
