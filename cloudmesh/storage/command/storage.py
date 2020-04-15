from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import yn_choice
from cloudmesh.common.console import Console

# noinspection PyBroadException
class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

           Usage:
             storage monitor [--storage=SERVICES] [--status=all | --status=STATUS] [--output=output] [--clear]
             storage create dir DIRECTORY [--storage=SERVICE] [--parallel=N]
             storage get SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
             storage put SOURCE DESTINATION [--recursive] [--storage=SERVICE] [--parallel=N]
             storage list [SOURCE] [--recursive] [--parallel=N] [--output=OUTPUT] [--dryrun]
             storage delete SOURCE [--parallel=N] [--dryrun]
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
                       "dryrun",
                       "recursive",
                       "storage",
                       "source",
                       "target",
                       "parallel",
                       "status")

        source = arguments.source
        target = arguments.target
        variables = Variables()

        parallelism = arguments.parallel or 4

        arguments.storage = Parameter.expand(arguments.storage or variables[
            'storage'])
        if arguments["monitor"]:
            provider = Provider(arguments.storage[0], parallelism=parallelism)
            status = arguments.status or "all"
            result = provider.monitor(status=status)
        elif arguments["get"]:
            provider = Provider(arguments.storage[0], parallelism=parallelism)

            result = provider.get(arguments.SOURCE,
                                  arguments.DESTINATION,
                                  arguments.recursive)

        elif arguments.put:
            provider = Provider(arguments.storage[0], parallelism=parallelism)

            result = provider.put(arguments.SOURCE,
                                  arguments.DESTINATION,
                                  arguments.recursive)

        elif arguments.create and arguments.dir:
            provider = Provider(arguments.storage[0], parallelism=parallelism)

            result = provider.create_dir(arguments.DIRECTORY)

        elif arguments.list:

            """
            storage list SOURCE [--parallel=N]
            """
            sources = arguments.SOURCE or variables["storage"] or 'local:.'
            sources = Parameter.expand(sources)

            deletes = []
            for source in sources:
                storage, entry = Parameter.separate(source)

                storage = storage or "local"
                deletes.append((storage, entry))

            _sources = ', '.join(sources)

            for delete in deletes:
                service, entry = delete
                if arguments.dryrun:
                    print(f"Dryrun: list {service}:{entry}")
                else:
                    provider = Provider(service=service, parallelism=parallelism)
                    provider.list(name=entry)

            return ""

        elif arguments.delete:

            """
            storage delete SOURCE [--parallel=N]
            """
            sources = arguments.SOURCE or variables["storage"] or 'local:.'
            sources = Parameter.expand(sources)

            deletes = []
            for source in sources:
                storage, entry = Parameter.separate(source)

                storage = storage or "local"
                deletes.append((storage, entry))

            _sources = ', '.join(sources)

            answer = yn_choice(f"Would you like to delete {_sources}?", default="no")

            if answer:

                for delete in deletes:
                    service, entry = delete
                    if arguments.dryrun:
                        print(f"Dryrun: delete {service}:{entry}")
                    else:
                        provider = Provider(service=service, parallelism=parallelism)
                        provider.delete(name=entry)

            else:
                Console.error("Deletion canceled")

            return ""

        elif arguments.search:

            for storage in arguments.storage:
                provider = Provider(storage, parallelism=parallelism)

                provider.search(arguments.DIRECTORY,
                                arguments.FILENAME,
                                arguments.recursive)

        elif arguments.rsync:
            # TODO: implement
            raise NotImplementedError

        elif arguments.copy:
            scloud, sbucket = arguments['--source'].split(":", 1) or None
            tcloud, tbucket = arguments['--target'].split(":", 1) or None
            if scloud == "aws" or scloud == "google":
                provider = Provider(service=scloud, parallelism=parallelism)
                provider.copy(scloud, tcloud, sbucket, tbucket)
            elif (scloud == "local" and tcloud == "aws") or (
                scloud == "local" and tcloud == "google"):
                provider = Provider(service=tcloud, parallelism=parallelism)
                provider.copy(scloud, tcloud, sbucket, tbucket)
            elif (scloud == "local" and tcloud == "parallelawss3"):
                provider = Provider(service=tcloud, parallelism=parallelism)
                provider.copy(arguments['--source'], arguments['--target'],
                              arguments.recursive)
            else:
                print("Not Implemented")

        return ""
