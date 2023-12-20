#!/bin/bash

start_dir="$PWD"

# resolve links - $0 may be a softlink
this="${BASH_SOURCE-$0}"
common_bin=$(cd -P -- "$(dirname -- "$this")" && pwd -P)
script="$(basename -- "$this")"
this="$common_bin/$script"
# convert relative path to absolute path
config_bin=`dirname "$this"`
script=`basename "$this"`
my_home=`cd "$config_bin"; pwd`

export MY_HOME="$my_home"
export MY_LOGS=$MY_HOME/logs/cli_log.out
export MY_LITE=$MY_HOME/conf/db_local.db
export MY_CMD=nc

cd "$MY_HOME"

hub_new="$MY_HOME/hub_new"
if [ -d "$hub_new" ];then
  `mv $MY_HOME/hub_new $MY_HOME/hub_upgrade`
  log_time=`date +"%Y-%m-%d %H:%M:%S"`
  echo "$log_time [INFO] : completing hub upgrade" >> $MY_LOGS
  `mv $MY_HOME/hub $MY_HOME/hub_old`
  `cp -rf $MY_HOME/hub_upgrade/* $MY_HOME/`
  `rm -rf $MY_HOME/hub_upgrade`
  `rm -rf $MY_HOME/hub_old`
  log_time=`date +"%Y-%m-%d %H:%M:%S"`
  echo "$log_time [INFO] : hub upgrade completed" >> $MY_LOGS
fi

declare -a array
array[0]="$MY_HOME/hub/scripts"
LIB="$MY_HOME/hub/scripts/lib"
array[1]="$LIB"

lib="None"
if [ -d "$LIB/el9-arm" ]; then
  lib="$LIB/el9-arm"
elif [ -d "$LIB/el9-amd" ]; then
  lib="$LIB/el9-amd"
elif [ -d "$LIB/el8-amd" ]; then
  lib="$LIB/el8-amd"
elif [ -d "$LIB/osx" ]; then
  lib="$LIB/osx"
elif [ -d "$LIB/ubu22-arm" ]; then
  lib="$LIB/ubu22-arm"
elif [ -d "$LIB/ubu22-amd" ]; then
  lib="$LIB/ubu22-amd"
fi

if [ ! "$lib" == "None" ]; then
  array[2]="$lib"
  if [ -d "$lib/bin" ]; then
    export PATH=$lib/bin:$PATH
  fi
fi

export PYTHONPATH=$(printf "%s:" ${array[@]})
##echo PYTHONPATH=$PYTHONPATH
for var in "$@"
do
  if [ "$var" == "-v" ]; then
    echo "PYTHONPATH=$PYTHONPATH"
  fi
done

v=`python3 --version | cut -d' ' -f2 | cut -d'.' -f1 -f2`
rc=$?
if [ $rc != 0 ];then
  echo "ERROR: missing python3"
  exit 1
fi

if [ $v == "3.9" ] || [ $v == "3.10" ] || [ $v == "3.11" ] || [ $v == "3.12" ]; then
  export PYTHON=python3
elif [ -f /usr/bin/python3.9 ]; then
  export PYTHON=/usr/bin/python3.9
else
  export PYTHON=python3
fi

$PYTHON -u "$MY_HOME/hub/scripts/cli.py" "$@"
