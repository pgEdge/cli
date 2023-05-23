 
####################################################################
######          Copyright (c)  2022-2023 pgEdge           ##########
####################################################################

import util

util.change_pgconf_keyval("pgXX", "timescaledb.telemetry_level", "off")

util.create_extension("pgXX", "timescaledb", True)

