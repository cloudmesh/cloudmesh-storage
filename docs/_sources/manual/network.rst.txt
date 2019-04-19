network
=======

::

    Usage:
        network get fixed [ip] [--cloud=CLOUD] FIXED_IP
        network get floating [ip] [--cloud=CLOUD] FLOATING_IP_ID
        network reserve fixed [ip] [--cloud=CLOUD] FIXED_IP
        network unreserve fixed [ip] [--cloud=CLOUD] FIXED_IP
        network associate floating [ip] [--cloud=CLOUD] [--group=GROUP]
                                   [--instance=INS_ID_OR_NAME] [FLOATING_IP]
        network disassociate floating [ip] [--cloud=CLOUD] [--group=GROUP]
                                      [--instance=INS_ID_OR_NAME] [FLOATING_IP]
        network create floating [ip] [--cloud=CLOUD] [--pool=FLOATING_IP_POOL]
        network delete floating [ip] [--cloud=CLOUD] [--unused] [FLOATING_IP]
        network list floating pool [--cloud=CLOUD]
        network list floating [ip] [--cloud=CLOUD] [--unused] [--instance=INS_ID_OR_NAME] [IP_OR_ID]
        network create cluster --group=demo_group
        network -h | --help

    Options:
        -h                          help message
        --unused                    unused floating ips
        --cloud=CLOUD               Name of the IaaS cloud e.g. india_openstack_grizzly.
        --group=GROUP               Name of the group in Cloudmesh
        --pool=FLOATING_IP_POOL     Name of Floating IP Pool
        --instance=INS_ID_OR_NAME   ID or Name of the vm instance

    Arguments:
        IP_OR_ID        IP Address or ID of IP Address
        FIXED_IP        Fixed IP Address, e.g. 10.1.5.2
        FLOATING_IP     Floating IP Address, e.g. 192.1.66.8
        FLOATING_IP_ID  ID associated with Floating IP, e.g. 185c5195-e824-4e7b-8581-703abec4bc01

    Examples:
        network get fixed ip --cloud=india 10.1.2.5
        network get fixed --cloud=india 10.1.2.5
        network get floating ip --cloud=india 185c5195-e824-4e7b-8581-703abec4bc01
        network get floating --cloud=india 185c5195-e824-4e7b-8581-703abec4bc01
        network reserve fixed ip --cloud=india 10.1.2.5
        network reserve fixed --cloud=india 10.1.2.5
        network unreserve fixed ip --cloud=india 10.1.2.5
        network unreserve fixed --cloud=india 10.1.2.5
        network associate floating ip --cloud=india --instance=albert-001 192.1.66.8
        network associate floating --cloud=india --instance=albert-001
        network associate floating --cloud=india --group=albert_group
        network disassociate floating ip --cloud=india --instance=albert-001 192.1.66.8
        network disassociate floating --cloud=india --instance=albert-001 192.1.66.8
        network create floating ip --cloud=india --pool=albert-f01
        network create floating --cloud=india --pool=albert-f01
        network delete floating ip --cloud=india 192.1.66.8 192.1.66.9
        network delete floating --cloud=india 192.1.66.8 192.1.66.9
        network list floating ip --cloud=india
        network list floating --cloud=india
        network list floating --cloud=india --unused
        network list floating --cloud=india 192.1.66.8
        network list floating --cloud=india --instance=323c5195-7yy34-4e7b-8581-703abec4b
        network list floating pool --cloud=india
        network create cluster --group=demo_group

