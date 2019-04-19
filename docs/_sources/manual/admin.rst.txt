admin
=====

::

  Usage:
    admin mongo install [--brew] [--download=PATH]
    admin mongo create
    admin mongo status
    admin mongo stats
    admin mongo version
    admin mongo start
    admin mongo stop
    admin mongo backup FILENAME
    admin mongo load FILENAME
    admin mongo security
    admin mongo password PASSWORD
    admin mongo list
    admin rest status
    admin rest start
    admin rest stop
    admin status
    admin system info

  The admin command performs some administrative functions, such as installing packages, software and services.
  It also is used to start services and configure them.

  Arguments:
    FILENAME  the filename for backups

  Options:
    -f      specify the file

  Description:

    Mongo DB

      MongoDB is managed through a number of commands.

      The configuration is read from ~/.cloudmesh/cloudmesh4.yaml

      First, you need to create a MongoDB database with

        cms admin mongo create

      Second, you need to start it with

         cms admin mongo start

      Now you can interact with it to find out the status, the stats,
      and the database listing with the commands

         cms admin mongo status
         cms admin mongo stats
         cms admin mongo list

      To stop it from running use the command

         cms admin mongo stop

      System information about your machine can be returned by

         cms admin system info

      This can be very useful in case you are filing an issue or bug.

