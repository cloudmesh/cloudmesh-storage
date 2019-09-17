from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE

class Shell3Command(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_shell3(self, args, arguments):
        """
            ::

              Usage:
                    shell3 --text=TEXT
                    shell3 --number=NUMBER
                    shell3 list

              This command informs the option entered along with values.

              Arguments:
                  TEXT      a text string
                  NUMBER    a whole number

            """
        arguments.TEXTSTR = arguments['--text'] or None

        arguments.NUMBER = arguments['--number'] or None

        VERBOSE(arguments)

        if arguments.TEXTSTR:
            print("You have entered Text Option, Value: " + arguments.TEXTSTR)

        elif arguments.NUMBER:
            print("You have entered Number Option, Value:" + str(arguments.NUMBER))

        elif arguments.list:
            print("You have entered list Option")

        return ""

