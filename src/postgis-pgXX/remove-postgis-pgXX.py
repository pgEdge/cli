 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           ##########
####################################################################

import util

ver = "pgXX"
ext = "postgis-3"

util.remove_pgconf_keyval(ver, "shared_preload_libraries", ext)

