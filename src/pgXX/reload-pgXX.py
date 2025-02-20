
####################################################################
######          Copyright (c)  2022-2025 PGEDGE                #######
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

util.message(pgver + " reloading")

autostart = util.get_column("autostart", pgver)
if autostart == "on":
    rc = startup.reload_linux("pg" + pgver[2:4])
    sys.exit(rc)

MY_HOME = os.getenv("MY_HOME", "")
homedir = os.path.join(MY_HOME, pgver)
datadir = util.get_column("datadir", pgver)

pg_ctl = os.path.join(homedir, "bin", "pg_ctl")
parms = ' reload -D "' + datadir + '"'
rc = util.echo_cmd(pg_ctl + parms)

sys.exit(rc)
