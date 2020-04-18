import textwrap
import uuid
from abc import ABCMeta, abstractmethod
from multiprocessing import Pool

import oyaml as yaml
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.debug import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class StorageQueue(metaclass=ABCMeta):
    # status = [
    #     'completed',
    #     'waiting',
    #     'inprogress',
    #     'canceled'
    # ]

    def __init__(self,
                 name=None,
                 parallelism=4):
        """
        TBD

        :param service: TBD
        :param config: TBD
        """
        self.name = name
        self.parallelism = parallelism
        self.config_path = config

        self.collection = f"storage-queue-{name}"
        self.number = 0

    @DatabaseUpdate()
    def copy(self, sourcefile, destinationfile, recursive=False):
        """
        adds a copy action to the queue

        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.

        The copy will not be performed if the files are the same.

        :param sourcefile:
        :param destinationfile:
        :param recursive:
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{sourcefile}:{destinationfile}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            action: copy
            source: 
              path: {sourcefile}
            destination: 
              path: {destinationfile}
            recursive: {recursive}
            status: waiting
        """)
        #
        # TODO: consider
        #
        # removing cm from the specification and using
        #
        # specification = textwrap.dedent(f"""
        #             action: copy
        #             source:
        #               path: {sourcefile}
        #             destination:
        #               path: {destinationfile}
        #             recursive: {recursive}
        #             status: waiting
        #         """)
        #
        # specification = self._add_cm(**locals()) + specification.strip() + "\n"
        #
        # EVALUATE and adapt
        #

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        # todo: this increment wouldn't work because at each call, there will be a new instance of the class
        self.number = self.number + 1
        return entries

    @abstractmethod
    def _put(self, specification: dict) -> dict:
        """
        function to upload file or directory
        puts the source on the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory
                            or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """
        raise NotImplementedError

    # TODO: make indentations of the yaml uniform, see delete, do this for all
    @DatabaseUpdate()
    def delete(self, path, recursive=True):
        """
        adds a delete action to the queue

        :param path:
        :param recursive:

        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{path}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            action: delete
            source: 
              path: {path}
            recursive: {recursive}
            status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        # todo: this increment wouldn't work because at each call, there will be a new instance of the class
        self.number = self.number + 1
        return entries

    # function to delete file or directory
    @abstractmethod
    def _delete(self, specification: dict) -> dict:
        """
        deletes the source

        :param specification:

        :return: dict

        """
        raise NotImplementedError

    # BUG: THis should ideally be name and not id. THis has impact on all
    # providers as there may be a bug in the cancel methods including the ABC
    # class.
    @DatabaseUpdate()
    def cancel(self, id=None):
        """
        cancels a job with a specific id
        :param id:
        :return:
        """
        # if None all are canceled
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{id}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            action: cancel
            status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        # todo: this increment wouldn't work because at each call, there will be a new instance of the class
        self.number = self.number + 1
        return entries

    @abstractmethod
    def _cancel(self, specification: dict) -> dict:
        raise NotImplementedError

    @DatabaseUpdate()
    def mkdir(self, path):
        """
        adds a mkdir action to the queue

        create the directory in the storage service
        :param path:
        :return:
        """

        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                  cm:
                    number: {self.number}
                    kind: storage
                    id: {uuid_str}
                    cloud: {self.name}
                    name: {path}
                    collection: {self.collection}
                    created: {date}
                  action: mkdir
                  path: {path}
                  status: waiting
            """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        # todo: this increment wouldn't work because at each call, there will be a new instance of the class
        self.number = self.number + 1

        return entries

    @abstractmethod
    def _mkdir(self, specification: dict) -> dict:
        """
        function to create a directory the function will first check if the
        bucket exists or not,if the bucket doesn't exist it will create the
        bucket and it will create the directory specified. the name of the
        bucket will come from YAML specifications and the directory name comes
        from the arguments.

        :param specification:
        :return:
        """
        #     cm:
        #     number: {self.number}
        #     kind: storage
        #     id: {uuid_str}
        #     cloud: {self.name}
        #     name: {path}
        #     collection: {self.collection}
        #     created: {date}
        #
        # action: mkdir
        # path: {path}
        # status: waiting

        raise NotImplementedError

    @DatabaseUpdate()
    def list(self, path, dir_only=False, recursive=False):
        """
        adds a list action to the queue

        list the directory in the storage service
        :param path:
        :param dir_only:
        :param recursive:

        :return:
        """

        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
              cm:
                number: {self.number}
                kind: storage
                id: {uuid_str}
                cloud: {self.name}
                name: {path}
                collection: {self.collection}
                created: {date}
              action: list
              path: {path}
              dir_only:{dir_only}
              recursive:{recursive}
              status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        # todo: this increment wouldn't work because at each call, there will be a new instance of the class
        self.number = self.number + 1

        return entries

    @abstractmethod
    def _list(self, specification: dict) -> dict:
        """
        lists the information as dict

        :param specification.source: the source which either can be a directory or file
        :param specification.dir_only: Only the directory names
        :param specification.recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source

        :return: dict

        """
        raise NotImplementedError

    def action(self, specification):
        """
        executes the action identified by the specification. This is used by the
        run command.

        :param specification:
        :return:
        """
        action = specification["action"]
        if action == "copy":
            # print("COPY", specification)
            specification = self._put(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "delete":
            # print("DELETE", specification)
            specification = self._delete(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "mkdir":
            # print("MKDIR", specification)
            specification = self._mkdir(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "list":
            # print("LIST", specification)
            specification = self._list(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "cancel":
            specification = self._cancel(specification)
            self.update_dict(elements=[specification])

    def get_actions(self):
        """
        TODO: missing

        :return:
        """
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        _mkdir = []
        _copy = []
        _list = []
        _delete = []
        _cancel = []
        for entry in entries:
            VERBOSE(entry)
            if entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                _mkdir.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                _copy.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                _list.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                _delete.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                _cancel.append(entry)

        return _mkdir, _copy, _list, _delete, _cancel

    @DatabaseUpdate()
    def update_dict(self, elements, kind=None):
        """
        this is an internal function for building dict object

        :param elements:
        :param kind:
        :return:
        """
        d = []
        for element in elements:
            # entry = element.__dict__
            # entry = element['objlist']
            entry = element

            # element.properties = element.properties.__dict__
            d.append(entry)
        return d

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        mkdir_action, \
        copy_action, \
        list_action, \
        delete_action, \
        cancel_action = self.get_actions()

        # cancel the actions
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, cancel_action)

        # delete files/directories
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, delete_action)

        # create directories
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, mkdir_action)

        # COPY FILES
        #
        p = Pool(self.parallelism)
        #
        p.map(self.action, copy_action)

        # LIST FILES
        p = Pool(self.parallelism)
        p.map(self.action, list_action)

        # function to list file  or directory


if __name__ == "__main__":
    p = Provider(name="aws")
    # p.mkdir("/abcworking2")
    # p.mkdir("/abcworking3")
    # p.mkdir("/abcworking4")
    # p.mkdir("/abcworking5")
    # p.mkdir("/abcworking6")

    # p.list('/')
    # p.run()
    # p.cancel()
    # p.delete(path="testABC")
    # p.copy(sourcefile="./Provider.py", destinationfile="testABC.txt")

    p.run()
