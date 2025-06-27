
####################################################################
######          Copyright (c)  2022-2025 PGEDGE           ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column("autostart", pgver)
if autostart == "on":
    startup.remove_linux("pg" + pgver[2:4], pgver)

isRM_DATA = os.getenv("isRM_DATA", "False")
if isRM_DATA == "True":
    util.message("Removing 'data' directories at your request")
    data_dir = util.get_column("datadir", pgver)
    util.echo_cmd(f"sudo rm -r {data_dir}")
    util.echo_cmd(f"sudo rm -r data/logs/{pgver}")
