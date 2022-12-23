 
####################################################################
######          Copyright (c)  2020-2022 OSCG Partners    ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "pg_auto_failover")

