 
####################################################################
######          Copyright (c)  2015-2019 BigSQL           ##########
####################################################################

import util

##util.change_pgconf_keyval("pgXX", "timescaledb.telemetry_level", "off")

util.create_extension("pgXX", "timescaledb", True)

