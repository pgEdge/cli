 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "pg_readonly")

