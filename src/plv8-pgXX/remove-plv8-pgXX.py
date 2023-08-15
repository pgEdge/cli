 
####################################################################
######          Copyright (c)  2021-2023 pgEdge           ##########
####################################################################

import util, sys

#print(f"Argument List: {sys.argv}")

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "plv8-3.2.0")

