
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, fire, meta, time

base_dir = "cluster"


def create_local_json(cluster_name, db, num_nodes, usr, passwd, pg, port1):
    """Create a json config file for a local cluster.
    
       Create a JSON configuration file that defines a local cluster. \n
       Example: cluster define-localhost demo lcdb 3 lcusr lcpasswd 16 5432
       :param cluster_name: The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
       :param db: The database name.
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgres version of the database.
       :param port1: The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number. 
    """

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

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    db_json = {}
    db_json["username"] = usr
    db_json["password"] = passwd
    db_json["name"] = db
    database_json["databases"].append(db_json)
    cluster_json["database"] = database_json
    
    local_nodes = {"localhost": []}
    for n in range(1, num_nodes + 1):
        node_array = {"nodes": []}
        node_json = {}
        node_json["name"] = "n" + str(n)
        node_json["is_active"] = True
        node_json["ip_address"] = "127.0.0.1"
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
    """Create a template for a json config file for a remote cluster.
    
       Create a JSON configuration file template that can be modified to fully define a remote cluster. \n
       Example: cluster define-remote demo lcdb 3 lcusr lcpasswd 16 5432
       :param cluster_name: The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
       :param db: The database name.
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgres version of the database.
       :param port1: The port number for the database. 
    """

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

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    db_json = {}
    db_json["username"] = usr
    db_json["password"] = passwd
    db_json["name"] = db
    database_json["databases"].append(db_json)
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
        node_json["ip_address"] = ""
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
    """Load a json config file for a cluster."""

    parsed_json = get_cluster_json(cluster_name)

    pg = parsed_json["database"]["pg_version"]
    
    db=[]
    for databases in parsed_json["database"]["databases"]:
        db.append(databases)
    
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
            if "azure" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["azure"])
                    node.append(n)
            else:
                util.exit_message("azure info missing from JSON", 1)           

    if "gcp" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["gcp"]:
            if "gcp" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["gcp"])
                    node.append(n)        
            else:
                util.exit_message("gcp info missing from JSON", 1)      

    if "localhost" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["localhost"]:
            if "localhost" in parsed_json:
                for n in group["nodes"]:
                    n.update(parsed_json["localhost"])
                    node.append(n)  
            else:
                util.exit_message("localhost info missing from JSON", 1)
       
    return (
        db,
        pg,
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


def remove(cluster_name):
    """Remove a test cluster from json definition file of existing nodes.
    
       Remove a cluster. This will stop postgres on each node, and then remove the pgedge directory on each node.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster remove demo 
       :param cluster_name: The name of the cluster. 
    """
    db, pg, nodes = load_json(cluster_name)

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + os.sep + "pgedge stop 2> " + os.sep + "dev" + os.sep + "null"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])

    util.message("\n## Ensure that pgEdge root directory is gone")
    for nd in nodes:
        cmd = f"rm -rf " + nd["path"] + os.sep + "pgedge"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])


def init(cluster_name):
    """Initialize a cluster from json definition file of existing nodes.
    
       Install pgedge on each node, create the initial database, install spock, and create all spock nodes and subscriptions. 
       Additional databases will be created with all spock nodes and subscriptions if defined in the json file.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster init demo 
       :param cluster_name: The name of the cluster. 
    """

    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    db, pg, nodes = load_json(cluster_name)

    util.message("\n## Checking ssh'ing to each node")
    for nd in nodes:
        rc = util.echo_cmd(
            usr=nd["os_user"], host=nd["ip_address"], key=nd["ssh_key"], cmd="hostname"
        )
        if rc == 0:
            print("OK")
        else:
            util.exit_message("cannot ssh to node")

    ssh_install_pgedge(cluster_name, db[0]["name"], pg, db[0]["username"], db[0]["password"], nodes)
    ssh_cross_wire_pgedge(cluster_name, db[0]["name"], pg, db[0]["username"], db[0]["password"], nodes)
    if len(db) > 1:
        for database in db[1:]:
            create_spock_db(nodes,database)
            ssh_cross_wire_pgedge(cluster_name, database["name"], pg, database["username"], database["password"], nodes)        


def local_create(
    cluster_name,
    num_nodes,
    pg="16",
    port1=6432,
    User="lcusr",
    Passwd="lcpasswd",
    db="lcdb",
):
    """Create a localhost test cluster of N pgEdge nodes on different ports.
    
       Create a local cluster. Each node will be located in the cluster/<cluster_name>/<node_name> directory. Each database will have a different port. \n
       Example: cluster local-create demo 3 lcusr lcpasswd 16 6432 lcdb
       :param cluster_name: The name of the cluster. 
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgreSQL version of the database.
       :param port1: The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number. 
       :param db: The database name.
    """
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
    db, pg, nodes = load_json(
        cluster_name
    )

    ssh_install_pgedge(cluster_name, db[0]["name"], pg, db[0]["username"], db[0]["password"], nodes)
    ssh_cross_wire_pgedge(cluster_name, db[0]["name"], pg, db[0]["username"], db[0]["password"], nodes)
    if len(db) > 1:
        for database in db[1:]:
            create_spock_db(nodes,database)
            ssh_cross_wire_pgedge(cluster_name, database["name"], pg, database["username"], database["password"], nodes)        
    

def print_install_hdr(cluster_name, db, pg, db_user, count):
    util.message("#")
    util.message(
        f"######## ssh_install_pgedge: cluster={cluster_name}, db={db}, pg={pg} db_user={db_user}, count={count}"
    )


def ssh_install_pgedge(cluster_name, db, pg, db_user, db_passwd, nodes):
    """Install pgEdge on every node in a cluster."""

    for n in nodes:
        print_install_hdr(cluster_name, db, pg, db_user, len(nodes))
        ndnm = n["name"]
        ndpath = n["path"]
        ndip = n["ip_address"]
        try:
            ndport = str(n["port"])
        except Exception:
            ndport = "5432"

        REPO = os.getenv("REPO", "")
        if REPO == "":
            REPO = "https://pgedge-upstream.s3.amazonaws.com/REPO"
            os.environ["REPO"] = REPO

        install_py = "install.py"

        util.message(
            f"########                node={ndnm}, host={ndip}, path={ndpath} REPO={REPO}\n"
        )
        
        cmd0 = f"export REPO={REPO}; "
        cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
        cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
        util.echo_cmd(cmd0 + cmd1 + cmd2, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])

        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge "
        parms = (
            " -U "
            + str(db_user)
            + " -P "
            + str(db_passwd)
            + " -d "
            + str(db)
            + " -p "
            + str(ndport)
            + " --pg "
            + str(pg)
        )
        util.echo_cmd(
            nc + " install pgedge" + parms, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"]
        )
        util.message("#")


def create_spock_db(nodes,db):
    for n in nodes:
            nc = n["path"] + os.sep + "pgedge" + os.sep + "pgedge "
            cmd = nc + " db create -U " + db["username"] + " -d " + db["name"] + " -p " + db["password"]
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])


def ssh_cross_wire_pgedge(cluster_name, db, pg, db_user, db_passwd, nodes):
    """Create nodes, repsets, and subs on every node in a cluster."""

    sub_array=[]
    for prov_n in nodes:
        ndnm = prov_n["name"]
        ndpath = prov_n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = prov_n["ip_address"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]
        if "ip_address_private" in prov_n and prov_n["ip_address_private"] != "":
            ndip_private = prov_n["ip_address_private"]
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
            sub_ndnm = sub_n["name"]
            if sub_ndnm != ndnm:
                sub_ndip = sub_n["ip_address"]
                if "ip_address_private" in sub_n and sub_n["ip_address_private"] != "":
                    sub_ndip_private = sub_n["ip_address_private"]
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
    """Stop and then nuke a localhost cluster.
    
       Destroy a local cluster. This will stop postgres on each node, and then remove the pgedge directory for each node in a local cluster. \n
       Example: cluster local-destroy demo
       :param cluster_name: The name of the cluster. 
    """

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
    cluster_dir = base_dir + os.sep + str(cluster_name)

    cfg = get_cluster_json(cluster_name)
    if "localhost" in cfg:
        command(cluster_name, "all", "stop")
        util.echo_cmd("rm -rf " + cluster_dir)
    else:
        util.message(f"Cluster '{cluster_name}' is not a localhost cluster")        


def command(cluster_name, node, cmd, args=None):
    """Run './pgedge' commands on one or 'all' nodes.
    
       Run './pgedge' commands on one or all of the nodes in a cluster. 
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster command demo n1 "status"
       Example: cluster command demo all "spock repset-add-table default '*' lcdb"
       :param cluster_name: The name of the cluster.
       :param node: The node to run the command on. Can be the node name or all.
       :param cmd: The command to run on every node, excluding the beginning './pgedge' 
    """

    db, pg, nodes = load_json(
        cluster_name
    )
    rc = 0
    knt = 0
    for nd in nodes:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            rc = util.echo_cmd(
                nd["path"] + os.sep + "pgedge" + os.sep + "pgedge " + cmd,
                host=nd["ip_address"],
                usr=nd["os_user"],
                key=nd["ssh_key"],
            )

    if knt == 0:
        util.message("# nothing to do")

    return rc


def app_install(cluster_name, app_name, database_name=None, factor=1):
    """Install test application [ pgbench | northwind ].
    
       Install a test application on all of the nodes in a cluster. 
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster app-install pgbench
       :param cluster_name: The name of the cluster.
       :param node: The application name, pgbench or northwind.
       :param factor: The scale flag for pgbench.
    """
    db, pg, nodes = load_json(
            cluster_name
        )
    db_name=None
    if database_name is None:
        db_name=db[0]["name"]
    else:
        for i in db:
            if i["name"]==database_name:
                db_name=database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    ctl =  os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app pgbench-install {db_name} {factor} default", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app northwind-install {db} default", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")


def app_remove(cluster_name, app_name, database_name=None):
    """Remove test application from cluster.
    
       Remove a test application from all of the nodes in a cluster. 
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster app-remove pgbench
       :param cluster_name: The name of the cluster.
       :param node: The application name, pgbench or northwind.
    """
    db, pg, nodes = load_json(
            cluster_name
        )
    db_name=None
    if database_name is None:
        db_name=db[0]["name"]
    else:
        for i in db:
            if i["name"]==database_name:
                db_name=database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    ctl =  os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
         for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app pgbench-remove {db_name}", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
         for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app northwind-remove {db}", host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message("Invalid application name.")


if __name__ == "__main__":
    fire.Fire(
        {
            "define-localhost": create_local_json,
            "define-remote": create_remote_json,
            "local-create": local_create,
            "local-destroy": local_destroy,
            "init": init,
            "remove": remove,
            "command": command,
            "app-install": app_install,
            "app-remove": app_remove
        }
    )
