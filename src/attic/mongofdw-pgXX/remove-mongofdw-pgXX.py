 
####################################################################
######          Copyright (c)  2015-2020 PGSQL.IO         ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "mongo_fdw")

