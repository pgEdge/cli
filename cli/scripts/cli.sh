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
export MY_LOGS="$my_home/logs/cli_log.out"
export MY_CMD="io"

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
array[1]="$MY_HOME/hub/scripts/lib"

export PYTHONPATH=$(printf "%s:${PYTHONPATH}" ${array[@]})

pyver=`python3 --version > /dev/null 2>&1`
rc=$?   
if [ $rc == 0 ];then
  export PYTHON=python3
else
  pyver=`python --version > /dev/null 2>&1`
  rc=$?   
  if [ $rc == 0 ];then
    export PYTHON=python
  else
    export PYTHON=python2
  fi
fi

$PYTHON -u "$MY_HOME/hub/scripts/cli.py" "$@"
