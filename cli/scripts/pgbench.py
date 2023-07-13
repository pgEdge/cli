#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import util, cluster

def setup_node(node_nm, port, nc, num_nodes, db, pg, host, factor, os_user, ssh_key):
  pgb = nc + " pgbin "
  spk = nc + " spock "
  scale = int(num_nodes) * int(factor)
  pgbench_cmd = '"pgbench --initialize --scale=' + str(scale) + ' ' + str(db) + '"'
  util.echo_cmd(pgb + str(pg) +  " " + pgbench_cmd, host=host, usr=os_user, key=ssh_key)

  dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
  util.echo_cmd(spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db,
                 host=host, usr=os_user, key=ssh_key)

  rep_set = 'pgbench-repset'
  util.echo_cmd(spk + "repset-create " + rep_set + " --db " + db,
                  host=host, usr=os_user, key=ssh_key)
  util.echo_cmd(spk + "repset-add-table " + rep_set + " public.pgbench* --db " + db,
                  host=host, usr=os_user, key=ssh_key)

  log_old_val("pgbench_accounts", "abalance", "true", nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
  log_old_val("pgbench_branches", "bbalance", "true", nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
  log_old_val("pgbench_tellers",  "tbalance", "true", nc, db, pg,
                host=host, usr=os_user, key=ssh_key)


def psql_cmd(cmd, nc, db, pg, host, usr, key):
  util.echo_cmd(nc + "psql " + str(pg) + " \"" + cmd + "\" " + db,
                  host=host, usr=usr, key=key)


def log_old_val(tbl, col, val, nc, db, pg, host, usr, key):
  cmd = "ALTER TABLE " + tbl + " ALTER COLUMN " + col + \
    " SET (LOG_OLD_VALUE=" + val + ")"
  psql_cmd(cmd, nc, db, pg, host, usr, key)


def install(cluster_name, factor=1):
  util.message("\n# loading cluster definition ######")
  db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = cluster.load_json(cluster_name)
  db_pg = " " + str(db) + " --pg=" + str(pg)

  util.message("\n# setup individual nodes ##########")
  for nd in nodes:
    nodename = nd["nodename"]
    port = nd["port"]
    host = nd["ip"]
    nc = nd["path"] + "/pgedge/nodectl "
    setup_node(nodename, port, nc, count, db, str(pg), host, factor,
                 os_user=os_user, ssh_key=ssh_key)

  util.message("\n# wire nodes together #############")
  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = pub["path"] + "/pgedge/nodectl spock "
    host = pub["ip"]

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        provider_dsn = "'" + sub_ip_port + " user=" + os_user + " dbname=" + db + "' "

        util.echo_cmd(spk + "sub-create " + sub_name + provider_dsn + db_pg, 
                        host=host, usr=os_user, key=ssh_key)
        util.echo_cmd(spk + "sub-add-repset " + sub_name + " pgbench-repset " + db_pg, 
                        host=host, usr=os_user, key=ssh_key)


def remove(cluster_name):
  db, pg, count, db_usr, db_passwd, os_user, ssh_key, nodes = cluster.load_json(cluster_name)
  db_pg = " " + str(db) + " --pg=" + str(pg)

  for pub in nodes:
    pub_ip_port = "host=" + str(pub["ip"]) + " port=" + str(pub["port"])
    spk = pub["path"] + "/pgedge/nodectl spock "
    host = pub["ip"]

    for sub in nodes:
      sub_ip_port = "host=" + str(sub["ip"]) + " port=" + str(sub["port"])

      if pub_ip_port != sub_ip_port:
        sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
        util.echo_cmd(spk + "sub-drop " + sub_name + db_pg, 
                        host=host, usr=os_user, key=ssh_key)

  for nd in nodes:
    host = nd["ip"]
    nc =nd["path"] + "/pgedge/nodectl "
    spk = nc + "spock "
    util.echo_cmd(spk + "repset-drop pgbench-repset" + db_pg, 
                    host=host, usr=os_user, key=ssh_key)
    util.echo_cmd(spk + "node-drop " + nd["nodename"] + db_pg, 
                    host=host, usr=os_user, key=ssh_key)
    psql_cmd("DROP TABLE pgbench_history",  nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
    psql_cmd("DROP TABLE pgbench_accounts", nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
    psql_cmd("DROP TABLE pgbench_tellers",  nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
    psql_cmd("DROP TABLE pgbench_branches", nc, db, pg,
                host=host, usr=os_user, key=ssh_key)
 
