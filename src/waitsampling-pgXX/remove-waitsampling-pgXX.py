 
####################################################################
######          Copyright (c)  2020-2021 PGSQL.IO         ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "pg_wait_sampling")

