export MY_HOME=$PWD
export MY_CMD=nc

export MY_LOGS=/tmp/cli_log.out
rm -f $MY_LOGS

base_conf=../../src/conf
new_conf=$MY_HOME/conf
rm -rf $new_conf
mkdir -p $new_conf/cache
cp $base_conf/db_local.db $new_conf/.
export MY_LITE=$new_conf/db_local.db

sqlite3 $MY_LITE < $base_conf/versions24.sql

$NC/devel/startHTTP.sh

python3 -u cli.py "$@"
