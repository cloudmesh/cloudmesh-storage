image
=====

::

    Usage:
        image refresh [--cloud=CLOUD]
        image list [ID] [--cloud=CLOUD] [--output=OUTPUT] [--refresh]
        This lists out the images present for a cloud
    Options:
       --output=OUTPUT  the output format [default: table]
       --cloud=CLOUD    the cloud name
       --refresh        live data taken from the cloud
    Examples:
        cm image refresh
        cm image list
        cm image list --format=csv
        cm image list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh

