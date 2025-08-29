
####################################################################
######          Copyright (c)  2022-2025 PGEDGE             ##########
####################################################################

import os, sys, subprocess, json
import util, startup, time

pgver = "pgXX"

MY_HOME = os.getenv("MY_HOME", "")
homedir = os.path.join(MY_HOME, pgver)
logdir = os.path.join(homedir, pgver)
datadir = util.get_column("datadir", pgver)

first_time = "no"
if not os.path.isdir(datadir):
    rc = os.system(sys.executable + " -u " + homedir + os.sep + "init-" + pgver + ".py")
    if rc == 0:
        rc = os.system(
            sys.executable + " -u " + homedir + os.sep + "config-" + pgver + ".py"
        )
    else:
        sys.exit(rc)
    datadir = util.get_column("datadir", pgver)
    first_time = "yes"

autostart = util.get_column("autostart", pgver)
logfile = util.get_column("logdir", pgver) + os.sep + "postgres.log"
port = util.get_column("port", pgver)

msg = pgver + " starting on port " + str(port)
util.message(msg)

cmd = sys.executable + " " + homedir + os.sep + "run-pgctl.py"

if autostart == "on":
    startup.start_linux("pg" + pgver[2:4])
else:
    subprocess.run(cmd, preexec_fn=os.setpgrp(), close_fds=True, shell=True)

isYes = os.getenv("isYes", "False")
pgName = os.getenv("pgName", "")
if (pgName > "") and (isYes == "True"):
    util.message("\n # waiting for DB to start...")
    time.sleep(4)
    cmd = os.path.join(pgver, "bin", "createdb")
    cmd = cmd + " -w -e -p " + str(port) + " " + str(pgName)
    util.message("\n # " + cmd)

    cmd = os.path.join(MY_HOME, cmd)
    os.system(cmd)
