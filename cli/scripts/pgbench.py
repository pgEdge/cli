#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def setup_node(node_nm, port, nc, num_nodes, db, pg, usr):
  pgb = nc + " pgbin "
  spk = nc + " spock "
  pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
  util.echo_cmd(pgb + str(pg) +  " " + pgbench_cmd)

  dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
  util.echo_cmd(spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db)

  rep_set = 'pgbench-repset'
  util.echo_cmd(spk + "repset-create " + rep_set + " --db " + db)
  util.echo_cmd(spk + "repset-add-table " + rep_set + " public.pgbench* --db " + db)

  log_old_val("pgbench_accounts", "abalance", "true", nc, db, pg)
  log_old_val("pgbench_branches", "bbalance", "true", nc, db, pg)
  log_old_val("pgbench_tellers",  "tbalance", "true", nc, db, pg)


def psql_cmd(cmd, nc, db, pg):
    util.echo_cmd(nc + "pgbin " + str(pg) +  " " +  '"psql -c \\"' + cmd + '\\" ' + db + '"')


def log_old_val(tbl, col, val, nc, db, pg):
    cmd = "ALTER TABLE " + tbl + " ALTER COLUMN " + col + " SET (LOG_OLD_VALUE=" + val + ")"
    psql_cmd(cmd, nc, db, pg)


def install(cluster_name):
  util.message("\n# loading cluster definition ######")
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  db_pg = " " + db + " --pg=" + pg

  util.message("\n# setup individual nodes ##########")
  for nd in nodes:
    nodename = nd["nodename"]
    port = nd["port"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    setup_node(nodename, port, nc, count, db, pg, usr)

  util.message("\n# wire nodes together #############")
  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = "cluster/" + pub["path"] + "/nodectl spock "

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        provider_dsn = "'" + sub_ip_port + " user=" + usr + " dbname=" + db + "' "

        util.echo_cmd(spk + "sub-create " + sub_name + provider_dsn + db_pg)
        util.echo_cmd(spk + "sub-add-repset " + sub_name + " pgbench-repset " + db_pg)


def remove(cluster_name):
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  db_pg = " " + db + " --pg=" + pg

  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = "cluster/" + pub["path"] + "/nodectl spock "

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        util.echo_cmd(spk + "sub-drop " + sub_name + db_pg)

  for nd in nodes:
    nc = "cluster/" + nd["path"] + "/nodectl "
    spk = nc + "spock "
    util.echo_cmd(spk + "repset-drop pgbench-repset" + db_pg)
    util.echo_cmd(spk + "node-drop " + nd["nodename"] + db_pg)
    psql_cmd("DROP TABLE pgbench_history",  nc, db, pg)
    psql_cmd("DROP TABLE pgbench_accounts", nc, db, pg)
    psql_cmd("DROP TABLE pgbench_tellers",  nc, db, pg)
    psql_cmd("DROP TABLE pgbench_branches", nc, db, pg)
 
