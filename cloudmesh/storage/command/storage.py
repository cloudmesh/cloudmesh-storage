from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.storage.Provider import Provider


# noinspection PyBroadException
class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

           Usage:
             storage create dir DIRECTORY [--storage=SERVICE] [--parallel=N]
             storage get SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
             storage put SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
             storage list [SOURCE] [--recursive]  [--storage=SERVICE] [--parallel=N] [--output=OUTPUT]
             storage slist --source=SOURCE:SOURCE_FILE_DIR [WILLBEMERGED]
             storage delete SOURCE [--storage=SERVICE] [--parallel=N]
             storage sdelete --source=SOURCE:SOURCE_FILE_DIR [WILLBEMERGED]
             storage search  DIRECTORY FILENAME [--recursive] [--storage=SERVICE] [--parallel=N] [--output=OUTPUT]
             storage sync SOURCE DESTINATION [--name=NAME] [--async] [--storage=SERVICE]
             storage sync status [--name=NAME] [--storage=SERVICE]
             storage config list [--output=OUTPUT]
             storage [--parallel=N] copy SOURCE DESTINATION [--recursive]
             storage copy --source=SOURCE:SOURCE_FILE_DIR --target=TARGET:TARGET_FILE_DIR

           This command does some useful things.

           Arguments:
             SOURCE        SOURCE can be a directory or file
             DESTINATION   DESTINATION can be a directory or file
             DIRECTORY     DIRECTORY refers to a folder on the cloud service
             SOURCE:SOURCE_FILE_DIR   source provider name: file or directory name
             TARGET:SOURCE_FILE_DIR   destination provider name

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

             storage copy SOURCE DESTINATION
               Copies files from source storage to destination storage.
               The syntax of SOURCE and DESTINATION is:
               SOURCE - awss3:source.txt
               DESTINATION - azure:target.txt

           Description of the copy command:

                Command enables to Copy files between different cloud service
                providers, list and delete them. This command accepts `aws` ,
                `google` and `local` as the SOURCE and TARGET provider.

                cms storage copy --source=SERVICE:SOURCE --target=DEST:TARGET

                    Command copies files or directories from Source provider to
                    Target Provider.

                cms storage slist --source=SERVICE:SOURCE
                    Command lists all the files present in SOURCE provider's in
                    the given SOURCE_FILE_DIR location This command accepts
                    `aws` or `google` as the SOURCE provider

                cms storage sdelete --source=SERVICE:SOURCE
                    Command deletes the file or directory from the SOURCE
                    provider's SOURCE_FILE_DIR location

            Examples:
                cms storage_service copy --source=local:test1.txt --target=aws:uploadtest1.txt
                cms storage_service list --source=google:test
                cms storage_service delete --source=aws:uploadtest1.txt


           Example:
              set storage=azureblob
              storage put SOURCE DESTINATION --recursive

              is the same as
              storage --storage=azureblob put SOURCE DESTINATION --recursive

              storage copy azure:source.txt oracle:target.txt

        """
        # arguments.CONTAINER = arguments["--container"]

        VERBOSE(arguments)
        map_parameters(arguments,
                       "recursive",
                       "storage",
                       "source",
                       "target")

        source = arguments.source
        target = arguments.target
        VERBOSE(arguments)

        if arguments.storage is None:
            if arguments.copy is None:
                try:
                    v = Variables()
                    arguments.storage = v['storage']
                except Exception as e:
                    arguments.storage = None
                    raise ValueError("Storage provider is not defined")
            else:
                if arguments.DESTINATION.split(":")[0] == "local":
                    arguments.storage = arguments.SOURCE.split(":")[0]
                else:
                    arguments.storage = arguments.DESTINATION.split(":")[0]

        arguments.storage = Parameter.expand(arguments.storage)

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

            source = arguments.SOURCE or '.'

            for storage in arguments.storage:
                provider = Provider(storage)

                result = provider.list(source,
                                       arguments.recursive)

        elif arguments.slist:
            scloud, sbucket = source.split(":", 1) or None
            if (scloud == "aws" or scloud == "google"):
                provider = Provider(service=scloud)
                provider.list(sbucket)
            else:
                print("Source Provider Not Implemented")


        elif arguments.delete:

            for storage in arguments.storage:
                provider = Provider(storage)

                provider.delete(arguments.SOURCE)

        elif arguments.sdelete:

            scloud, sbucket = source.split(":", 1) or None
            if (scloud == "aws" or scloud == "google"):
                provider = Provider(service=scloud)
                provider.delete(sbucket)
            else:
                print("Source Provider Not Implemented")


        elif arguments.search:

            for storage in arguments.storage:
                provider = Provider(storage)

                provider.search(arguments.DIRECTORY,
                                arguments.FILENAME,
                                arguments.recursive)

        elif arguments.rsync:
            # TODO: implement
            raise NotImplementedError

        elif arguments.copy:
            VERBOSE(f"COPY: Executing Copy command from {arguments.SOURCE} to "
                    f"{arguments.DESTINATION} providers")
            print(f"DEBUG storage.py: INITIALIZE with {arguments.storage[0]} "
                  "provider.")

            provider = Provider(arguments.storage[0])

            result = provider.copy(arguments.SOURCE,
                                   arguments.DESTINATION,
                                   arguments.recursive)


        elif arguments.copy:
            scloud, sbucket = source.split(":", 1) or None
            tcloud, tbucket = target.split(":", 1) or None
            # print(scloud + " " + tcloud + " " + sbucket + " " + tbucket)

            if scloud == "aws" or scloud == "google":
                provider = Provider(service=scloud)
                provider.copy(scloud, tcloud, sbucket, tbucket)
            elif (scloud == "local" and tcloud == "aws") or (
                scloud == "local" and tcloud == "google"):
                provider = Provider(service=tcloud)
                provider.copy(scloud, tcloud, sbucket, tbucket)
            else:
                print("Not Implemented")

        return ""
