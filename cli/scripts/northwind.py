#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

# (The northwind database originates from microsoft : http://northwinddatabase.codeplex.com/license)
# Microsoft Public License (Ms-PL)

import util, cluster, os

g_tables = ("public.employees", "public.region", "public.categories", "public.us_states", "public.territories", "public.suppliers",
            "public.shippers", "public.products", "public.customers", "public.orders", "public.order_details",
            "public.employee_territories", "public.customer_demographics", "public.customer_customer_demo") 

g_repset = "nw-repset"

g_running_sums = ("products.units_in_stock", "products.units_on_order")


def setup_node(node_nm, port, nc, num_nodes, my_home, db, pg, host, factor, os_user, ssh_key):
  spk = nc + " spock "

  sql_file = my_home + os.sep + "hub/scripts/sql/northwind.sql"
  cmd = nc + " psql " + str(pg) + " -f " + sql_file
  util.echo_cmd(cmd, host=host, usr=os_user, key=ssh_key)

  dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
  util.echo_cmd(spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db,
                 host=host, usr=os_user, key=ssh_key)

  util.echo_cmd(spk + "repset-create " + g_repset + " --db " + db,
                  host=host, usr=os_user, key=ssh_key)

  cluster.add_repset_tables(spk, g_repset, g_tables, db, host, os_user, ssh_key)

  cluster.log_old_vals(g_running_sums, nc, db, pg, host, os_user, ssh_key)


def install(cluster_name, factor=1):
  util.message("\n# loading cluster definition ######")
  il, db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = cluster.load_json(cluster_name)
  db_pg = " " + str(db) + " --pg=" + str(pg)

  util.message("\n# setup individual nodes ##########")
  for nd in nodes:
    nodename = nd["nodename"]
    port = nd["port"]
    host = nd["ip"]
    nc = nd["path"] + "/pgedge/nodectl "
    my_home = nd["path"] + "/pgedge"
    setup_node(nodename, port, nc, count, my_home, db, str(pg), host, factor,
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
  il, db, pg, count, db_usr, db_passwd, os_user, ssh_key, nodes = cluster.load_json(cluster_name)
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

    cluster.drop_tables(g_tables, nc, db, pg, host, os_user, ssh_key)

