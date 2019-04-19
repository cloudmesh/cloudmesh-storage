batch
=====

::

  Usage:
    batch job create JOB_NAME --script=SLURM_SCRIPT_PATH --input-type=INPUT_TYPE --cluster=CLUSTER_NAME --job-script-path=SCRIPT_PATH --remote-path=REMOTE_PATH --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
    batch job run JOB_NAME
    batch fetch JOB_NAME
    batch test CLUSTER_NAME
    batch set cluster CLUSTER_NAME PARAMETER VALUE
    batch set job JOB_NAME PARAMETER VALUE
    batch list clusters [DEPTH [default:1]]
    batch list jobs [DEPTH [default:1]]
    batch remove cluster CLUSTER_NAME
    batch remove job JOB_NAME
    batch clean JOB_NAME

  This command does some useful things.

  Arguments:
      FILE   a file name

  Options:
      -f      specify the file

