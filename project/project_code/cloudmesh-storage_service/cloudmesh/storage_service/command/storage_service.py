from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.storage_service.providers.Provider import Provider


class Storage_serviceCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage_service(self, args, arguments):
        """
        ::

          Usage:
                storage_service copy --source=SOURCE:SOURCE_FILE_DIR --target=TARGET:TARGET_FILE_DIR
                storage_service list --source=SOURCE:SOURCE_FILE_DIR
                storage_service delete --source=SOURCE:SOURCE_FILE_DIR

          This command does some useful things.

          Arguments:
              SOURCE:SOURCE_FILE_DIR   source provider name : file or directory name
              TARGET:SOURCE_FILE_DIR   destination provider name


          Options:
              --source=SOURCE:SOURCE_FILE_DIR      specify the cloud:location
              --target=TARGET:LOCATION      specify the target:location

           Description:
                Command enables to Copy files between different cloud service providers, list and delete them.
                This command accepts "aws" , "google" and "local" as the SOURCE and TARGET provider

                cms storage_service copy --source=SOURCE:SOURCE_FILE_DIR --target=TARGET:TARGET_FILE_DIR
                    Command copies files or directories from Source provider to Target Provider.

                cms storage_service list --source=SOURCE:SOURCE_FILE_DIR
                    Command lists all the files present in SOURCE provider's in the given SOURCE_FILE_DIR location
                    This command accepts "aws" or "google" as the SOURCE provider

                cms storage_service delete --source=SOURCE:SOURCE_FILE_DIR
                    Command deletes the file or directory from the SOURCE provider's SOURCE_FILE_DIR location

            Examples:
                cms storage_service copy --source=local:test1.txt --target=aws:uploadtest1.txt
                cms storage_service list --source=google:test
                cms storage_service delete --source=aws:uploadtest1.txt

        """

        source = arguments['--source'] or None
        target = arguments['--target'] or None

        VERBOSE(arguments)

        if arguments.list:
            scloud, sbucket = source.split(":", 1) or None
            if(scloud == "aws" or scloud == "google"):
                provider = Provider(service=scloud)
                provider.list(sbucket)
            else:
                print("Source Provider Not Implemented")
        elif arguments.copy:
            print("Inside Arguments.copy")
            scloud, sbucket = source.split(":", 1) or None
            tcloud, tbucket = target.split(":", 1) or None
            #print(scloud + " " + tcloud + " " + sbucket + " " + tbucket)

            if scloud == "aws" or scloud == "google":
                provider = Provider(service=scloud)
                provider.copy(scloud,tcloud,sbucket,tbucket)
            elif (scloud == "local" and tcloud == "aws") or (scloud == "local" and tcloud == "google"):
                provider = Provider(service=tcloud)
                provider.copy(scloud, tcloud, sbucket, tbucket)
            else:
                print("Not Implemented")

        return ""
