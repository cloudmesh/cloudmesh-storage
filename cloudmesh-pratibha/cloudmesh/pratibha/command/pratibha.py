from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.pratibha.api.manager import Manager
from cloudmesh.common.util import path_expand
from cloudmesh.common.debug import VERBOSE

class PratibhaCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pratibha(self, args, arguments):
        """
        ::

          Usage:
                pratibha --text=TEXTSTR
                pratibha list

          This command does some useful things.

          Arguments:
              TEXTSTR   a file name

          Options:
              -f      specify the file

        """
        arguments.TEXTSTR = arguments['--text'] or None

        VERBOSE(arguments)

        m = Manager()

        if arguments.TEXTSTR:
            print("option --text")
            m.list(path_expand(arguments.TEXTSTR))

        elif arguments.list:
            print("option list")
            m.list("Just calling list without parameter")

        return ""
