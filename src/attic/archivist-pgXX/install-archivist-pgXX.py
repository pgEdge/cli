 
####################################################################
######          Copyright (c)  2020-2021 PGSQL.IO         ##########
####################################################################

import util

util.change_pgconf_keyval("pgXX", "track_io_timing", "on", True)

util.run_sql_cmd("pgXX", "CREATE EXTENSION btree_gist", True)

util.create_extension("pgXX", "pg_stat_statements", True, "pg_stat_statements")
util.create_extension("pgXX", "powa", True, "powa")

