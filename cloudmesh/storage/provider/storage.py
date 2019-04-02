from cloudmesh.abstractclass.StorageABC import StorageABC


# from cloudmesh.storag.google.Provider import Provider as GoogleStorageProvider
# from cloudmesh.bostorage.box.Provider import Provider as GoogleBoxProvider


class Provider(StorageABC):

    def __init__(self, cloud, config):
        '''
        if cloud == 'google':
            self.p = GoogleStorageProvider


        '''
        raise NotImplementedError

    def create_dir(self, service=None, directory=None):
        """
        creates a directory

        :param service: the name of the service in the yaml file
        :param directory: the name of the directory
        :return: dict
        """
        raise NotImplementedError

    # @DatabaseUpdate
    def list(self, service=None, source=None, recursive=False):
        """
        lists the information as dict

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError

    def put(self, service=None, source=None, destination=None, recusrive=False):
        """
        puts the source on the service

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError

    def get(self, service=None, source=None, destination=None, recusrive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError

    def delete(self, service=None, source=None, recusrive=False):
        """
        deletes the source

        :param service: the name of the service in the yaml file
        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError

    def search(self, service=None, directory=None, filename=None,
               recusrive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
