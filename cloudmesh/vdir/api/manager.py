#
# this manager stors directk=ly into the db wit Database update

from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.console import Console
from cloudmesh.storage.Provider import Provider
from pprint import pprint
import os
from datetime import datetime


class Vdir(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))
        self.cm = CmDatabase()
        self.col = self.cm.db['local-vdir']
        self.directory = ''

    def cd(self, dirname=None):
        try:
            if dirname is None:
                if self.directory == '':
                    Console.error("Root directory reached.")
                else:
                    cwd = self.col.find_one({'type':'directory', 'cm.name':self.directory})
                    print(cwd)
                    self.directory = cwd['parent']
            else:
                directory = self.col.find_one({'type': 'directory', 'cm.name': dirname})
                print(directory)
                if directory['parent'] == self.directory:
                    self.directory = dirname
                else:
                    Console.error('Directory does not exist at this location.')
            print(self.directory)
        except Exception as e:
            print(e)


    @DatabaseUpdate()
    def mkdir(self, dirname):
        try:
            dir_dict = dict()
            dir_dict['cm'] = {}
            cm = dir_dict['cm']
            cm['name'] = dirname
            cm['kind'] = 'vdir'
            cm['cloud'] = 'local'
            dir_dict['type'] = 'directory'
            dir_dict['parent'] = self.directory
            cm['created'] = datetime.utcnow()
            cm['modified'] = datetime.utcnow()
            print(dir_dict)
            return dir_dict
        except Exception as e:
            print(e)

    def ls(self, directory=None):
        try:
            dash = '-' * 40
            if directory is not None:
                cloudmesh = self.col.find({'$or':[{'vdirectory': directory}, {'parent': directory}]})
                count = self.col.count_documents({'$or':[{'vdirectory': directory}, {'parent': directory}]})
            else:
                cloudmesh = self.col.find({'$or':[{'vdirectory': self.directory}, {'parent': self.directory}]})
                count = self.col.count_documents({'$or':[{'vdirectory': self.directory}, {'parent': self.directory}]})
            locations = "{:<20} {:>}".format("Name", "Location")+"\n"+dash+"\n"
            for i in range(0, count):
                entry = cloudmesh[i]
                if entry['type'] == 'fileendpoint':
                    location = entry['provider']+":"+ entry['cloud_directory']+"/"+entry['filename']
                else:
                    if self.directory == '':
                        location = 'Vdir'
                    else:
                        location = self.directory
                locations += "{:<20} {:>}".format(entry['cm']['name'], location)+"\n"
            print(locations)
            return locations
        except Exception as e:
            print(e)

    @DatabaseUpdate()
    def add(self, endpoint, dir_and_name):
        try:
            dirname = os.path.dirname(dir_and_name).split('/')[-1]
            filename = os.path.basename(dir_and_name)
            directory = self.col.find_one({"cm.name": dirname, 'type': 'directory'})
            file = self.col.find_one({"cm.name": filename, 'type':'fileendpoint'})
            if directory is not None and file is None:
                file_dict = dict()
                file_dict['cm'] = {}
                cm = file_dict['cm']
                cm['name'] = filename
                cm['kind'] = 'vdir'
                cm['cloud'] = 'local'
                file_dict['type'] = 'fileendpoint'
                file_dict['vdirectory'] = dirname
                file_dict['cloud_directory'] = os.path.dirname(endpoint).split(':')[1]
                file_dict['filename'] = os.path.basename(endpoint)
                file_dict['provider'] = os.path.dirname(endpoint).split(':')[0]
                cm['created'] = datetime.utcnow()
                cm['modified'] = datetime.utcnow()
                print(file_dict)
                return file_dict
            elif directory is None:
                Console.error("Virtual directory",dirname," not found.")
            elif file is not None:
                Console.error("File with that name already exists.")
        except Exception as e:
            print(e)

    def get(self, name):
        try:
            doc = self.col.find_one({'cm.name': name, 'cm.type': 'fileendpoint'})
            if doc is not None:
                cm = doc['cm']
                service = cm['provider']
                source = os.path.join(cm['cloud_directory'], cm['filename'])
                destination = '~/.cloudmesh'
                p = Provider(service)
                file = p.get(source, destination, False)
                return file
            else:
                Console.error("File not found.")
        except Exception as e:
            print(e)

    def delete(self, dir_or_name):
        pass
