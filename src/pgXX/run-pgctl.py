from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2020-2022 OSCG             ##########
####################################################################

import subprocess
import os
import sys

MY_HOME = os.getenv("MY_HOME", "")
sys.path.append(os.path.join(MY_HOME, 'hub', 'scripts'))
sys.path.append(os.path.join(MY_HOME, 'hub', 'scripts', 'lib'))

import util

util.set_lang_path()
 
pgver = "pgXX"

datadir = util.get_column('datadir', pgver)

logdir = util.get_column('logdir', pgver)

autostart = util.get_column('autostart', pgver)

pg_ctl = os.path.join(MY_HOME, pgver, "bin", "pg_ctl")
logfile = util.get_column('logdir', pgver) + os.sep + "postgres.log"

util.read_env_file(pgver)

cmd = pg_ctl + ' start -s -w -D "' + datadir + '" ' + '-l "' + logfile + '"'
util.system(cmd)
