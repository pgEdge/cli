#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

# (The northwind database originates from microsoft : http://northwinddatabase.codeplex.com/license)
# Microsoft Public License (Ms-PL)

import util, cluster

g_tables = ("employees", "region", "categories", "us_states", "territories", "suppliers",
            "shippers", "products", "customers", "orders", "order_details",
            "employee_territories", "customer_demographics", "customer_customer_demo") 

g_repset = "nw-repset"

g_running_sums = ("products.units_in_stock", "products.units_on_order")


def setup_node(node_nm, port, nc, num_nodes, db, pg, host, factor, os_user, ssh_key):
  pgb = nc + " pgbin "
  spk = nc + " spock "

  ########### T0DO ######################
  scale = int(num_nodes) * int(factor)
  pgbench_cmd = '"pgbench --initialize --scale=' + str(scale) + ' ' + str(db) + '"'
  util.echo_cmd(pgb + str(pg) +  " " + pgbench_cmd, host=host, usr=os_user, key=ssh_key)
  ########## END TODO ##################

  dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
  util.echo_cmd(spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db,
                 host=host, usr=os_user, key=ssh_key)

  util.echo_cmd(spk + "repset-create " + g_repset + " --db " + db,
                  host=host, usr=os_user, key=ssh_key)

  cluster.add_repset_tables(spk, g_repset, p_tbls, db, host, os_usr, ssh_key)

  cluster.log_old_vals(g_running_sums, nc, db, pg, host, os_user, ssh_key)


def psql_cmd(cmd, nc, db, pg, host, usr, key):
  util.echo_cmd(nc + "psql " + str(pg) + " \"" + cmd + "\" " + db,
                  host=host, usr=usr, key=key)


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
        util.echo_cmd(spk + "sub-add-repset " + sub_name + " " + g_repset + " " + db_pg, 
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
    util.echo_cmd(spk + "repset-drop " + g_repset + " " + db_pg, 
                    host=host, usr=os_user, key=ssh_key)
    util.echo_cmd(spk + "node-drop " + nd["nodename"] + db_pg, 
                    host=host, usr=os_user, key=ssh_key)

    cluster.drop_tables(tables, nc, db, pg, host, os_user, ssh_key)

