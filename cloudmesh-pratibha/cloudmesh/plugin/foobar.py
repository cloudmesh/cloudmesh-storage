from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint


class FoobarCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_foobar(self, args, arguments):
        """
        ::

          Usage:
                foobar

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """

        print(arguments)

        print("FOOBAR")

        return ""
