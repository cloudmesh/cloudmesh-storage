vcluster
========

::

  Usage:

    vcluster create cluster CLUSTER_NAME --clusters=CLUSTERS_LIST [--computers=COMPUTERS_LIST] [--debug]
    vcluster destroy cluster CLUSTER_NAME
    vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
    vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
    vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]]  [--download-later [default=True]]  [--debug]
    vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
    vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout+file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
    vcluster set-param runtime-config CONFIG_NAME PARAMETER VALUE
    vcluster destroy runtime-config CONFIG_NAME
    vcluster list clusters [DEPTH [default:1]]
    vcluster list runtime-configs [DEPTH [default:1]]
    vcluster run-script --script-path=SCRIPT_PATH --job-name=JOB_NAME --vcluster-name=CLUSTER_NAME --config-name=CONFIG_NAME --arguments=SET_OF_PARAMS --remote-path=REMOTE_PATH --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
    vcluster fetch JOB_NAME
    vcluster clean-remote JOB_NAME PROCESS_NUM
    vcluster test-connection CLUSTER_NAME PROCESS_NUM

  This command does some useful things.

  Arguments:
      FILE   a file name

  Options:
      -f      specify the file

