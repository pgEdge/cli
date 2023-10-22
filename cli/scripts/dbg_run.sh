export MY_HOME=$PWD
export MY_CMD=nc

action="$1"

export MY_LOGS=/tmp/cli_log.out
rm -f $MY_LOGS

base_conf=../../src/conf
new_conf=$MY_HOME/conf
export MY_LITE=$new_conf/db_local.db
if [ ! -d "$new_conf" ] || [ "$action" == "reset" ]; then
  if [ -d "$new_conf" ]; then
    python3 -u cli.py stop
  fi

  ./dbg_cleanup.sh

  rm -rf "$new_conf"
  mkdir -p "$new_conf/cache"
  cp $base_conf/db_local.db "$new_conf/."
  "$NC"/devel/startHTTP.sh
  
  exit 0
fi

sqlite3 "$MY_LITE" < $base_conf/versions24.sql

python3 -u cli.py "$@"
