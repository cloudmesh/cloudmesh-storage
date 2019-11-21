from cloudmesh.common.parameter import Parameter
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.variables import Variables
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.debug import VERBOSE


# noinspection PyBroadException
class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

          Usage:
                storage [--storage=SERVICE] create dir DIRECTORY
                storage [--storage=SERVICE] get SOURCE DESTINATION [--recursive]
                storage [--storage=SERVICE] put SOURCE DESTINATION [--recursive]
                storage [--storage=SERVICE] list SOURCE [--recursive] [--output=OUTPUT]
                storage [--storage=SERVICE] delete SOURCE
                storage [--storage=SERVICE] search  DIRECTORY FILENAME [--recursive] [--output=OUTPUT]
                storage [--storage=SERVICE] sync SOURCE DESTINATION [--name=NAME] [--async]
                storage [--storage=SERVICE] sync status [--name=NAME]
                storage config list [--output=OUTPUT]

          This command does some useful things.

          Arguments:
              SOURCE        SOURCE can be a directory or file
              DESTINATION   DESTINATION can be a directory or file
              DIRECTORY     DIRECTORY refers to a folder on the cloud service


          Options:
              --storage=SERVICE  specify the cloud service name like aws or
                                 azure or box or google

          Description:
                commands used to upload, download, list files on different
                cloud storage services.

                storage put [options..]
                    Uploads the file specified in the filename to specified
                    cloud from the SOURCEDIR.

                storage get [options..]
                    Downloads the file specified in the filename from the
                    specified cloud to the DESTDIR.

                storage delete [options..]
                    Deletes the file specified in the filename from the
                    specified cloud.

                storage list [options..]
                    lists all the files from the container name specified on
                    the specified cloud.

                storage create dir [options..]
                    creates a folder with the directory name specified on the
                    specified cloud.

                storage search [options..]
                    searches for the source in all the folders on the specified
                    cloud.

                sync SOURCE DESTINATION
                    puts the content of source to the destination.
                    If --recursive is specified this is done recursively from
                       the source
                    If --async is specified, this is done asynchronously
                    If a name is specified, the process can also be monitored
                       with the status command by name.
                    If the name is not specified all date is monitored.

                sync status
                    The status for the asynchronous sync can be seen with this
                    command

                config list
                    Lists the configures storage services in the yaml file

          Example:
            set storage=azureblob
            storage put SOURCE DESTINATION --recursive

            is the same as
            storage --storage=azureblob put SOURCE DESTINATION --recursive

        """
        # arguments.CONTAINER = arguments["--container"]

        map_parameters(arguments,
                       "recursive",
                       "storage")
        VERBOSE(arguments)


        if arguments.storage is None:
            try:
                v = Variables()
                arguments.storage = v['storage']
            except Exception as e:
                arguments.storage = None
                raise ValueError("Storage provider is not defined")

        arguments.storage = Parameter.expand(arguments.storage)

        #
        # BUG: some commands could be run on more than the first provider,
        # such as list
        # thus the if condition needs to be reorganized

        if arguments["get"]:
            provider = Provider(arguments.storage[0])

            result = provider.get(arguments.SOURCE,
                                  arguments.DESTINATION,
                                  arguments.recursive)

        elif arguments.put:
            provider = Provider(arguments.storage[0])

            result = provider.put(arguments.SOURCE,
                                  arguments.DESTINATION,
                                  arguments.recursive)

        elif arguments.create and arguments.dir:
            provider = Provider(arguments.storage[0])

            result = provider.create_dir(arguments.DIRECTORY)

        elif arguments.list:

            #
            # BUG: this command is much more complicated
            #

            for storage in arguments.storage:
                provider = Provider(storage)

                result = provider.list(arguments.SOURCE,
                                       arguments.recursive)

        elif arguments.delete:

            #
            # BUG:: this command could be much more complicated
            #
            for storage in arguments.storage:
                provider = Provider(storage)

                provider.delete(arguments.SOURCE)

        elif arguments.search:
            #
            # BUG: this command is much more complicated
            #

            for storage in arguments.storage:
                provider = Provider(storage)

                provider.search(arguments.DIRECTORY,
                                arguments.FILENAME,
                                arguments.recursive)

        elif arguments.rsync:
            # TODO: implement
            raise NotImplementedError
