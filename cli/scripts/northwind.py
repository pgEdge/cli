#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

# (The northwind database originates from microsoft : http://northwinddatabase.codeplex.com/license)
# Microsoft Public License (Ms-PL)

import util, cluster, os, sys

g_tables = "northwind.*"

g_repset = "nw-repset"


def setup_node(
    node_nm, port, nc, num_nodes, my_home, db, pg, host, factor, os_user, ssh_key
):
    spk = nc + " spock "
    app = nc + " app "

    cmd = app + "northwind-install " + str(db)
    util.echo_cmd(cmd, host=host, usr=os_user, key=ssh_key)

    dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
    util.echo_cmd(
        spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )

    util.echo_cmd(
        spk + "repset-create " + g_repset + " --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )

    util.echo_cmd(
        spk + "repset-add-table " + g_repset + " " + g_tables + " --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )


def install(cluster_name, factor=1):
    util.message("\n# loading cluster definition ######")
    il, db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = cluster.load_json(
        cluster_name
    )
    db_pg = " " + str(db) + " --pg=" + str(pg)

    util.message("\n# setup individual nodes ##########")
    for nd in nodes:
        nodename = nd["nodename"]
        try:
            port = str(nd["port"])
        except Exception as e:
            port = "5432"
        host = nd["ip"]
        nc = nd["path"] + "/pgedge/ctl "
        my_home = nd["path"] + "/pgedge"
        setup_node(
            nodename,
            port,
            nc,
            count,
            my_home,
            db,
            str(pg),
            host,
            factor,
            os_user=os_user,
            ssh_key=ssh_key,
        )

    util.message("\n# wire nodes together #############")
    for pub in nodes:
        try:
            pubport = str(pub["port"])
        except Exception as e:
            pubport = "5432"
        pub_ip_port = "host=" + str(pub["ip"]) + " port=" + pubport
        spk = pub["path"] + "/pgedge/ctl spock "
        host = pub["ip"]

        for sub in nodes:
            try:
                subport = str(sub["port"])
            except Exception as e:
                subport = "5432"
            sub_ip_port = "host=" + str(sub["ip"]) + " port=" + subport

            if pub_ip_port != sub_ip_port:
                sub_name = "sub_" + pub["nodename"] + sub["nodename"] + " "
                provider_dsn = (
                    "'" + sub_ip_port + " user=" + os_user + " dbname=" + db + "' "
                )

                util.echo_cmd(
                    spk + "sub-create " + sub_name + provider_dsn + db_pg,
                    host=host,
                    usr=os_user,
                    key=ssh_key,
                )
                util.echo_cmd(
                    spk + "sub-add-repset " + sub_name + " " + g_repset + " " + db_pg,
                    host=host,
                    usr=os_user,
                    key=ssh_key,
                )


def remove(cluster_name):
    il, db, pg, count, db_usr, db_passwd, os_user, ssh_key, nodes = cluster.load_json(
        cluster_name
    )
    db_pg = " " + str(db) + " --pg=" + str(pg)

    rc2 = 0
    for pub in nodes:
        app = pub["path"] + "/pgedge/ctl app "
        host = pub["ip"]
        print("")
        rc1 = util.echo_cmd(
            app + "northwind-remove " + db_pg, host=host, usr=os_user, key=ssh_key
        )
        rc2 = rc2 + rc1

    sys.exit(rc2)
