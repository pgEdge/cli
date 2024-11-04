
####################################################################
######          Copyright (c)  2022-2024 PGEDGE           ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column("autostart", pgver)
if autostart == "on":
    startup.remove_proc("pg" + pgver[2:4])

isRM_DATA = os.getenv("isRM_DATA", "False")
if isRM_DATA == "True":
    util.message("Removing 'data' directories at your request")
    util.echo_cmd(f"sudo rm -r data/{pgver}")
    util.echo_cmd(f"sudo rm -r data/logs/{pgver}")
