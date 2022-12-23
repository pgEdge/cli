from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2020-2022 OSCG             ##########
####################################################################


import os, sys, json

MY_HOME = os.getenv("MY_HOME", "")
scripts_path = os.path.join(MY_HOME, 'hub', 'scripts')
scripts_lib_path = os.path.join(MY_HOME, 'hub', 'scripts', 'lib')

if scripts_path not in sys.path:
  sys.path.append(scripts_path)
if scripts_lib_path not in sys.path:
  sys.path.append(scripts_lib_path)

import util, startup

pgver = "pgXX"

homedir = os.path.join(MY_HOME, pgver)

datadir = util.get_column('datadir', pgver)

pidfile = os.path.join(datadir, "postmaster.pid")

if os.path.isfile(pidfile):
  with open(pidfile, 'r') as f:
    pid = f.readline().rstrip(os.linesep)
else:
  util.message(pgver + " stopped")
  sys.exit(0)

util.message(pgver + " stopping")

pg_ctl = os.path.join(homedir, "bin", "pg_ctl")

stop_cmd = pg_ctl + ' stop -s -w -m immediate -D "' + datadir + '"'

autostart = util.get_column('autostart', pgver)
if autostart == "on":
  rc = startup.stop_linux("postgresql" + pgver[2:4])
else:
  rc = util.system(stop_cmd)

if (rc > 0):
  util.message("problem stopping " + pgver)

sys.exit(rc)
