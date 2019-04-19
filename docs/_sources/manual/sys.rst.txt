sys
===

::

  Usage:
    sys upload
    sys commit MESSAGE
    sys command generate NAME
    sys version VERSION

  This command does some useful things.

  Arguments:
    MESSAGE   the message to commit 
    NAME      the command to generate
    VERSION   the version number

  Options:
    -f      specify the file

  Description:      
    cms sys command generate my
        This requires that you have checked out 

        ./cloudmesh.common
        ./cloudmesh.cmd5
        ./cloudmesh.sys

        When you execute in . this command
        will generate a sample directory tree for
        the command 'my'.

        You can than modify 

        cloudmesh.my/cloudmesh/my/command/my.py

        to define your own cmd5 add on commands.
        You install the command with 

        cd cloudmesh.my; pip install .

    The commands 'version', 'commit' and 'upload'
    are only to be used by Gregor.        

    cms version
        The version command adds a new version to the 
        VERSION file for cmd5, common, and sys.
        This helps to keep the versions aligned across 
        these modules.

    cms commit
        The commit  command adds a new version and commits

    cms upload
        The upload command uploads the new version to pypi

