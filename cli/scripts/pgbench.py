#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def setup_node(node_nm, port, nc, num_nodes, db, pg, usr, host):
  pgb = nc + " pgbin "
  spk = nc + " spock "
  pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
  util.echo_cmd(pgb + str(pg) +  " " + pgbench_cmd, host)

  dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
  util.echo_cmd(spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db, host)

  rep_set = 'pgbench-repset'
  util.echo_cmd(spk + "repset-create " + rep_set + " --db " + db, host)
  util.echo_cmd(spk + "repset-add-table " + rep_set + " public.pgbench* --db " + db, host)

  log_old_val("pgbench_accounts", "abalance", "true", nc, db, pg)
  log_old_val("pgbench_branches", "bbalance", "true", nc, db, pg)
  log_old_val("pgbench_tellers",  "tbalance", "true", nc, db, pg)


def psql_cmd(cmd, nc, db, pg):
    util.echo_cmd(nc + "psql " + str(pg) + " \"" + cmd + "\" " + db)


def log_old_val(tbl, col, val, nc, db, pg):
    cmd = "ALTER TABLE " + tbl + " ALTER COLUMN " + col + " SET (LOG_OLD_VALUE=" + val + ")"
    psql_cmd(cmd, nc, db, pg)


def install(cluster_name):
  util.message("\n# loading cluster definition ######")
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  db_pg = " " + str(db) + " --pg=" + str(pg)

  util.message("\n# setup individual nodes ##########")
  for nd in nodes:
    nodename = nd["nodename"]
    port = nd["port"]
    host = nd["ip"]
    nc = nd["path"] + "/nodectl "
    setup_node(nodename, port, nc, count, db, str(pg), usr, host)

  util.message("\n# wire nodes together #############")
  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = "cluster/" + pub["path"] + "/nodectl spock "
    host = pub["ip"]

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        provider_dsn = "'" + sub_ip_port + " user=" + usr + " dbname=" + db + "' "

        util.echo_cmd(spk + "sub-create " + sub_name + provider_dsn + db_pg, host)
        util.echo_cmd(spk + "sub-add-repset " + sub_name + " pgbench-repset " + db_pg, host)


def remove(cluster_name):
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  db_pg = " " + str(db) + " --pg=" + str(pg)

  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = "cluster/" + pub["path"] + "/nodectl spock "
    host = pub["ip"]

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        util.echo_cmd(spk + "sub-drop " + sub_name + db_pg, host)

  for nd in nodes:
    host = nd["ip"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    spk = nc + "spock "
    util.echo_cmd(spk + "repset-drop pgbench-repset" + db_pg, host)
    util.echo_cmd(spk + "node-drop " + nd["nodename"] + db_pg, host)
    psql_cmd("DROP TABLE pgbench_history",  nc, db, pg)
    psql_cmd("DROP TABLE pgbench_accounts", nc, db, pg)
    psql_cmd("DROP TABLE pgbench_tellers",  nc, db, pg)
    psql_cmd("DROP TABLE pgbench_branches", nc, db, pg)
 
