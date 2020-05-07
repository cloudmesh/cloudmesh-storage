import textwrap
import time
import uuid
import os
from multiprocessing import Pool

import oyaml as yaml
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.Printer import Printer
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.abstract.StorageABC import StorageABC
from cloudmesh.common.util import path_expand


class StorageQueue(StorageABC):

    def __init__(self, service=None, parallelism=4):
        super().__init__(service=service)
        self.parallelism = parallelism
        self.name = service
        self.collection = f"storage-queue-{service}"
        self.number = 0
        self.storage_dict = {}

    def pretty_print(self, data, data_type, output=None):
        if output == "table":
            order = self.output[data_type]['order']  # not pretty
            header = self.output[data_type]['header']  # not pretty
            sort_keys = self.output[data_type]['sort_keys']
            print(Printer.flatwrite(data,
                                    sort_keys=sort_keys,
                                    order=order,
                                    header=header,
                                    output=output,
                                    )
                  )
        else:
            print(Printer.write(data, output=output))

    @DatabaseUpdate()
    def update_dict(self, elements):
        """
        this is an internal function for building dict object
        :param elements:
        :return:
        """
        d = []
        for element in elements:
            entry = element
            d.append(entry)
        return d

    #
    # keep those with the raised as we can inherit form this class an than
    # overwrite the _ functions
    #
    def _notimplemented(self, specification):
        """

        :param specification:
        :return:
        """
        raise NotImplementedError

    #
    # not sure if the next thing works, if not duplicate
    #
    put_run = _notimplemented
    get_run = _notimplemented
    mkdir_run = _notimplemented
    cancel_run = _notimplemented
    delete_run = _notimplemented
    copy_run = _notimplemented
    list_run = _notimplemented
    search_run = _notimplemented

    def add_cm(self, cm_name):
        date = DateTime.now()
        uuid_str = str(uuid.uuid1())

        spec = textwrap.dedent(
            f"""
            cm:
               number: {self.number}
               name: "{cm_name}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
            """
        ).strip() + "\n"

        return spec

    @DatabaseUpdate()
    def copy(self, sourcefile, destinationfile, recursive=False):
        """
        adds a copy action to the queue
        copies the file from the source service to the destination service using
        the file located in the path and storing it into the remote. If remote
        is not specified path is used for it.
        The copy will not be performed if the files are the same.
        :param sourcefile: The source file to copy
        :param destinationfile: The destination file path
        :param recursive: whether or not copy the file/dir recursively
        :return:
        """
        specification = textwrap.dedent(
            f"""
            action: copy
            source: {sourcefile}
            destination: {destinationfile}
            recursive: {recursive}
            status: waiting
            """
        )
        common_cm = self.add_cm(cm_name=f"{sourcefile}:{destinationfile}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def delete(self, source, recursive=True):
        """
        adds a delete action to the queue

        :param source:
        :param recursive:
        :return:
        """
        specification = textwrap.dedent(
            f"""
               action: delete
               path: {source}
               recursive: {recursive}
               status: waiting
               """
        )
        common_cm = self.add_cm(cm_name=f"{source}")
        specification = common_cm + specification.strip() + "\n"
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def search(self, directory=None, filename=None, recursive=False):
        specification = textwrap.dedent(
            f"""
                action: search
                path: {directory}
                filename: {filename}
                recursive: {recursive}
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{directory}:{filename}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    #
    # BUG: THis should ideally be name and not id. THis has impact on all
    # providers as there may be a bug in the cancel methods including the ABC
    # class.
    #
    @DatabaseUpdate()
    def cancel(self, name=None):
        """
        cancels a job with a specific id
        :param name:
        :return:
        """
        # if None all are canceled
        specification = textwrap.dedent(
            f"""
                action: cancel
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{name}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def get(self, source, destination, recursive=False):
        specification = textwrap.dedent(
            f"""
                action: get
                source: {source}
                destination: {destination}
                recursive: {recursive}
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{source}:{destination}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def put(self, source, destination, recursive=False):
        specification = textwrap.dedent(
            f"""
                action: put
                source: {path_expand(source)}
                destination: {destination}
                recursive: {recursive}
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{source}:{destination}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def create_dir(self, directory):
        """
        adds a mkdir action to the queue
        create the directory in the storage service
        :param directory:
        :return:
        """
        specification = textwrap.dedent(
            f"""
                action: mkdir
                path: {directory}
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{directory}")
        specification = common_cm + specification.strip() + "\n"

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    @DatabaseUpdate()
    def list(self, source, dir_only=False, recursive=False):
        """
        adds a list action to the queue
        list the directory in the storage service
        :param source:
        :param dir_only:
        :param recursive:
        :return:
        """
        specification = textwrap.dedent(
            f"""
                action: list
                path: {source}
                dir_only: {dir_only}
                recursive: {recursive}
                status: waiting
                """
        )
        common_cm = self.add_cm(cm_name=f"{source}")
        specification = common_cm + specification.strip() + "\n"

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
            specification = self.put_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "delete":
            specification = self.delete_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "mkdir":
            specification = self.mkdir_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "list":
            specification = self.list_run(specification)
            # update status
            self.update_dict(elements=[specification])
        elif action == "cancel":
            specification = self.cancel_run(specification)
            self.update_dict(elements=[specification])
        elif action == "get":
            specification = self.get_run(specification)
            self.update_dict(elements=[specification])
        elif action == "put":
            specification = self.put_run(specification)
            self.update_dict(elements=[specification])
        elif action == "search":
            specification = self.search_run(specification)
            self.update_dict(elements=[specification])

    def get_actions(self):
        """
        get all the actions from database
        param:
        :return lists of actions from database
        """
        cm = CmDatabase()
        entries = cm.find(cloud=self.name,
                          kind='storage')
        get_actions = []
        put_actions = []
        mkdir_actions = []
        copy_actions = []
        list_actions = []
        delete_actions = []
        cancel_actions = []
        search_actions = []

        for entry in entries:
            if entry['action'] == 'get' and entry['status'] == 'waiting':
                get_actions.append(entry)
            elif entry['action'] == 'put' and entry['status'] == 'waiting':
                put_actions.append(entry)
            elif entry['action'] == 'mkdir' and entry['status'] == 'waiting':
                mkdir_actions.append(entry)
            elif entry['action'] == 'copy' and entry['status'] == 'waiting':
                copy_actions.append(entry)
            elif entry['action'] == 'list' and entry['status'] == 'waiting':
                list_actions.append(entry)
            elif entry['action'] == 'delete' and entry['status'] == 'waiting':
                delete_actions.append(entry)
            elif entry['action'] == 'cancel' and entry['status'] == 'waiting':
                cancel_actions.append(entry)
            elif entry['action'] == 'search' and entry['status'] == 'waiting':
                search_actions.append(entry)

        return get_actions, put_actions, mkdir_actions, copy_actions, \
               list_actions, delete_actions, cancel_actions, search_actions

    def run(self):
        """
        runs the copy process for all jobs in the queue and completes when all
        actions are completed

        :return:
        """
        get_action, put_action, mkdir_action, copy_action, list_action, \
        delete_action, cancel_action, search_action = self.get_actions()

        pool = Pool(self.parallelism)
        # CANCEL ACTIONS
        pool.map(self.action, cancel_action)

        # CREATE DIRECTORIES
        pool.map(self.action, mkdir_action)

        # COPY FILES
        pool.map(self.action, copy_action)

        # PUT FILES
        pool.map(self.action, put_action)

        # GET FILES
        pool.map(self.action, get_action)

        # LIST FILES
        pool.map(self.action, list_action)

        # SEARCH FILES
        pool.map(self.action, search_action)

        # DELETE FILES/DIRECTORIES
        pool.map(self.action, delete_action)

        # Worker processes within a Pool typically live for the complete \
        # duration of the Pool’s work queue.

        # Prevents any more tasks from being submitted to the pool.Once all
        # the tasks have been completed the worker processes will exit.
        pool.close()
        # Wait for the worker processes to exit.One must call close() or \
        # terminate() before using join().
        pool.join()

    def monitor(self, status, rate=5, output="table"):
        cm = CmDatabase()
        try:
            while True:
                entries = cm.find(cloud=self.name, kind='storage')
                if status != "all":
                    entries = list(filter(lambda entry: entry['status'] ==
                                                        status, entries))
                os.system("clear")
                self.pretty_print(data=entries, data_type="monitor",
                                  output=output)
                print("--------------Press Ctrl+C to quit.--------------")
                time.sleep(rate)
        except KeyboardInterrupt:
            pass
