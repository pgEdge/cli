
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, fire, meta
import pgbench, northwind

base_dir = "cluster"


def remote_create(node_size, provider_locations):
    """Create a hybrid multi-cloud pgEdge cluster."""
    pass


def log_old_vals(p_run_sums, p_nc, p_db, p_pg, p_host, p_usr, p_key):
    for tbl_col in p_run_sums:
        tbl_col_lst = tbl_col.split(".")
        tbl = tbl_col_lst[0] + "." + tbl_col_lst[1]
        col = tbl_col_lst[2]

        cmd = (
            "ALTER TABLE " + tbl + " ALTER COLUMN " + col + " SET (LOG_OLD_VALUE=true)"
        )
        util.psql_cmd(cmd, p_nc, p_db, p_pg, p_host, p_usr, p_key)


def create_local_json(cluster_name, db, num_nodes, usr, passwd, pg, port1):
    cluster_dir = base_dir + os.sep + cluster_name
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    cluster_json = {}
    cluster_json["cluster"] = cluster_name
    cluster_json["is_localhost"] = "True"
    cluster_json["create_dt"] = datetime.date.today().isoformat()
    cluster_json["db_name"] = db
    cluster_json["db_user"] = usr
    cluster_json["db_init_passwd"] = passwd
    cluster_json["os_user"] = util.get_user()
    cluster_json["ssh_key"] = ""
    cluster_json["pg_ver"] = pg
    cluster_json["count"] = num_nodes
    cluster_json["nodes"] = []
    for n in range(1, num_nodes + 1):
        node_json = {}
        node_json["nodename"] = "n" + str(n)
        node_json["ip"] = "127.0.0.1"
        node_json["port"] = port1
        node_json["path"] = (
            os.getcwd()
            + os.sep
            + "cluster"
            + os.sep
            + cluster_name
            + os.sep
            + "n"
            + str(n)
        )
        cluster_json["nodes"].append(node_json)
        port1 = port1 + 1
    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to create JSON file", 1)


def create_remote_json(
    cluster_name, db, num_nodes, usr, passwd, pg, create_dt, id, nodes
):
    cluster_dir = base_dir + os.sep + cluster_name
    os.system("mkdir -p " + cluster_dir)
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    cluster_json = {}
    cluster_json["cluster"] = cluster_name
    cluster_json["id"] = id
    cluster_json["is_localhost"] = "False"
    cluster_json["create_dt"] = create_dt
    cluster_json["db_name"] = db
    cluster_json["db_user"] = usr
    cluster_json["db_init_passwd"] = passwd
    cluster_json["os_user"] = usr
    cluster_json["ssh_key"] = ""
    cluster_json["pg_ver"] = pg
    cluster_json["count"] = num_nodes
    cluster_json["nodes"] = nodes
    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to create JSON file", 1)


def load_json(cluster_name):
    parsed_json = get_cluster_json(cluster_name)

    is_local = parsed_json["is_localhost"]
    db_name = parsed_json["db_name"]
    pg = parsed_json["pg_ver"]
    count = parsed_json["count"]
    db_user = parsed_json["db_user"]
    db_passwd = parsed_json["db_init_passwd"]
    os_user = parsed_json["os_user"]
    ssh_key = parsed_json["ssh_key"]
    return (
        is_local,
        db_name,
        pg,
        count,
        db_user,
        db_passwd,
        os_user,
        ssh_key,
        parsed_json["nodes"],
    )


def get_cluster_json(cluster_name):
    cluster_dir = base_dir + os.sep + cluster_name
    cluster_file = cluster_dir + os.sep + cluster_name + ".json"

    if not os.path.isdir(cluster_dir):
        util.exit_message(f"Cluster directory '{cluster_dir}' not found")

    if not os.path.isfile(cluster_file):
        util.exit_message(f"Cluster file '{cluster_file}' not found")

    parsed_json = None
    try:
        with open(cluster_file) as f:
            parsed_json = json.load(f)
    except Exception as e:
        util.exit_message(f"Unable to load cluster def file '{cluster_file}\n{e}")

    return parsed_json


def remote_import_def(cluster_name, json_file_name):
    """Import a cluster definition file so we can work with it like a pgEdge cluster."""

    try:
        with open(json_file_name) as f:
            json.load(f)
    except FileNotFoundError:
        util.exit_message(f"file '{json_file_name}' not found")
    except Exception as e:
        util.exit_message(
            f"Unable to parse file '{json_file_name}' into json object.\n  {e.msg}"
        )

    cluster_dir = f"cluster/{cluster_name}"

    util.echo_cmd(f"mkdir -p {cluster_dir}")

    util.echo_cmd(f"cp {json_file_name} {cluster_dir}/{cluster_name}.json")


def remote_reset(cluster_name):
    """Reset a test cluster from json definition file of existing nodes."""
    il, db, pg, count, user, db_passwd, os_user, key, nodes = load_json(cluster_name)

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + "/ctl stop 2> /dev/null"
        util.echo_cmd(cmd, host=nd["ip"], usr=os_user, key=key)

    util.message("\n## Ensure that pgEdge root directory is gone")
    for nd in nodes:
        cmd = "rm -rf " + nd["path"]
        util.echo_cmd(cmd, host=nd["ip"], usr=os_user, key=key)


def remote_init(cluster_name):
    """Initialize a test cluster from json definition file of existing nodes."""

    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    cj = get_cluster_json(cluster_name)

    util.message("\n## Checking node count")
    try:
        kount = cj["count"]
        nodes = cj["nodes"]
        if len(nodes) != kount:
            util.exit_message(
                f"Invalid node count '{kount}' versus actual nodes '{len(nodes)}'"
            )
    except Exception as e:
        util.exit_message(f"error parsing config file\n{str(e)}")
    util.message(f"### Node count = {kount}")

    util.message("\n## Checking ssh'ing to each node")
    for nd in cj["nodes"]:
        rc = util.echo_cmd(
            usr=cj["os_user"], host=nd["ip"], key=cj["ssh_key"], cmd="hostname"
        )
        if rc == 0:
            print("OK")
        else:
            util.exit_message("cannot ssh to node")

    ssh_install_pgedge(cluster_name, cj["db_init_passwd"])


def local_create(
    cluster_name,
    num_nodes,
    pg="16",
    port1=6432,
    User="lcusr",
    Passwd="lcpasswd",
    db="lcdb",
):
    """Create a localhost test cluster of N pgEdge nodes on different ports."""

    util.message("# verifying passwordless ssh...")
    if util.is_password_less_ssh():
        pass
    else:
        util.exit_message("passwordless ssh not configured on localhost", 1)

    cluster_dir = base_dir + os.sep + cluster_name

    try:
        num_nodes = int(num_nodes)
    except Exception:
        util.exit_message("num_nodes parameter is not an integer", 1)

    try:
        port1 = int(port1)
    except Exception:
        util.exit_message("port1 parameter is not an integer", 1)

    kount = meta.get_installed_count()
    if kount > 1:
        util.message(
            "WARNING: No other components should be installed when using 'cluster local'"
        )

    if num_nodes < 1:
        util.exit_message("num-nodes must be >= 1", 1)

    #  increment port1 to the first available port from it's initial value
    n = port1
    while util.is_socket_busy(n):
        util.message(f"# port {n} is busy")
        n = n + 1
    port1 = n

    if os.path.exists(cluster_dir):
        util.exit_message("cluster already exists: " + str(cluster_dir), 1)

    util.message("# creating cluster dir: " + os.getcwd() + os.sep + cluster_dir)
    os.system("mkdir -p " + cluster_dir)

    pg = os.getenv("pgN", pg)
    db = os.getenv("pgName", db)
    User = os.getenv("pgeUser", User)
    Passwd = os.getenv("pgePasswd", Passwd)

    create_local_json(cluster_name, db, num_nodes, User, Passwd, pg, port1)

    ssh_install_pgedge(cluster_name, Passwd)


def print_install_hdr(cluster_name, db, pg, db_user, count):
    util.message("#")
    util.message(
        f"######## ssh_install_pgedge: cluster={cluster_name}, db={db}, pg={pg} db_user={db_user}, count={count}"
    )


def ssh_install_pgedge(cluster_name, passwd):
    il, db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = load_json(
        cluster_name
    )
    for n in nodes:
        print_install_hdr(cluster_name, db, pg, db_user, count)
        ndnm = n["nodename"]
        ndpath = n["path"]
        ndip = n["ip"]
        try:
            ndport = str(n["port"])
        except Exception:
            ndport = "5432"

        REPO = os.getenv("REPO", "")
        if REPO == "":
            REPO = "https://pgedge-download.s3.amazonaws.com/REPO"
            os.environ["REPO"] = REPO

        install_py = os.getenv("INSTALL_PY", "")
        if install_py == "":
            if "-upstream" in REPO:
                install_py = "install24.py"
            else:
                install_py = "install.py"

        util.message(
            f"########                node={ndnm}, host={ndip}, path={ndpath} REPO={REPO}\n"
        )

        cmd0 = f"export REPO={REPO}; "
        cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
        cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
        util.echo_cmd(cmd0 + cmd1 + cmd2, host=n["ip"], usr=os_user, key=ssh_key)

        nc = ndpath + "/pgedge/ctl "
        parms = (
            " -U "
            + str(db_user)
            + " -P "
            + str(passwd)
            + " -d "
            + str(db)
            + " -p "
            + str(ndport)
            + " --pg "
            + str(pg)
        )
        util.echo_cmd(
            nc + " install pgedge" + parms, host=n["ip"], usr=os_user, key=ssh_key
        )
        util.message("#")


def local_destroy(cluster_name):
    """Stop and then nuke a localhost cluster."""

    if not os.path.exists(base_dir):
        util.exit_message("no cluster directory: " + str(base_dir), 1)

    if cluster_name == "all":
        kount = 0
        for it in os.scandir(base_dir):
            if it.is_dir():
                kount = kount + 1
                lc_destroy1(it.name)

        if kount == 0:
            util.exit_message("no cluster(s) to delete", 1)

    else:
        lc_destroy1(cluster_name)


def lc_destroy1(cluster_name):
    cluster_dir = base_dir + "/" + str(cluster_name)

    cfg = get_cluster_json(cluster_name)

    try:
        is_localhost = cfg["is_localhost"]
    except Exception:
        is_localhost = "False"

    if is_localhost == "True":
        command(cluster_name, "all", "stop")
        util.echo_cmd("rm -rf " + cluster_dir)
    else:
        util.message(f"Cluster '{cluster_name}' is not a localhost cluster")


def command(cluster_name, node, cmd, args=None):
    """Run './ctl' commands on one or 'all' nodes."""

    il, db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = load_json(
        cluster_name
    )
    rc = 0
    knt = 0
    for nd in nodes:
        if node == "all" or node == nd["nodename"]:
            knt = knt + 1
            rc = util.echo_cmd(
                nd["path"] + "/pgedge/ctl " + cmd,
                host=nd["ip"],
                usr=os_user,
                key=ssh_key,
            )

    if knt == 0:
        util.message("# nothing to do")

    return rc


def app_install(cluster_name, app_name, factor=1):
    """Install test application [ pgbench | northwind ]."""

    if app_name == "pgbench":
        pgbench.install(cluster_name, factor)
    elif app_name == "northwind":
        northwind.install(cluster_name, factor)
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")


def app_remove(cluster_name, app_name):
    """Remove test application from cluster."""
    if app_name == "pgbench":
        pgbench.remove(cluster_name)
    elif app_name == "northwind":
        northwind.remove(cluster_name)
    else:
        util.exit_message("Invalid application name.")


if __name__ == "__main__":
    fire.Fire(
        {
            "remote-create": remote_create,
            "remote-init": remote_init,
            "remote-reset": remote_reset,
            "remote-import-def": remote_import_def,
            "local-create": local_create,
            "local-destroy": local_destroy,
            "command": command,
            "app-install": app_install,
            "app-remove": app_remove,
        }
    )
