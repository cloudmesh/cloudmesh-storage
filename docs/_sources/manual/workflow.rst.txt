workflow
========

::

    Usage:
        workflow refresh [--cloud=CLOUD] [-v]
        workflow list [ID] [NAME] [--cloud=CLOUD] [--output=OUTPUT] [--refresh] [-v]
        workflow add NAME LOCATION
        workflow delete ID
        workflow status [NAMES]
        workflow show ID
        workflow save NAME WORKFLOWSTR
        workflow run NAME
        workflow service start
        workflow service stop
        This lists out the workflows present for a cloud

    Options:
       --output=OUTPUT  the output format [default: table]
       --cloud=CLOUD    the cloud name
       --refresh        refreshes the data before displaying it
                        from the cloud

    Examples:
        cm workflow refresh
        cm workflow list
        cm workflow list --format=csv
        cm workflow show 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh
        cm workflow run workflow1

