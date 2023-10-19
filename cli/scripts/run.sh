export MY_HOME=$PWD
export MY_LOGS=/tmp/cli_log.out
export MY_LITE=$PWD/../../src/conf/db_local.db
export MY_CMD=nc

python3 -u cli.py "$@"
