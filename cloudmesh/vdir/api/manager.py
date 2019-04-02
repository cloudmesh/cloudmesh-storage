#
# this manager stors directk=ly into the db wit Database update

from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

class Vdir(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    @DatabaseUpdate
    def mkdir(self):
        pass

    def list(self, parameter):
        print("list", parameter)
