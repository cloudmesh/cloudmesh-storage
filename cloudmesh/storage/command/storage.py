from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.storage.api.manager import Manager
from cloudmesh.shell.variables import Variables
from pprint import pprint
from cloudmesh.common.console import Console


# noinspection PyBroadException
class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

          Usage:
                storage [--storage=SERVICE] put FILENAME
                storage [--storage=SERVICE] get FILENAME
                storage [--storage=SERVICE] delete FILENAME
                storage [--storage=SERVICE] size FILENAME
                storage [--storage=SERVICE] info FILENAME
                storage [--storage=SERVICE] create FILENAME
                storage [--storage=SERVICE] sync SOURCEDIR DESTDIR


          This command does some useful things.

          Arguments:
              FILE   a file name
              

          Options:
              -f      specify the file

          Example:
            set storage=box
            storage  put FILENAME

            is the same as 

            starage  --storage=box put FILENAME


        """

        pprint(arguments)

        m = Manager()

        service = None

        filename = arguments.FILENAME[0]
        try:
            service = arguments["--storage"][0]
        except Exception as e:
            try:
                v = Variables()
                service = v['storage']
            except Exception as e:
                service = None

        if service is None:
            Console.error("storage service not defined")

        if arguments.get:
            m.get(service, filename)
