#!/bin/bash

mydir="$(dirname "${0}")"
cd $mydir

source dbg_env.sh

del="rm -rf"

#if [ -d "conf" ]; then
#  python3 -u cli.py stop
#fi

$del $MY_LOGS

$del pg1*
$del conf
$del data

$del pgcat
$del staz
$del etcd
$del prompgexp
$del postgrest
$del backrest

$del __pycache__
$del lib/__pycache__
