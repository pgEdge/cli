 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           ##########
####################################################################

import util, datetime, os

util.change_pgconf_keyval("pgXX", "wal_level", "logical", True)
util.change_pgconf_keyval("pgXX", "max_worker_processes", "10", True)
util.change_pgconf_keyval("pgXX", "max_replication_slots", "10", True)
util.change_pgconf_keyval("pgXX", "max_wal_senders", "10", True)

util.change_pgconf_keyval("pgXX", "track_commit_timestamp", "on", True)
#util.change_pgconf_keyval("pgXX", "log_min_messages", "debug3", True)

util.change_pgconf_keyval("pgXX", "log_destination", "stderr, csvlog")

util.change_pgconf_keyval("pgXX", "pglogical.conflict_resolution", "last_update_wins", True)

day = datetime.datetime.now().strftime('%a')
logdir = util.get_column("logdir", "pgXX")

util.create_extension("pgXX", "pglogical", True)


