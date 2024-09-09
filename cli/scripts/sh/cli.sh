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
export MY_LOGS=$MY_HOME/data/logs/cli_log.out
export MY_LITE=$MY_HOME/data/conf/db_local.db
export MY_CMD=pgedge


set_libpath () {
  vers="$1"
  for ver in ${vers}; do
    lp="$MY_HOME/pg$ver/lib"
    if [ -d "$lp" ]; then
      export LD_LIBRARY_PATH="$lp":$LD_LIBRARY_PATH
    fi
  done
}

set_pythonpath () {
  vers="$1"
  for ver in ${vers}; do
    lib="$LIB/$ver"
    if [ -d "$LIB/$ver" ]; then
      lib="$LIB/$ver"
      export MY_CTLIB_VER=$ver
      return
    fi
  done
}

## MAINLINE #######################

cd "$MY_HOME"

declare -a array
array[0]="$MY_HOME/hub/scripts"
LIB="$MY_HOME/hub/scripts/lib"
array[1]="$LIB"

py_path="el9-arm el9-amd el8-amd ubu22-arm ubu22-amd osx"
py_path="$py_path ubu24-arm ubu24-amd deb12-arm deb12-amd el10-amd el10-arm"
lib="None"
set_pythonpath "$py_path"

if [ ! "$lib" == "None" ]; then
  array[2]="$lib"
  if [ -d "$lib/bin" ]; then
    export PATH=$lib/bin:$PATH
  fi
fi

array[3]=$MY_HOME/hub/scripts/contrib

export PYTHONPATH=$(printf "%s:" ${array[@]})
for var in "$@"
do
  if [ "$var" == "-v" ]; then
    echo "PYTHONPATH=$PYTHONPATH"
  fi
done

## echo "DEBUG: PYTHONPATH=$PYTHONPATH"

set_libpath "14 15 16 17"
## echo "DEBUG: LD_LIBRARY_PATH=$LD_LIBRARY_PATH"

python3 --version > /dev/null 2>&1
rc=$?
if [ $rc != 0 ];then
  echo "ERROR: missing python3"
  exit 1
fi
v=`python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2`

if [ -f /usr/bin/python3.11 ]; then
  export PYTHON=python3.11
elif [ $v == "3.9" ] || [ $v == "3.10" ] || [ $v == "3.11" ] || [ $v == "3.12" ]; then
  export PYTHON=python3
elif [ -f /usr/bin/python3.9 ]; then
  export PYTHON=/usr/bin/python3.9
else
  # try it anyway
  export PYTHON=python3
fi

$PYTHON -W ignore -u "$MY_HOME/hub/scripts/cli.py" "$@"
