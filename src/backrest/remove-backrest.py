#     Copyright (c)  2022-2024 PGEDGE  #

import os
import util, startup

pgV = ""
if os.path.isdir("pg14"):
    pgV = "pg14"
elif os.path.isdir("pg15"):
    pgV = "pg15"
elif os.path.isdir("pg16"):
    pgV = "pg16"
elif os.path.isdir("pg17"):
    pgV = "pg17"

autostart = util.get_column("autostart", "backrest")
if autostart == "on":
    startup.remove_linux("backrest")

os.system("sudo rm -f /usr/bin/pgbackrest")

isRM_DATA = os.getenv("isRM_DATA", "False")
if isRM_DATA == "True":
    br_dir = "/var/lib/pgbackrest"
    util.message("Removing '" + br_dir + "' directory at your request")
    os.system("sudo rm -rf " + br_dir)

if pgV > "":
    util.message("\n## Modify 'postgresql.conf' #########################")
    util.change_pgconf_keyval(pgV, "archive_command", "", p_replace=True)
    util.change_pgconf_keyval(pgV, "archive_mode", "off", p_replace=True)

    os.system("./pgedge restart " + pgV)
