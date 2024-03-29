
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


def json_create(cluster_name, style, db=None, user=None, passwd=None, pg=None):
    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = style
    cluster_json["create_date"] = datetime.datetime.now().isoformat(" ", "seconds")

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    database_json["spock_version"] = ""
    database_json["auto_ddl"] = "off"
    db_json = {}
    db_json["username"] = user
    db_json["password"] = passwd
    db_json["name"] = db
    database_json["databases"].append(db_json)
    cluster_json["database"] = database_json

    cluster_json["node_groups"] = {style: []}

    write_cluster_json(cluster_name, cluster_json)


def json_add_node(cluster_name, node_group, node_name, is_active, ip_address, port, path, os_user=None, ssh_key=None, provider=None, airport=None):
    cj = get_cluster_json (cluster_name)

    util.message(f"json_add_node()\n{json.dumps(cj, indent=2)}", "debug")

    node_json = {}
    node_json["name"] = node_name
    node_json["is_active"] = is_active
    node_json["ip_address"] = ip_address
    node_json["port"] = port
    node_json["path"] = path
    if os_user:
        node_json["os_user"] = os_user
    if ssh_key:
        node_json["ssh_key"] = ssh_key
    if provider:
        node_json["provider"] = provider
    if airport:
        node_json["airport"] = airport

    util.message(f"node_json = {node_json}", "debug")

    lhn = cj["node_groups"]
    lhn[node_group].append(node_json)

    write_cluster_json(cluster_name, cj)

    

def create_remote_json(
    cluster_name, db, num_nodes, usr, passwd, pg, port
):
    """Create a template for a Cluster Configuration JSON file.
    
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
    database_json["spock_version"] = ""
    database_json["auto_ddl"] = "off"
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
        node_json["ip_address_private"] = ""
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
    spock = ""
    auto_ddl = "off"
    if "spock_version" in parsed_json["database"]:
        spock = parsed_json["database"]["spock_version"]
    if "auto_ddl" in parsed_json["database"]:
        auto_ddl = parsed_json["database"]["auto_ddl"]

    db_settings = {}
    db_settings["pg_version"] = pg
    db_settings["spock_version"] = spock
    db_settings["auto_ddl"] = auto_ddl
 
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
        db_settings,
        node
    )


def validate(cluster_name):
    """Validate a Cluster Configuration JSON file"""

    parsed_json = get_cluster_json(cluster_name)    

    if "name" not in parsed_json:
        util.exit_message("Cluster name missing")

    if "database" not in parsed_json:
        util.exit_message("Database section missing")
    else:
        if "pg_version" not in parsed_json["database"]:
            parsed_json["database"]["pg_version"] = ""
        if "spock" not in parsed_json["database"]:
            parsed_json["database"]["spock_version"]=""
        if "auto_ddl" not in parsed_json["database"]:
            parsed_json["database"]["auto_ddl"]="off"
        if "databases" not in parsed_json["database"]:
            util.exit_message("Database Details section missing")
        if 1 > len(parsed_json["database"]["databases"]):
            util.exit_message("At least one database needs to be defined")
        else:
            for db in parsed_json["database"]["databases"]:
                if "name" not in db:
                    util.exit_message("Database Name missing")
                elif "username" not in db:
                    util.exit_message("User missing for " + db["name"])
                elif "password" not in db:
                    util.exit_message("Password missing for " + db["name"])

    if "node_groups" not in parsed_json:
        util.exit_message("Node Group section missing")
    db, db_settings, nodes = load_json(cluster_name)
    util.message(f"JSON defines a {len(nodes)} node cluster", 'success')
    

def remove(cluster_name, force=False):
    """Remove a test cluster.
    
       Remove a cluster. This will remove spock subscriptions and nodes, and then stop postgres on each node. If the flag force is set to true, then it will also remove the pgedge directory on each node.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster remove demo 
       :param cluster_name: The name of the cluster. 
    """
    db, db_settings, nodes = load_json(cluster_name)

    ssh_un_cross_wire(cluster_name, db[0]["name"], db_settings, db[0]["username"], db[0]["password"], nodes)

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + os.sep + "pgedge stop 2> " + os.sep + "dev" + os.sep + "null"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])

    if force == True:
        util.message("\n## Ensure that pgEdge root directory is gone")
        for nd in nodes:
            cmd = f"rm -rf " + nd["path"] + os.sep + "pgedge"
            util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])


def init(cluster_name):
    """Initialize a cluster via Cluster Configuration JSON file.
    
       Install pgedge on each node, create the initial database, install spock, and create all spock nodes and subscriptions. 
       Additional databases will be created with all spock nodes and subscriptions if defined in the json file.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: cluster init demo 
       :param cluster_name: The name of the cluster. 
    """

    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    db, db_settings, nodes = load_json(cluster_name)

    util.message("\n## Checking ssh'ing to each node")
    for nd in nodes:
        rc = util.echo_cmd(
            usr=nd["os_user"], host=nd["ip_address"], key=nd["ssh_key"], cmd="hostname"
        )
        if rc == 0:
            print("OK")
        else:
            util.exit_message("cannot ssh to node")

    ssh_install_pgedge(cluster_name, db[0]["name"], db_settings, db[0]["username"], db[0]["password"], nodes)
    ssh_cross_wire_pgedge(cluster_name, db[0]["name"], db_settings, db[0]["username"], db[0]["password"], nodes)
    if len(db) > 1:
        for database in db[1:]:
            create_spock_db(nodes,database,db_settings)
            ssh_cross_wire_pgedge(cluster_name, database["name"], db_settings, database["username"], database["password"], nodes)        


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
    """Add a database to an existing pgEdge cluster.
    
       Create the new database in the cluster, install spock, and create all spock nodes and subscriptions.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n
       Example: cluster add-db demo test admin password
       :param cluster_name: The name of the existing cluster.
       :param database_name: The name of the new database.
       :param username: The name of the user that will be created and own the db. 
       :param password: The password for the new user.
    """
    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    db, db_settings, nodes = load_json(cluster_name)

    db_json = {}
    db_json["username"] = username
    db_json["password"] = password
    db_json["name"] = database_name

    util.message(f"## Creating database {database_name}")
    create_spock_db(nodes,db_json, db_settings)
    ssh_cross_wire_pgedge(cluster_name, database_name, db_settings, username, password, nodes)
    util.message(f"## Updating cluster '{cluster_name}' json definition file")
    update_json(cluster_name, db_json)



def print_install_hdr(cluster_name, db, db_user, count):
    util.message("#")
    util.message(
        f"######## ssh_install_pgedge: cluster={cluster_name}, db={db}, db_user={db_user}, count={count}"
    )


def ssh_install_pgedge(cluster_name, db, db_settings, db_user, db_passwd, nodes):
    """Install pgEdge on every node in a cluster."""

    for n in nodes:
        print_install_hdr(cluster_name, db, db_user, len(nodes))
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
        pg = db_settings["pg_version"]
        spock = db_settings["spock_version"]        

        cmd0 = f"export REPO={REPO}; "
        cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
        cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
        util.echo_cmd(cmd0 + cmd1 + cmd2, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])

        nc = os.path.join(ndpath, "pgedge", "pgedge ")
        parms = f" -U {db_user} -P {db_passwd} -d {db} --port {ndport}"
        if pg is not None and pg != '':
            parms = parms + f" --pg {pg}"
        if spock is not None and spock != '':
            parms = parms + f" --spock_ver {spock}"
        util.echo_cmd(f"{nc} setup {parms}", host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
        if db_settings["auto_ddl"] == "on":
            cmd = nc + " db guc-set spock.enable_ddl_replication on;"
            cmd = cmd + " " + nc + " db guc-set spock.include_ddl_repset on;"
            cmd = cmd + " " + nc + " db guc-set spock.allow_ddl_from_functions on;"
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
        util.message("#")


def create_spock_db(nodes,db,db_settings):
    for n in nodes:
        nc = n["path"] + os.sep + "pgedge" + os.sep + "pgedge "
        cmd = nc + " db create -U " + db["username"] + " -d " + db["name"] + " -p " + db["password"]
        util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
        if db_settings["auto_ddl"] == "on":
            cmd = nc + " db guc-set spock.enable_ddl_replication on;"
            cmd = cmd + " " + nc + " db guc-set spock.include_ddl_repset on;"
            cmd = cmd + " " + nc + " db guc-set spock.allow_ddl_from_functions on;"
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])

def ssh_cross_wire_pgedge(cluster_name, db, db_settings, db_user, db_passwd, nodes):
    """Create nodes and subs on every node in a cluster."""

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


def ssh_un_cross_wire(cluster_name, db, db_settings, db_user, db_passwd, nodes):
    """Create nodes and subs on every node in a cluster."""
    sub_array=[]
    for prov_n in nodes:
        ndnm = prov_n["name"]
        ndpath = prov_n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = prov_n["ip_address"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]
        for sub_n in nodes:
            sub_ndnm = sub_n["name"]
            if sub_ndnm != ndnm:
                cmd = f"{nc} spock sub-drop sub_{ndnm}{sub_ndnm} {db}"
                util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)

    for prov_n in nodes:
        ndnm = prov_n["name"]
        ndpath = prov_n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = prov_n["ip_address"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]
        cmd1 = f"{nc} spock node-drop {ndnm} {db}"
        util.echo_cmd(cmd1, host=ndip, usr=os_user, key=ssh_key)
    ## To Do: Check Nodes have been dropped


def replication_all_tables(cluster_name, database_name=None):
    """Add all tables in the database to replication on every node"""
    db, db_settings, nodes = load_json(cluster_name)
    db_name=None
    if database_name is None:
        db_name=db[0]["name"]
    else:
        for i in db:
            if i["name"]==database_name:
                db_name=database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    if "auto_ddl" in db_settings:
        if db_settings["auto_ddl"] == "on":
            util.exit_message(f"Auto DDL enabled for db {database_name}")

    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["ip_address"]
        os_user = n["os_user"]
        ssh_key = n["ssh_key"]
        cmd = f"{nc} spock repset-add-table default '*' {db_name}"
        util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)


def replication_check(cluster_name, show_spock_tables=False, database_name=None):
    """Print replication status on every node"""
    db, db_settings, nodes = load_json(cluster_name)
    db_name=None
    if database_name is None:
        db_name=db[0]["name"]
    else:
        for i in db:
            if i["name"]==database_name:
                db_name=database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["ip_address"]
        os_user = n["os_user"]
        ssh_key = n["ssh_key"]
        if show_spock_tables == True:
            cmd = f"{nc} spock repset-list-tables '*' {db_name}"
            util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)
        cmd = f"{nc} spock sub-show-status '*' {db_name}"
        util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)


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

    db, db_settings, nodes = load_json(
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
    db, db_settings, nodes = load_json(
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
            util.echo_cmd(f"{ndpath}{ctl} app northwind-install {db_name} default", host=ndip, usr=n["os_user"], key=n["ssh_key"])
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
    db, db_settings, nodes = load_json(
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
            "json-template": create_remote_json,
            "json-validate": validate,
            "init": init,
            "replication-begin": replication_all_tables,
            "replication-check": replication_check,
            "add-db": add_db,
            "remove": remove,
            "command": command,
            "app-install": app_install,
            "app-remove": app_remove
        }
    )
