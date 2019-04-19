var
===

::

    Usage:
        var list
        var clear
        var delete NAME
        var NAME=VALUE
        var NAME

    Arguments:
        NAME      the name of the variable
        VALUE     the value of the variable
        FILENAME  the filename of the variable
    Description:
        Manage persistent variables

        var NAME=VALUE
           sets the variable with the name to the value
           if the value is one of data, time, now it will be
           replaced with the value at this time, the format will be
            date    2017-04-14
            time    11:30:33
            now     2017-04-14 11:30:41
        It will wbe replaced accordingly

        The value can also refer to another variable name.
        In this case the current value will be copied in the named
        variable. As we use the $ sign it is important to distinguish
        shell variables from cms variables while using proper quoting.

        Examples include:

           cms var a=\$b
           cms var 'a=$b'
           cms var a=val.b

        The previous command copy the value from b to a. The val command
        was added to avoid quoting.

