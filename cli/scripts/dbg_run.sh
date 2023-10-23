#!/bin/bash

mydir="$(dirname "${0}")"
cd $mydir

source dbg_env.sh

action="$1"
base_conf=../../src/conf

if [ ! -d "conf" ] || [ "$action" == "reset" ]; then
  ./dbg_cleanup.sh

  mkdir -p "conf/cache"
  cp $base_conf/db_local.db "conf/."
  $NC/devel/startHTTP.sh
  
  exit   
fi

sqlite3 "$MY_LITE" < $base_conf/versions24.sql

python3 -u cli.py "$@"
