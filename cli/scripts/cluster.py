
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, fire, meta, time

BASE_DIR = "cluster"

def get_cluster_info(cluster_name):
    cluster_dir = os.path.join(BASE_DIR, cluster_name)
    os.system("mkdir -p " + cluster_dir)
    cluster_file = os.path.join(cluster_dir, f"{cluster_name}.json")
    util.message(f"get_cluster_info({cluster_name}) --> ({cluster_dir}, {cluster_file})", "debug")
    return (cluster_dir, cluster_file)


def get_cluster_json(cluster_name):
    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    if not os.path.isdir(cluster_dir):
        util.exit_message(f"Cluster directory '{cluster_dir}' not found")

    if not os.path.isfile(cluster_file):
        util.message(f"Cluster file '{cluster_file}' not found", "warning")
        return None

    parsed_json = None
    try:
        with open(cluster_file, "r") as f:
            parsed_json = json.load(f)
    except Exception as e:
        util.exit_message(f"Unable to load cluster def file '{cluster_file}'\n{e}")

    util.message(f"parsed_json = \n{json.dumps(parsed_json, indent=2)}", "debug")
    return parsed_json


def write_cluster_json(cluster_name, cj):
    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    try:
        cjs = json.dumps(cj, indent=2)
        util.message(f"write_cluster_json {cluster_name}, {cluster_dir}, {cluster_file},\n{cjs}", "debug")
        f = open(cluster_file, "w")
        f.write(cjs)
        f.close()
    except Exception as e:
        util.exit_message("Unable to write_cluster_json {cluster_file}\n{str(e)}")


def json_create(cluster_name, style, db, user, passwd, pg):
    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = style
    cluster_json["create_date"] = datetime.datetime.now().isoformat(" ", "seconds")

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    db_json = {}
    db_json["username"] = user
    db_json["password"] = passwd
    db_json["name"] = db
    database_json["databases"].append(db_json)
    cluster_json["database"] = database_json

    cluster_json["node_groups"] = {style: []}

    write_cluster_json(cluster_name, cluster_json)


def json_add_node(cluster_name, node_group, node_name, is_active, ip_address, port, path, ssh_key=None, provider=None, airport=None):
    cj = get_cluster_json (cluster_name)

    util.message(f"json_add_node()\n{json.dumps(cj, indent=2)}", "debug")

    for ng in cj["node_groups"]:
      print(f"DEBUG: {ng}")

    node_json = {}
    node_json["name"] = node_name
    node_json["is_active"] = is_active
    node_json["ip_address"] = ip_address
    node_json["port"] = port
    node_json["path"] = path
    if ssh_key:
        node_json["ssh_key"] = ssh_key
    if provider:
        node_json["provider"] = provider
    if airport:
        node_json["airport"] = airport

    util.message(f"node_json = {node_json}")

    lhn = cj["node_groups"]
    print(f"lhn {lhn}")
    lhn["localhost"].append(node_json)

    write_cluster_json(cluster_name, cj)

    
def create_local_json(cluster_name, db, num_nodes, usr, passwd, pg, ports, hosts=None, paths=None, keys=None):
    """Create a json config file for a local cluster.
    
       Create a JSON configuration file that defines a local cluster. \n
       Example: cluster define-localhost demo lcdb 3 lcusr lcpasswd 16 5432
       :param cluster_name: The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
       :param db: The database name.
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgres version of the database.
       :param ports: The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number. 
    """

    util.message(f"create_local_json({cluster_name}, {db}, {num_nodes}, {usr}, {passwd}, {pg}, {ports})", "debug")

    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    ## rc = json_create(cluster_name, "localhost", db, usr, passwd, pg)

    ## json_add_node(cluster_name, "localhost", "n1", True, "127.0.0.1", "6432", "/tmp")

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

    port1 = ports
    port_a = str(ports).split(",")
    if len(port_a) == num_nodes:
       pass
    else:
       if len(port_a) == 1:
          port1 = ports
       else:
          util.exit_message("ports param '{ports}' does NOT match num_nodes = {num_nodes}")

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

    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    os.system("mkdir -p " + cluster_dir)
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")

    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = "remote"
    cluster_json["create_date"] = datetime.datetime.now().isoformat()

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


def update_json(cluster_name, db_json):
    parsed_json = get_cluster_json(cluster_name)

    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    os.system(f"mkdir -p {cluster_dir}{os.sep}backup")
    timeof = datetime.datetime.now().strftime('%y%m%d_%H%M')
    os.system(f"cp {cluster_dir}{os.sep}{cluster_name}.json {cluster_dir}{os.sep}backup/{cluster_name}_{timeof}.json")
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    parsed_json["database"]["databases"].append(db_json)
    try:
        text_file.write(json.dumps(parsed_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to update JSON file", 1)


def add_db(cluster_name, database_name, username, password):
    """Add a database to an existing cluster and cross wire it together.
    
       Create the new database in the cluster, install spock, and create all spock nodes and subscriptions.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n
       Example: cluster add-db demo test admin password
       :param cluster_name: The name of the existing cluster.
       :param database_name: The name of the new database.
       :param username: The name of the user that will be created and own the db. 
       :param password: The password for the new user.
    """
    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    db, pg, nodes = load_json(cluster_name)

    db_json = {}
    db_json["username"] = username
    db_json["password"] = password
    db_json["name"] = database_name

    util.message(f"## Creating database {database_name}")
    create_spock_db(nodes,db_json)
    ssh_cross_wire_pgedge(cluster_name, database_name, pg, username, password, nodes)
    util.message(f"## Updating cluster '{cluster_name}' json definition file")
    update_json(cluster_name, db_json)


def localhost_create(
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

Below is an example of the JSON file that is generated that defines a 2 node localhost cluster

{
  "name": "cl1",
  "style": "localhost",
  "create_date": "2024-02-23",
  "localhost": {
    "os_user": "rocky",
    "ssh_key": ""
  },
  "database": {
    "databases": [
      {
        "username": "lcusr",
        "password": "lcpasswd",
        "name": "lcdb"
      }
    ],
    "pg_version": "16"
  },
  "node_groups": {
    "localhost": [
      {
        "nodes": [
          {
            "name": "n1",
            "is_active": true,
            "ip_address": "127.0.0.1",
            "port": 6432,
            "path": "/home/rocky/dev/cli/out/posix/cluster/cl1/n1"
          }
        ]
      },
      {
        "nodes": [
          {
            "name": "n2",
            "is_active": true,
            "ip_address": "127.0.0.1",
            "port": 6433,
            "path": "/home/rocky/dev/cli/out/posix/cluster/cl1/n2"
          }
        ]
      }
    ]
  }
    """


    util.message("# verifying passwordless ssh...")
    if util.is_password_less_ssh():
        pass
    else:
        util.exit_message("passwordless ssh not configured on localhost", 1)

    cluster_dir, cluster_file = get_cluster_info(cluster_name)

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

        nc = os.path.join(ndpath, "pgedge", "pgedge ")
        parms = f" -U {db_user} -P {db_passwd} -d {db} --port {ndport} --pg {pg}"
        util.echo_cmd(f"{nc} setup {parms}", host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
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


def localhost_destroy(cluster_name):
    """Stop and then nuke a localhost cluster.
    
       Destroy a local cluster. This will stop postgres on each node, and then remove the pgedge directory for each node in a local cluster. \n
       Example: cluster local-destroy demo
       :param cluster_name: The name of the cluster. 
    """

    if not os.path.exists(BASE_DIR):
        util.exit_message("no cluster directory: " + str(BASE_DIR), 1)

    if cluster_name == "all":
        kount = 0
        for it in os.scandir(BASE_DIR):
            if it.is_dir():
                kount = kount + 1
                lc_destroy1(it.name)

        if kount == 0:
            util.exit_message("no cluster(s) to delete", 1)

    else:
        lc_destroy1(cluster_name)


def lc_destroy1(cluster_name):
    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    cfg = get_cluster_json(cluster_name)

    if cfg:
        if "localhost" in cfg:
            command(cluster_name, "all", "stop")
        else:
            util.message(f"Cluster '{cluster_name}' is not a localhost cluster")

    util.echo_cmd("rm -rf " + cluster_dir)


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
            "localhost-create": localhost_create,
            "localhost-destroy": localhost_destroy,
            "init": init,
            "add-db": add_db,
            "remove": remove,
            "command": command,
            "app-install": app_install,
            "app-remove": app_remove
        }
    )
