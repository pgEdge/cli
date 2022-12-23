 
####################################################################
######          Copyright (c)  2020-2021 OpenRDS          ##########
####################################################################

import util, os

util.change_pgconf_keyval("pgXX", "wal_level", "logical", True)
util.change_pgconf_keyval("pgXX", "max_worker_processes", "10", True)
util.change_pgconf_keyval("pgXX", "max_replication_slots", "10", True)
util.change_pgconf_keyval("pgXX", "max_wal_senders", "10", True)

## TODO This is for demo and isn't yet secure ################
sql="CREATE ROLE replication WITH SUPERUSER REPLICATION LOGIN ENCRYPTED PASSWORD 'password'"
util.run_sql_cmd("pgXX", sql, False)

datadir = util.get_column("datadir", "pgXX")
os.system("cp " + datadir + "/pg_hba.conf " + datadir + "/pg_hba.conf.orig")

thisdir = os.path.dirname(os.path.realpath(__file__))
os.system("cp " + thisdir + "/pg_hba.conf.replication " + datadir + "/pg_hba.conf")

util.change_pgconf_keyval("pgXX", "shared_preload_libraries", "decoderbufs")
util.restart_postgres("pgXX")


