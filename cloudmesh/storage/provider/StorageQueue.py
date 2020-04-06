import os
import textwrap
import uuid
from multiprocessing import Pool

import oyaml as yaml
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.debug import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


#


class StorageQueue(object):

    def __init__(self,
                 name=None,
                 config="~/.cloudmesh/cloudmesh.yaml",
                 parallelism=4):

        self.parallelism = parallelism
        self.name = name
        self.collection = f"storage-queue-{name}"
        self.number = 0
        self.directory_marker_file_name = 'marker.txt'
        self.storage_dict = {}

    #
    # keep tose with the rasied as we can inherit form this class an than
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
    _put = _notimplemented
    _get = _notimplemented
    _mkdir = _notimplemented
    _cancel = _notimplemented
    _delete = _notimplemented
    _copy = _notimplemented
    _list = _notimplemented

    def create_spec(self, spec, kwargs):
        result = textwrap.dedent(f"""
            cm:
               number: {self.number}
               name: "{sourcefile}:{destinationfile}"
               kind: storage
               id: {uuid_str}
               cloud: {self.name}
               collection: {self.collection}
               created: {date}
        """).format(**kwargs).strip() + \
                 "\n" + \
                 textwrap.dedent(spec).strip() + "\n"

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
        specification = self.create_spec(f"""
            action: copy
            source: 
              path: {sourcefile}
            destination: 
              path: {destinationfile}
            recursive: {recursive}
            status: waiting
        """, **locals())

        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    #
    # TODO: make indentations of the yaml uniform, see delete, do this for all
    #
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
        specification = self.create_spec(f"""
            action: delete
            source: 
              path: {path}
            recursive: {recursive}
            status: waiting
        """, **locals())
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

    #
    # BUG: THis should ideally be name and not id. THis has impact on all
    # providers as there may be a bug in the cancel methods including the ABC
    # class.
    #
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
        specification = self.create_spec(f"""
            action: cancel
            status: waiting
        """, **locals())
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1
        return entries

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
        specification = self.create_spec(f"""
                  action: mkdir
                  path: {path}
                  status: waiting
            """, **locals())
        entries = yaml.load(specification, Loader=yaml.SafeLoader)
        self.number = self.number + 1

        return entries

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
        specification = self.create_spec(f"""
              action: list
              path: {path}
              dir_only:{dir_only}
              recursive:{recursive}
              status: waiting
        """, **locals())
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

    def monitor(self, rate):
        cm = CmDatabase()
        while True:
            entries = cm.find(cloud=self.name,
                              kind='storage')
            os.system("clear")
            print(entries)  # use a pretty table
            # sleep (rate)
