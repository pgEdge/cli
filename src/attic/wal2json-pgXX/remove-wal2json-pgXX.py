 
####################################################################
######          Copyright (c)  2022-2024 pgEdge           ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "wal2json")

