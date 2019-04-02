class Provider(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def put(self, filename):
        print("put", filename)

    def get(self, filename):
        print("box provider get", filename)

    def delete(self, filename):
        print("put", filename)
