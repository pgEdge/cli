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

if [ `uname` == "Linux" ]; then
  if [ -f "/etc/redhat-release" ]; then
    if [ `arch` == "aarch64" ]; then
      array[2]="$LIB/el9-arm"
    else
      PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
      if [ "$PLATFORM" == "el9" ]; then
        array[2]="$LIB/el9-amd"
      else
        array[2]="$LIB/el8-amd"
      fi
    fi
  else
    if [ -f "/etc/os-release" ]; then
      grep "22.04" /etc/os-release > /dev/null 2>&1
      rc=$?
      if [ $rc == "0" ]; then
        if [ `arch` == "aarch64" ]; then
          array[2]="$LIB/ubu22-arm"
        else
          array[2]="$LIB/ubu22-amd"
        fi
      fi
    fi
  fi
elif [ `uname` == "Darwin" ]; then
  ## universal binaries for x86_64 & arm64
  array[2]="$LIB/osx"
fi

if [ -d $LIB/el9-amd/bin ]; then
  export PATH=$LIB/el9-amd/bin:$PATH
fi

export PYTHONPATH=$(printf "%s:" ${array[@]})
##echo PYTHONPATH=$PYTHONPATH
for var in "$@"
do
  if [ "$var" == "-v" ]; then
    echo "PYTHONPATH=$PYTHONPATH"
  fi
done

if [ -f /usr/bin/python3.9 ]; then
  export PYTHON=/usr/bin/python3.9
else
  export PYTHON=/usr/bin/python3
fi
pyver=`$PYTHON --version > /dev/null 2>&1`
rc=$?
if [ $rc != 0 ];then
  echo "ERROR: missing python3"
  exit 1
fi

$PYTHON -u "$MY_HOME/hub/scripts/cli.py" "$@"
