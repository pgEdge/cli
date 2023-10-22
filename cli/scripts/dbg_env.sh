#!/bin/bash

mydir="$(dirname "${0}")"
cd $mydir

export MY_HOME=$mydir
export MY_CMD=dbg_run.sh
export MY_LOGS=/tmp/cli_log.out
export MY_LITE=$mydir/conf/db_local.db

