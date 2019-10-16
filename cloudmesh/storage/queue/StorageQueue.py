from multiprocessing import Pool
import textwrap
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider
from pprint import pprint
import oyaml as yaml
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
import uuid
from cloudmesh.common3.DateTime import DateTime

class StorageQueue:
    """
    This class specifies a storage object queue, that allows the queuing of
    files to be copied between services.

    The queue has a maximal parallelism that can be set to execute the copy in
    multiple threads.

    Please note that actions only add modify the queue in the db, however,
    the run command executes them one by one.

    It will be up to thes method to quarantee order. For example, in case of a
    recursive copy it wwould make sens to create directories first.

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

    def __init__(self,
                 source,
                 destination,
                 name="local",
                 parallelism=4):
        """
        :param name: The name of the queue (used as a collection in mongodb)
        :param source: The name of the service in cloudmesh.data from which to copy
        :param destination: The name of the service in cloudmesh.data from which to copy
        :param parallelism: The number of parallel threads
        """
        self.source = source
        self.destination = destination
        self.paralelism = parallelism

        config = Config()

        self.source_spec = config[f"cloudmesh.storage.{source}"]
        self.destination_spec = config[f"cloudmesh.storage.{destination}"]



        self.provider_source = Provider(service=source)
        self.provider_destination = Provider(service=destination)

        self.name = name
        self.collection = f"storage-queue-{name}-{source}-{destination}"

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
           name: "{self.source}:{sourcefile}"
           kind: storage
           id: {uuid_str}
           cloud: {self.collection}
           collection: {self.collection}
           created: {date}
        action: copy
        source: {self.source}:{sourcefile}
        destination: {self.destination}:{destinationfile}
        status: waiting
        """)
        entries = yaml.load(specification)

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

    def copy_tree(self, sourcetree, destinationtree):
        """
        adds a tree to be copied to the queue
        it will recursively add all files within the tree

        :param sourcetree:
        :param destinationtree:
        :return:
        """
        # goes recursively through the dree and adds_the file

        source_files = self.provider_source.list(sourcetree, recursive=True)

        # create dirs first

        files = []
        for file in source_files:
            location = file["cm"]["location"]
            files.append(self._copy_file(location, location))
        return files

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
        date = "1 Dec 2019 7:00" # define a uniform time function in cloudmesh.common
        specification = textwrap.dedent(f"""
        cm:
           id: uuid
           collection: storage-queue-{self.source}-{self.destination}
        action: mkdir
        source: {self.service}:{path}
        created: {date}
        status: waiting
        """)
        print (specification)



    def delete(self, service, path):
        """
        adds a deleta action to the queue

        :param service: service must be either source or destination
        :param path:
        :return:
        """
        date = "1 Dec 2019 7:00" # define a uniform time function in cloudmesh.common
        specification = textwrap.dedent(f"""
        cm:
           id: uuid
           collection: storage-queue-{self.source}-{self.destination}
        action: delete
        source: {self.service}:{path}
        created: {date}
        status: waiting
        """)
        print (specification)


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

    def cancel(self, id=None):
        """
        cancels a job with a specific id
        :param id:
        :return:
        """
        # if None all are canceled
        raise NotImplementedError

    def get(self):
        """
        this is a threadsafe method that gets a single job from the queue
        :return:
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
            raise NotImplementedError
        elif action == "delete":
            raise NotImplementedError
        elif action == "mkdir":
            raise NotImplementedError
        elif action == "delete":
            raise NotImplementedError

    def do_action(self):
        specification = self.get()
        self.action(specification)

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all actions are completed

        :return:
        """
        # sequential

        # while there are still jobs in the queue:
        #    job = get()
        #    action (specification)

        # parallel
        #
        # p = Pool(self.parallelism)
        #
        # p.map(do_action)
        raise NotImplementedError







