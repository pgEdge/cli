
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, fire, meta, time
import pgbench, northwind

base_dir = "cluster"


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
    """Create a json config file for a local cluster."""
    cluster_dir = base_dir + os.sep + cluster_name
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = "localhost"
    cluster_json["create_date"] = datetime.date.today().isoformat()

    local_json = {}
    local_json["os_user"] = util.get_user()
    local_json["ssh_key"] = ""
    cluster_json["localhost"] = local_json

    database_json = {}
    database_json["username"] = usr
    database_json["password"] = passwd
    database_json["pg_version"] = pg
    database_json["name"] = db
    cluster_json["database"] = database_json

    
    local_nodes = {"localhost": []}
    for n in range(1, num_nodes + 1):
        node_array = {"nodes": []}
        node_json = {}
        node_json["name"] = "n" + str(n)
        node_json["is_active"] = True
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
        node_array["nodes"].append(node_json)
        local_nodes["localhost"].append(node_array)
        port1 = port1 + 1
    cluster_json["node_groups"] = local_nodes
    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to create JSON file", 1)


def create_remote_json(
    cluster_name, db, num_nodes, usr, passwd, pg, port
):
    """Create a template for a json config file for a remote cluster."""
    cluster_dir = base_dir + os.sep + cluster_name
    os.system("mkdir -p " + cluster_dir)
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")

    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = "remote"
    cluster_json["create_date"] = datetime.date.today().isoformat()

    remote_json = {}
    remote_json["os_user"] = ""
    remote_json["ssh_key"] = ""
    cluster_json["remote"] = remote_json

    database_json = {}
    database_json["username"] = usr
    database_json["password"] = passwd
    database_json["pg_version"] = pg
    database_json["name"] = db
    cluster_json["database"] = database_json

    remote_nodes = {"remote": []}
    for n in range(1, num_nodes + 1):
        node_array = {"region": ""}
        node_array.update({"availability_zones": ""})
        node_array.update({"instance_type": ""})
        node_array.update({"nodes": []})
        node_json = {}
        node_json["name"] = "n" + str(n)
        node_json["is_active"] = True
        node_json["ip"] = ""
        node_json["port"] = port
        node_json["path"] = ""
        node_array["nodes"].append(node_json)
        remote_nodes["remote"].append(node_array)
    cluster_json["node_groups"] = remote_nodes
    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to create JSON file", 1)


def load_json(cluster_name):
    parsed_json = get_cluster_json(cluster_name)

    db = parsed_json["database"]["name"]
    pg = parsed_json["database"]["pg_version"]
    user = parsed_json["database"]["username"]
    db_passwd = parsed_json["database"]["password"]
    node=[]

    if "remote" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["remote"]:
            if "remote" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["remote"])
                    node.append(n)
            else:
                util.exit_message("remote info missing from JSON", 1)

    if "aws" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["aws"]:
            if "aws" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["aws"])
                    node.append(n)
            else:
                util.exit_message("aws info missing from JSON", 1)

    if "azure" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["azure"]:
            if "remote" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["azure"])
                    node.append(n)
            else:
                util.exit_message("azure info missing from JSON", 1)           

    if "gcp" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["gcp"]:
            if "remote" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["gcp"])
                    node.append(n)        
            else:
                util.exit_message("gcp info missing from JSON", 1)      

    if "localhost" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["localhost"]:
            if "remote" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["localhost"])
                    node.append(n)  
            else:
                util.exit_message("localhost info missing from JSON", 1)
       
    return (
        db,
        pg,
        user,
        db_passwd,
        node
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
    db, pg, user, db_passwd, nodes = load_json(cluster_name)

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + "/ctl stop 2> /dev/null"
        util.echo_cmd(cmd, host=nd["ip"], usr=nd["os_user"], key=nd["ssh_key"])

    util.message("\n## Ensure that pgEdge root directory is gone")
    for nd in nodes:
        cmd = "rm -rf " + nd["path"]
        util.echo_cmd(cmd, host=nd["ip"], usr=nd["os_user"], key=nd["ssh_key"])


def remote_init(cluster_name):
    """Initialize a test cluster from json definition file of existing nodes."""

    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    cj = get_cluster_json(cluster_name)

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
    ssh_cross_wire_pgedge(cluster_name)


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
    ssh_cross_wire_pgedge(cluster_name)


def print_install_hdr(cluster_name, db, pg, db_user, count):
    util.message("#")
    util.message(
        f"######## ssh_install_pgedge: cluster={cluster_name}, db={db}, pg={pg} db_user={db_user}, count={count}"
    )


def ssh_install_pgedge(cluster_name, passwd):
    db, pg, db_user, db_passwd, nodes = load_json(
        cluster_name
    )
    for n in nodes:
        print_install_hdr(cluster_name, db, pg, db_user, len(nodes))
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
        util.echo_cmd(cmd0 + cmd1 + cmd2, host=n["ip"], usr=n["os_user"], key=n["ssh_key"])

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
            nc + " install pgedge" + parms, host=n["ip"], usr=n["os_user"], key=n["ssh_key"]
        )
        util.message("#")


def ssh_cross_wire_pgedge(cluster_name):
    db, pg, db_user, db_passwd, nodes = load_json(
        cluster_name
    )
    sub_array=[]
    for prov_n in nodes:
        ndnm = prov_n["nodename"]
        ndpath = prov_n["path"]
        nc = ndpath + "/pgedge/ctl"
        ndip = prov_n["ip"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]
        if "private_ip" in prov_n:
            ndip_private = prov_n["private_ip"]
        else:
            ndip_private = ndip
        try:
            ndport = str(prov_n["port"])
        except Exception:
            ndport = "5432"
        cmd1 = f"{nc} spock node-create {ndnm} 'host={ndip_private} user={os_user} dbname={db} port={ndport}' {db}"
        util.echo_cmd(cmd1, host=ndip, usr=os_user, key=ssh_key)
        cmd2 = f"{nc} spock repset-create {db}_repset {db}"
        util.echo_cmd(cmd2, host=ndip, usr=os_user, key=ssh_key)
        for sub_n in nodes:
            sub_ndnm = sub_n["nodename"]
            if sub_ndnm != ndnm:
                sub_ndip = sub_n["ip"]
                if "private_ip" in sub_n:
                    sub_ndip_private = sub_n["private_ip"]
                else:
                    sub_ndip_private = sub_ndip
                try:
                    sub_ndport = str(sub_n["port"])
                except Exception:
                    sub_ndport = "5432"
                cmd = f"{nc} spock sub-create sub_{ndnm}{sub_ndnm} 'host={sub_ndip_private} user={os_user} dbname={db} port={sub_ndport}' {db}"
                sub_array.append([cmd,ndip,os_user,ssh_key])
    ## To Do: Check Nodes have been created
    print(f"{nc} spock node-list {db}") ##, host=ndip, usr=os_user, key=ssh_key)
    time.sleep(10)
    for n in sub_array:
        cmd = n[0]
        nip = n[1]
        os_user = n[2]
        ssh_key = n[3]
        util.echo_cmd(cmd, host=nip, usr=os_user, key=ssh_key)
                
        

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

    db, pg, db_user, db_passwd, nodes = load_json(
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
                usr=nd["os_user"],
                key=nd["ssh_key"],
            )

    if knt == 0:
        util.message("# nothing to do")

    return rc


def app_install(cluster_name, app_name, factor=1):
    """Install test application [ pgbench | northwind ]."""
    db, pg, db_user, db_passwd, nodes = load_json(
            cluster_name
        )
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip"]
            util.echo_cmd(f"{ndpath}/pgedge/ctl app pgbench-install {db} {factor} default", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip"]
            util.echo_cmd(f"{ndpath}/pgedge/ctl app northwind-install {db} default", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")


def app_remove(cluster_name, app_name):
    """Remove test application from cluster."""
    db, pg, db_user, db_passwd, nodes = load_json(
            cluster_name
        )
    if app_name == "pgbench":
         for n in nodes:
            ndpath = n["path"]
            ndip = n["ip"]
            util.echo_cmd(f"{ndpath}/pgedge/ctl app pgbench-remove {db}", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
         for n in nodes:
            ndpath = n["path"]
            ndip = n["ip"]
            util.echo_cmd(f"{ndpath}/pgedge/ctl app northwind-remove {db}", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message("Invalid application name.")


if __name__ == "__main__":
    fire.Fire(
        {
            "define-localhost": create_local_json,
            "define-remote": create_remote_json,
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
