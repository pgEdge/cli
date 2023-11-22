
#  Copyright 2022-2024 PGEDGE  All rights reserved. #


import sys
import util, cluster


def setup_node(node_nm, port, nc, num_nodes, db, pg, host, os_user, ssh_key):
    pgb = nc + " pgbin "
    spk = nc + " spock "
    app = nc + " app "

    util.echo_cmd(app + "pgbench-install " + db, host=host, usr=os_user, key=ssh_key)

    dsn = "'host=127.0.0.1 port=" + str(port) + " dbname=" + db + "'"
    util.echo_cmd(
        spk + "node-create " + node_nm + " --dsn " + dsn + " --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )

    rep_set = "pgbench-repset"
    util.echo_cmd(
        spk + "repset-create " + rep_set + " --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )
    util.echo_cmd(
        spk + "repset-add-table " + rep_set + " public.pgbench* --db " + db,
        host=host,
        usr=os_user,
        key=ssh_key,
    )


def log_old_val(tbl, col, val, nc, db, pg, host, usr, key):
    cmd = (
        "ALTER TABLE "
        + tbl
        + " ALTER COLUMN "
        + col
        + " SET (LOG_OLD_VALUE="
        + val
        + ")"
    )
    util.psql_cmd(cmd, nc, db, pg, host, usr, key)


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
        setup_node(
            nodename,
            port,
            nc,
            count,
            db,
            str(pg),
            host,
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
                    spk + "sub-add-repset " + sub_name + " pgbench-repset " + db_pg,
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
            app + "pgbench-remove " + db_pg, host=host, usr=os_user, key=ssh_key
        )
        rc2 = rc2 + rc1

    sys.exit(rc2)
