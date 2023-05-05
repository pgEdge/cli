#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def setup_node(node_nm, port, nc, num_nodes, db, pg, usr):
  pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
  util.echo_cmd(nc + "pgbin " + str(pg) +  " " + pgbench_cmd)

  rep_set = 'pgbench-repset'
  dsn = "'host=" + util.get_1st_ip() + " port=" + str(port) + " user=" + usr + "'"

  util.echo_cmd(nc + " spock node-create " + node_nm + " --dsn " + dsn + " --db " + db)
  util.echo_cmd(nc + " spock repset-create " + rep_set + " --db " + db)
  util.echo_cmd(nc + " spock repset-add-table " + rep_set + " public.pgbench* --db " + db)

  log_old_val("pgbench_accounts", "abalance", "true", nc, db, pg)
  log_old_val("pgbench_branches", "bbalance", "true", nc, db, pg)
  log_old_val("pgbench_tellers",  "tbalance", "true", nc, db, pg)


def log_old_val(tbl, col, val, nc, db, pg):
    cmd = "ALTER TABLE " + tbl + " ALTER COLUMN " + col + " SET (LOG_OLD_VALUE=" + val + ")"
    util.echo_cmd(nc + "pgbin " + str(pg) +  " " +  '"psql -c \\"' + cmd + '\\" ' + db + '"')


def install(cluster_name):
  util.message("\n# loading cluster definition ######")
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)

  util.message("\n# setup indivisual nodes ##########")
  for nd in nodes:
    nodename = nd["nodename"]
    port = nd["port"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    setup_node(nodename, port, nc, count, db, pg, usr)

  util.message("\n# wire nodes together #############")
  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    nc = "cluster/" + pub["path"] + "/nodectl "

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        provider_dsn = "'" + sub_ip_port + " user=" + usr + " dbname=" + db + "' "

        util.echo_cmd(nc + " spock sub-create " + sub_name + provider_dsn + \
           db + " --pg=" + pg)

        util.echo_cmd(nc + " spock sub-add-repset " + sub_name + " pgbench-repset " + \
           db + " --pg=" + pg)


def remove_node(cluster_name, node):
  pass


def remove(cluster_name):
  for nd in nodes:
    print(nd["nodename"] + "Goodbye!!")

