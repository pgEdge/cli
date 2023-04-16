#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def install_node(node_nm, nc, num_nodes, db, pg, usr):
  pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
  util.echo_cmd(nc + "pgbin " + str(pg) +  " " + pgbench_cmd)

  rep_set = 'pgbench-repset'
  dsn = "'host=localhost user=" + usr + "'"

  util.echo_cmd(nc + " spock node-create '" + node_nm + "' --dsn 'host=localhost' --db " + db)
  util.echo_cmd(nc + " spock repset-create " + rep_set + " --db " + db)
  util.echo_cmd(nc + " spock repset-add-table " + rep_set + " public.pgbench* --db " + db)

  log_old_val("pgbench_accounts", "abalance", "true", nc, db, pg)
  log_old_val("pgbench_branches", "bbalance", "true", nc, db, pg)
  log_old_val("pgbench_tellers",  "tbalance", "true", nc, db, pg)


def log_old_val(tbl, col, val, nc, db, pg):
    cmd = "ALTER TABLE " + tbl + " ALTER COLUMN " + col + " SET (LOG_OLD_VALUE=" + val + ")"
    util.echo_cmd(nc + "pgbin " + str(pg) +  " " +  '"psql -c \\"' + cmd + '\\" ' + db + '"')


def wire_nodes(node_nm, nc, num_nodes, db, pg, usr):
  print(f"DEBUG: pgbench.wire_nodes({node_nm}, {nc}, {num_nodes}, {db}, {pg}, {usr})")
  util.exit_message("Not implemented yet!!")


def install(cluster_name):
  util.message("# loading cluster definition")
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)

  ## setup individual nodes
  for nd in nodes:
    nodename = nd["nodename"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    setup_node(nodename, nc, count, db, pg, usr)

  ## wire nodes together
  for nd in nodes:
    nodename = nd["nodename"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    wire_nodes(nodename, nc, count, db, pg, usr)


def remove_node(cluster_name, node):
  pass


def remove(cluster_name):
  for nd in nodes:
    print(nd["nodename"] + "Goodbye!!")


