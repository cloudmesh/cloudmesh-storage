import textwrap
import uuid
from multiprocessing import Pool
from pprint import pprint

import oyaml as yaml
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.storage.Provider import Provider


class StorageQueue:
    """
    This class specifies a storage object queue, that allows the queuing of
    files to be copied between services.

    The queue has a maximal parallelism that can be set to execute the copy in
    multiple threads.

    Please note that actions only add modify the queue in the db, however,
    the run command executes them one by one.

    It will be up to the method to guarantee order. For example, in case of a
    recursive copy it would make sense to create directories first.

    """

    """
    DB object

    cm:
       id: uuid
       collection: storage-queue-{source}-{destination}
       ...
    action: copy
    source: the/source/path
    destination: the/destination/path
    created: date
    status:

    Actions can be for example

        copy
        mkdir
        delete
        cancel

    cancel has a specific action allowing all jobs that have not
    yet been finished to be canceled.

    Each file can be in the state: completed, waiting, inprogress, canceled

    here is an example for the status of the queue.
        {
           "length": 100,
           "completed": 10,
           "waiting": 80,
           "inprogress": 10,
           "canceled": 0
        }

    """

    status = [
        'completed',
        'waiting',
        'inprogress',
        'canceled'
    ]

    # def register(self):
    #    # find the inheritor of StorageQueue and register the methd from
    #    # self._put = parent._put

    def redgister_actions(self,
                          put=None,
                          get=None,
                          delete=None,
                          mkdir=None,
                          list=None,
                          cancel=None):

        self._put = put
        self._get = get
        self._delete = delete
        self._mkdir = mkdir
        self._list = list  # attention list
        self._cancel = cancel

    def __init__(self,
                 source,
                 destination,
                 name="local",
                 parallelism=4):
        """
        :param name: The name of the queue (used as a collection in mongodb)
        :param source: The name of the service in cloudmesh.data from which
                       to copy
        :param destination: The name of the service in cloudmesh.data from
                            which to copy
        :param parallelism: The number of parallel threads
        """
        self.source = source
        self.destination = destination
        self.parallelism = parallelism

        config = Config()

        self.source_spec = config[f"cloudmesh.storage.{source}"]
        self.destination_spec = config[f"cloudmesh.storage.{destination}"]

        self.provider_source = Provider(service=source)
        self.provider_destination = Provider(service=destination)

        self.name = name
        self.collection = f"storage-queue-{name}-{source}-{destination}"
        self.number = 0

        #
        # TODO: create collection in mongodb
        #
        Console.ok(f"Collection: {self.name}")

    def _copy_file(self, sourcefile, destinationfile):
        """
        adds a copy action to the queue

        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.

        The copy will not be performed if the files are the same.

        :param sourcefile:
        :param destinationfile:
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
        cm:
           number: {self.number}
           name: "{self.source}:{sourcefile}"
           kind: storage
           id: {uuid_str}
           cloud: {self.collection}
           collection: {self.collection}
           created: {date}
        action: copy
        source:
          service: {self.source}
          path: {sourcefile}
        destination:
          service: {self.destination}
          path: {destinationfile}
        status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def copy_file(self, sourcefile, destinationfile):
        """
        adds a copy action to the queue

        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.

        The copy will not be performed if the files are the same.

        :param sourcefile:
        :param destinationfile:
        :return:
        """
        self._copy_file(sourcefile, destinationfile)

    @DatabaseUpdate()
    def copy_tree(self, sourcetree, destinationtree):
        """
        adds a tree to be copied to the queue
        it will recursively add all files within the tree

        :param sourcetree:
        :param destinationtree:
        :return:
        """
        # goes recursively through the dree and adds_the file

        sources = self.provider_source.list(sourcetree, recursive=True)

        files = []
        dirs = []

        for source in sources:
            if bool(source['file']):
                files.append(source)
            else:
                dirs.append((source))

        # create dirs first

        actions = []

        for file in dirs:
            location = file["cm"]["location"]
            actions.append(self.mkdir(self.destination, location))

        # now copy files

        for file in files:
            location = file["cm"]["location"]
            actions.append(self._copy_file(location, location))
        return actions

    def sync(self, sourcetree, destinationtree):
        """
        just a more convenient name for copy_tree
        :param sourcetree:
        :param destinationtree:
        :return:
        """
        self.copy_tree(sourcetree, destinationtree)

    def mkdir(self, service, path):
        """
        adds a mkdir action to the queue

        create the directory in the storage service
        :param service: service must be either source or destination
        :param path:
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                cm:
                   number: {self.number}
                   name: "{service}:{path}"
                   kind: storage
                   id: {uuid_str}
                   cloud: {self.collection}
                   collection: {self.collection}
                   created: {date}
                action: mkdir
                source:
                  service: {service}
                  path: {path}
                status: waiting
                """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1

        return entries

    def delete(self, service, path):
        """
        adds a deleta action to the queue

        :param service: service must be either source or destination
        :param path:
        :return:
        """
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())
        specification = textwrap.dedent(f"""
                cm:
                   number: {self.number}
                   name: "{service}:{path}"
                   kind: storage
                   id: {uuid_str}
                   cloud: {self.collection}
                   collection: {self.collection}
                   created: {date}
                action: delete
                source:
                  service: {service}
                  path: {path}
                status: waiting
                """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def delete(self, path, recursive=True):
        """
        adds a delete action to the queue

        :param path:
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
                  service: {service}
                  path: {path}
                recursive: {recursive}
                status: waiting
                """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    def status(self):
        """
        provides that status of the queue

        {
           "length": 100,
           "completed": 10,
           "waiting": 80,
           "inprogress": 10
        }

        :return:
        """
        # find all teh values from within the MongoDB
        raise NotImplementedError

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
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def list(self, path, dir_only=False, recursive=False):
        """
        adds a list action to the queue

        list the directory in the storage service
        :param service: service must be either source or destination
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
              action: list
              path: {path}
              dir_only:{dir_only}
              recursive:{recursive}
              status: waiting
        """)
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1

        return entries

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
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        mkdir = []
        copy = []
        list = []
        delete = []
        cancel = []
        for entry in entries:
            pprint(entry)
            if entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                mkdir.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                copy.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                list.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                delete.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                cancel.append(entry)

        return mkdir, copy, list, delete, cancel

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        mkdir_action, copy_action, list_action, delete_action, cancel_action = self.get_actions()

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
