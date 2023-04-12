#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def setup_node(node_nm, nc, num_nodes, db, pg, usr):
  print(f"DEBUG: pgbench.setup_node({node_nm}, {nc}, {num_nodes}, {db}, {pg}, {usr})")

  pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
  util.echo_cmd(nc + "pgbin " + str(pg) +  " " + pgbench_cmd)

  rep_set = 'pgbench-repset'
  dsn = "'host=localhost user=" + usr + "'"

  util.echo_cmd(nc + " spock node-create '" + node_nm + "' --dsn 'host=localhost' --db " + db)
  util.echo_cmd(nc + " spock repset-create " + rep_set + " --db " + db)
  util.echo_cmd(nc + " spock repset-add-table " + rep_set + " public.pgbench* --db " + db)


def setup_cluster(cluster_name):
  util.message("# loading cluster definition")
  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  print(f"DEBUG: {cluster_name} db={db} pg={pg} usr={usr}")

  for nd in nodes:
    nodename = nd["nodename"]
    nc = "cluster/" + nd["path"] + "/nodectl "
    print(f"nodename={nodename}, nc='{nc}'")
    print(nd)
    setup_node(nodename, nc, count, db, pg, usr)

