 
####################################################################
######          Copyright (c)  2021-2022 OSCG             ##########
####################################################################

import util

ver = "pgXX"
ext = "multicorn"

util.remove_pgconf_keyval(ver, "shared_preload_libraries", ext)

