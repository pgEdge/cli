 
####################################################################
######          Copyright (c)  2020-2022 OSCG-P           ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "pg_hint_plan")

