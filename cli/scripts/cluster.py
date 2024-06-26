
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, fire, meta, time, sys
try:
    import etcd, patroni
except Exception:
    pass

BASE_DIR = "cluster"

def ssh(cluster_name, node_name):
    """An SSH Terminal session into the specified node"""

    db, db_settings, nodes = load_json(cluster_name)
   
    for nd in nodes:
       if node_name == nd["name"]:
          util.echo_cmd(f'ssh -i ~/keys/eqn-test-key {nd["os_user"]}@{nd["ip_address"]}')
          util.exit_cleanly(0)

    util.exit_message(f"Could not locate node '{node_name}'")


def set_firewalld(cluster_name):
    """ Open up nodes only to each other on pg port (WIP)"""
    
    ## install & start firewalld if not present
    rc = util.echo_cmd("sudo firewall-cmd --version")
    if rc != 0:
       rc = util.echo_cmd("sudo dnf install -y firewalld")
       rc = util.echo_cmd("sudo systemctl start firewalld")

    db, db_settings, nodes = load_json(cluster_name)

    for nd in nodes:
       util.message(f'OUT name={nd["name"]}, ip_address={nd["ip_address"]}, port={nd["port"]}', "info")
       out_name = nd["name"]
       for in_nd in nodes:
          if in_nd["name"] != out_name:
             print(f'   IN    name={in_nd["name"]}, ip_address={in_nd["ip_address"]}, port={in_nd["port"]}')


def get_cluster_info(cluster_name):
    cluster_dir = os.path.join(util.MY_HOME, BASE_DIR, cluster_name)
    os.system("mkdir -p " + cluster_dir)
    cluster_file = os.path.join(cluster_dir, f"{cluster_name}.json")
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


def json_create(cluster_name, style, db="demo", user="user1", passwd="passwd1", pg="16", os_user=None, ssh_key=None):
    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = style
    cluster_json["create_date"] = datetime.datetime.now().isoformat(" ", "seconds")

    style_json = {}
    style_json["os_user"] = os_user
    style_json["ssh_key"] = ssh_key
    cluster_json["remote"] = style_json

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    database_json["spock_version"] = ""
    database_json["auto_ddl"] = "off"
    database_json["auto_start"] = "off"
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

    nodes = {"nodes": [node_json]}

    util.message(f"nodes = {nodes}", "debug")

    lhn = cj["node_groups"]
    lhn[node_group].append(nodes)

    write_cluster_json(cluster_name, cj)

    

def create_remote_json(
    cluster_name, db, num_nodes, usr, passwd, pg, port
):
    """Create a template for a Cluster Configuration JSON file.
    
       Create a JSON configuration file template that can be modified to fully define a remote cluster. \n
       Example: cluster define-remote demo db[0]["name"] 3 lcusr lcpasswd 16 5432
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
    database_json["auto_start"] = "off"
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
    if parsed_json is None:
        util.exit_message("Unable to load_json cluster")

    pg = parsed_json["database"]["pg_version"]
    spock = ""
    auto_ddl = "off"
    auto_start = "off"
    if "spock_version" in parsed_json["database"]:
        spock = parsed_json["database"]["spock_version"]
    if "auto_ddl" in parsed_json["database"]:
        auto_ddl = parsed_json["database"]["auto_ddl"]
    if "auto_start" in parsed_json["database"]:
        auto_start = parsed_json["database"]["auto_start"]

    db_settings = {
        "pg_version": pg,
        "spock_version": spock,
        "auto_ddl": auto_ddl,
        "auto_start": auto_start
    }

    db = parsed_json["database"]["databases"]

    node = []

    def process_nodes(group, group_name):
        if group_name in parsed_json:
            for n in group["nodes"]:
                n.update(parsed_json[group_name])
                if "subnodes" in n:
                    for subnode in n["subnodes"]:
                        subnode["parent_node"] = n["name"]
                        subnode["os_user"] = n["os_user"]
                        subnode["ssh_key"] = n["ssh_key"]
                node.append(n)
        else:
            util.exit_message(f"{group_name} info missing from JSON", 1)

    if "remote" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["remote"]:
            process_nodes(group, "remote")

    if "aws" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["aws"]:
            process_nodes(group, "aws")

    if "azure" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["azure"]:
            process_nodes(group, "azure")

    if "gcp" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["gcp"]:
            process_nodes(group, "gcp")

    if "localhost" in parsed_json["node_groups"]:
        for group in parsed_json["node_groups"]["localhost"]:
            process_nodes(group, "localhost")

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
            util.exit_message("pg_version is missing")
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
    """
    Initialize a cluster via Cluster Configuration JSON file.

    Install pgedge on each node, create the initial database, install spock,
    and create all spock nodes and subscriptions. Additional databases will
    be created with all spock nodes and subscriptions if defined in the JSON
    file. This command requires a JSON file with the same name as the cluster
    to be in the cluster/<cluster_name>.

    Example: cluster init demo
    :param cluster_name: The name of the cluster.
    """

    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    db, db_settings, nodes = load_json(cluster_name)
    parsed_json = get_cluster_json(cluster_name)
   
    if parsed_json.get("log_level"):
       verbose = parsed_json["log_level"]
    else:
       verbose = "Info"

    for nd in nodes:
        message = f"Checking ssh on {nd['ip_address']}"
        util.run_rcommand(
            cmd="hostname",
            message=message,
            host=nd["ip_address"],
            usr=nd["os_user"],
            key=nd["ssh_key"],
            verbose=verbose
        )

    ssh_install_pgedge(
        cluster_name, db[0]["name"], db_settings, db[0]["username"],
        db[0]["password"], nodes, True, " "
    )
    ssh_cross_wire_pgedge(
        cluster_name, db[0]["name"], db_settings, db[0]["username"],
        db[0]["password"], nodes
    )

    if len(db) > 1:
        for database in db[1:]:
            create_spock_db(nodes, database, db_settings)
            ssh_cross_wire_pgedge(
                cluster_name, database["name"], db_settings, database["username"],
                database["password"], nodes
            )

    pg_ver = db_settings["pg_version"]
    for node in nodes:
        system_identifier = get_system_identifier(db[0], node)
        if "subnodes" in node:
            for n in node["subnodes"]:
                ssh_install(
                    cluster_name, db[0]["name"], db_settings, db[0]["username"],
                    db[0]["password"], n, False, " "
                )

    if any("subnodes" in node for node in nodes):
        configure_etcd(cluster_name, system_identifier)
        configure_patroni(cluster_name)

def get_system_identifier(db, n):
    cmd = "SELECT system_identifier FROM pg_control_system()"
    try:
        op = util.psql_cmd_output(
            cmd, 
            f"{n['path']}/pgedge/pgedge", 
            db["name"], 
            "",
            host=n["ip_address"], 
            usr=n["os_user"], 
            key=n["ssh_key"]
        )
        lines = op.splitlines()
        for line in lines:
            # Look for the line that appears after the header line
            if line.strip() and line.strip().isdigit():
                system_identifier = line.strip()
                return system_identifier
        raise ValueError("System identifier not found in the output")
    except Exception as e:
        return str(e)

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

def print_install_hdr(cluster_name, db, db_user, count, name, path, ip, port, repo, primary, primary_name):
    
    if primary:
        node_type = "Primary"
    else:
        node_type = "Replica"

    node = {
        "REPO": repo,
        "Cluster Name": cluster_name,
        "Node Type": node_type,
        "Primary Node Name": primary_name,
        "Name": name,
        "Host": ip,
        "Port": port,
        "Path": path,
        "Database": db,
        "Database User": db_user,
        "Number of Nodes": count,
    }
    util.echo_node(node)

def ssh_install(cluster_name, db, db_settings, db_user, db_passwd, n, primary, primary_name):
    REPO = os.getenv("REPO", "")
    ndnm = n["name"]
    ndpath = n["path"]
    ndip = n["ip_address"]
    pg = db_settings["pg_version"]
    try:
        ndport = str(n["port"])
    except Exception:
        ndport = "5432"

    if REPO == "":
        REPO = "https://pgedge-upstream.s3.amazonaws.com/REPO"
        os.environ["REPO"] = REPO

    install_py = "install.py"

    pg = db_settings["pg_version"]
    spock = db_settings["spock_version"]        

    cmd0 = f"export REPO={REPO}; "
    cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
    cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
    util.echo_cmd(cmd0 + cmd1 + cmd2, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
    
    nc = os.path.join(ndpath, "pgedge", "pgedge ")
    cmd = f"{nc} install pg{pg}"
    util.run_rcommand(
        cmd,
        message=f"Installing pg{pg} on {ndnm}",
        host=n["ip_address"], usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
        )

def ssh_install_pgedge(cluster_name, db, db_settings, db_user, db_passwd, nodes, primary, primary_name):
    """Install pgEdge on every node in a cluster."""

    for n in nodes:
        REPO = os.getenv("REPO", "")
        print_install_hdr(cluster_name, db, db_user, len(nodes), n["name"], n["path"], n["ip_address"], n["port"], REPO, primary, primary_name)
        ndnm = n["name"]
        ndpath = n["path"]
        ndip = n["ip_address"]
        try:
            ndport = str(n["port"])
        except Exception:
            ndport = "5432"

        if REPO == "":
            REPO = "https://pgedge-upstream.s3.amazonaws.com/REPO"
            os.environ["REPO"] = REPO

        install_py = "install.py"

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
        if db_settings["auto_start"] == "on":
            parms = f"{parms} --autostart"
        util.echo_cmd(f"{nc} setup {parms}", host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
        if db_settings["auto_ddl"] == "on":
            cmd = nc + " db guc-set spock.enable_ddl_replication on;"
            cmd = cmd + " " + nc + " db guc-set spock.include_ddl_repset on;"
            cmd = cmd + " " + nc + " db guc-set spock.allow_ddl_from_functions on;"
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])
        util.message("#")
    return 0


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
       Example: cluster command demo all "spock repset-add-table default '*' db[0]["name"]"
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

def list_nodes(cluster_name):
    """List all nodes in the cluster."""
    
    cluster_data = get_cluster_json(cluster_name)

    nodes_list = []
    for group in cluster_data['node_groups']['aws']:
        for node in group['nodes']:
            node_info = (
                f"Node: {node['name']}, IP: {node['ip_address']}, "
                f"Port: {node['port']}, Active: {'Yes' if node['is_active'] else 'No'}"
            )
            nodes_list.append(node_info)

    return nodes_list

def add_node(cluster_name, source_node, target_node, script= " ", stanza=" ", backup_id = " "):
    """
    Adds a new node to a cluster, copying configurations from a specified 
    source node.

    Args:
        cluster_name (str): The name of the cluster to which the node is being 
                            added.
        source_node (str): The node from which configurations are copied.
        target_node (str): The new node being added.
        stanza (str): Stanza name.
        backup_id (str): Backup ID.
        script (str): Bash script.
    """
    cluster_data = get_cluster_json(cluster_name)
    parsed_json = get_cluster_json(cluster_name)
    pg = parsed_json["database"]["pg_version"]
    stanza_create = False
    if stanza == " ":
        stanza = f"pg{pg}"
    
    if parsed_json.get("log_level"):
       verbose = parsed_json["log_level"]
    else:
       verbose = "Info"
    
    node_file = f"{target_node}.json"
    if not os.path.exists(node_file):
        util.exit_message(f"Error: Missing node configuration file '{node_file}'.")
        return

    with open(node_file, 'r') as file:
        data = json.load(file)

    if 'aws' in data:
        aws_config = data['aws']
        for node_config in aws_config:
            node_data = node_config['nodes']
            for node in node_data:
                print(f"Node Name: {node['name']}")
    if 'localhost' in data:
        local_config = data['localhost']
        for node_config in local_config:
            node_data = node_config['nodes']
            for node in node_data:
                print(f"Node Name: {node['name']}")

    n = node_data[0]
    
    node_groups = cluster_data.get('node_groups', {})
    if 'aws' in data:
        nodes = node_groups.get('aws', [])
    if 'localhost' in data:
        nodes = node_groups.get('localhost', [])

    for node_group in nodes:
        nodes = node_group.get('nodes', [])
        for node in nodes:
            if node.get('name') == n['name']:
                util.exit_message(f"Error: node {n['name']} already exists.")
                break

    db, db_settings, nodes = load_json(cluster_name)
    s = next((node for node in nodes if node['name'] == source_node), None)
    if s is None:
        util.exit_message(f"Error: Source node '{source_node}' not found in cluster data.")
        return

    dbname = db[0]["name"]
    n.update({
        'os_user': s['os_user'],
        'ssh_key': s['ssh_key'],
    })

    util.echo_message(f"Installing and Configuring new node\n", bold=True)
    
    util.echo_action(f"Installing postgresql \n")
    rc = ssh_install_pgedge(cluster_name, dbname, db_settings, db[0]["username"],
                                db[0]["password"], node_data, True, " ")
    if rc == 0:    
        util.echo_action(f"Installing postgresql ", "ok")
    else:
        util.echo_action(f"Installing postgresql ", "failed", True)

    cmd = f"{s['path']}/pgedge/pgedge install backrest"
    util.run_rcommand(
        cmd,
        f"Installing backrest",
        host=s["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )

    repo1_path = f"/var/lib/pgbackrest/{s['name']}"
    os_user = n["os_user"]
    repo1_type = n["repo1_type"] if "repo1_type" in n else "Posix"
    port = s["port"]
    pg1_path = f"{s['path']}/pgedge/data/{stanza}"

    args = (f'--repo1-path {repo1_path} --stanza {stanza} '
            f'--pg1-path {pg1_path} --repo1-type {repo1_type} --log-level-console info '
            f'--pg1-port {port} --db-socket-path /tmp --repo1-cipher-type aes-256-cbc' )

    cmd = f"{s['path']}/pgedge/pgedge backrest command stanza-create '{args}'"
    util.run_rcommand(
        cmd,
        f"Creating stanza {stanza}",
        host=s["ip_address"],
        usr=s["os_user"],
        key=s["ssh_key"],
        verbose=verbose
    )
    cmd = f"{s['path']}/pgedge/pgedge  backrest set_postgresqlconf {stanza} {pg1_path} {repo1_path} {repo1_type}"
    util.run_rcommand(
        cmd,
        f"Modifying postgresql.conf file",
        host=s["ip_address"],
        usr=s["os_user"],
        key=s["ssh_key"],
        verbose=verbose
    )
    cmd = f"{s['path']}/pgedge/pgedge backrest set_hbaconf"
    util.run_rcommand(
        cmd,
        f"Modifying pg_hba.conf file",
        host=s["ip_address"],
        usr=s["os_user"],
        key=s["ssh_key"],
        verbose=verbose
    )
    sql_cmd = "select pg_reload_conf()"
    cmd = f"{s['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    util.run_rcommand(
        cmd,
        f"Reload configuration pg_reload_conf()",
        host=s["ip_address"],
        usr=s["os_user"],
        key=s["ssh_key"],
        verbose=verbose
    )

    args= args + f' --repo1-retention-full=7 --type=full'
    if backup_id == " ":
        cmd = f"{s['path']}/pgedge/pgedge backrest command backup '{args}'"
        util.run_rcommand(
            cmd,
            f"Creating full backup",
            host=s["ip_address"],
            usr=n["os_user"],
            key=n["ssh_key"],
            verbose=verbose
        )

    cmd = f"{n['path']}/pgedge/pgedge install backrest"
    util.run_rcommand(
        cmd,
        f"Installing backrest",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )

    manage_node(n, "stop", verbose)
    cmd = f'rm -rf {n["path"]}/pgedge/data/{stanza}'
    util.run_rcommand(
        cmd,
        f"Removing old data directory",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
    args = (f'--repo1-path /var/lib/pgbackrest/{s["name"]} --repo1-cipher-type aes-256-cbc ')

    cmd1 = (f'{n["path"]}/pgedge/pgedge backrest command restore --repo1-type={repo1_type} '
            f'--stanza={stanza} --pg1-path={n["path"]}/pgedge/data/{stanza} {args}')
    util.run_rcommand(
        cmd1,
        f"Restoring backup on new node",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )


    pgd = f'{n["path"]}/pgedge/data/{stanza}'
    pgc = f'{pgd}/postgresql.conf'
    
    cmd = f'echo "ssl_cert_file=\'{pgd}/server.crt\'" >> {pgc}'
    util.run_rcommand(
        cmd,
        f"Setting ssl_cert_file",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )

    cmd = f'echo "ssl_key_file=\'{pgd}/server.key\'" >> {pgc}'
    util.run_rcommand(
        cmd,
        f"Setting ssl_key_file",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
    
    cmd = f'echo "log_directory=\'{pgd}/log\'" >> {pgc}'
    util.run_rcommand(
        cmd,
        f"Setting log_directory",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
    
    cmd = (f'echo "shared_preload_libraries = \'pg_stat_statements, snowflake, spock\'"'
           f'>> {pgc}')
    util.run_rcommand(
        cmd,
        f"Setting shared_preload_libraries",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
    cmd = (f'{n["path"]}/pgedge/pgedge backrest configure_replica {stanza} '
        f'{n["path"]}/pgedge/data/{stanza} {s["ip_address"]} {s["port"]} {s["os_user"]}')
    util.run_rcommand(
        cmd,
        f"Configuring PITR on replica",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
 
    manage_node(n, "start", verbose)
    time.sleep(5)

    if script != " ":
        if script.strip() and os.path.isfile(script):
          util.echo_cmd(f'{script}')

    check_cluster_lag(n, dbname, stanza, verbose)
    terminate_cluster_transactions(nodes, dbname, stanza, verbose)
    set_cluster_readonly(nodes, True, dbname, stanza, verbose)

    sql_cmd = "SELECT pg_promote()"
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    util.run_rcommand(
        cmd,
        f"Promoting standby to primary",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )

    sql_cmd = "DROP extension spock cascade"
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    util.run_rcommand(
        cmd,
        f"DROP extension spock cascade",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )

    cmd = (f'cd {n["path"]}/pgedge/;'
           f'./pgedge remove spock33-pg16 -d {dbname} --no-restart;'
           f'./pgedge install spock33-pg16 -d {dbname}')
    util.run_rcommand(
        cmd,
        f"Re-installing spock",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose
    )
   
    create_node(n, dbname, verbose)
    set_cluster_readonly(nodes, False, dbname, stanza, verbose)
    create_sub(nodes, n, dbname, verbose)
    create_sub_new(nodes, n, dbname, verbose)
    
    cmd = (f'cd {n["path"]}/pgedge/; ./pgedge spock node-list lcdb')
    result = util.run_rcommand(
        cmd,
        f"Listing spock nodes",
        host=n["ip_address"],
        usr=n["os_user"],
        key=n["ssh_key"],
        verbose=verbose,
        capture_output=True
    )
    print(result.stdout)

    if 'aws' in cluster_data['node_groups']:
        cluster_data['node_groups']['aws'].append(node_config)
    elif 'localhost' in cluster_data['node_groups']:
        cluster_data['node_groups']['localhost'].append(node_config)
    write_cluster_json(cluster_name, cluster_data)

def remove_node(cluster_name, node_name):
    """Remove node from cluster."""
    
    cluster_data = get_cluster_json(cluster_name)
    
    node_groups = cluster_data.get('node_groups', {})
    nodes = node_groups.get('aws', [])

    for node_group in nodes:
        nodes = node_group.get('nodes', [])
        for node in nodes:
            if node.get('name') == node_name:
                nodes.remove(node)
                break

    write_cluster_json(cluster_name, cluster_data)

def manage_node(node, action, verbose):
    """
    Starts or stops a cluster based on the provided action.
    """
    if action not in ['start', 'stop']:
        raise ValueError("Invalid action. Use 'start' or 'stop'.")

    action_message = "Starting" if action == 'start' else "Stopping"

    # Construct the command based on the action
    if action == 'start':
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge config pg16 --port={node['port']}; "
               f"./pgedge start;")
    else:
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge stop")

    util.run_rcommand(
        cmd,
        message=f"{action_message} new node",
        host=node["ip_address"],
        usr=node["os_user"],
        key=node["ssh_key"],
        verbose=verbose
    )

def create_node(node, dbname, verbose):
    """
    Creates a new node in the database cluster.
    """
    cmd = (f"cd {node['path']}/pgedge/; "
           f"./pgedge spock node-create {node['name']} "
           f"'host={node['ip_address']} user=pgedge dbname={dbname} "
           f"port={node['port']}' {dbname}")
    util.run_rcommand(
        cmd,
        message=f"Creating new node {node['name']}",
        host=node["ip_address"],
        usr=node["os_user"],
        key=node["ssh_key"],
        verbose=verbose
    )


def create_sub_new(nodes, n, dbname, verbose):
    """
    Creates subscriptions for each node to a new node in the cluster.
    """
    for node in nodes:
        sub_name = f"sub_{n['name']}{node['name']}"
        cmd = (f"cd {n['path']}/pgedge/; "
               f"./pgedge spock sub-create {sub_name} "
               f"'host={node['ip_address']} user=pgedge dbname={dbname} "
               f"port={node['port']}' {dbname}")
        util.run_rcommand(
            cmd,
            message="Creating new subscriptions",
            host=n["ip_address"],
            usr=n["os_user"],
            key=n["ssh_key"],
            verbose=verbose
        )

def create_sub(nodes, new_node, dbname, verbose):
    """
    Creates subscriptions for each node to a new node in the cluster.
    """
    for n in nodes:
        sub_name = f"sub_{n['name']}{new_node['name']}"

        cmd = (f"cd {n['path']}/pgedge/; "
               f"./pgedge spock sub-create {sub_name} "
               f"'host={new_node['ip_address']} user=pgedge dbname={dbname} "
               f"port={new_node['port']}' {dbname}")
        util.run_rcommand(
            cmd,
            message=f"Creating subscriptions {sub_name}",
            host=n["ip_address"],
            usr=n["os_user"],
            key=n["ssh_key"],
            verbose=verbose
        )

def terminate_cluster_transactions(nodes, dbname, stanza, verbose):
    sql_cmd = "SELECT spock.terminate_active_transactions()"
    for node in nodes:
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        util.run_rcommand(
            cmd,
            f"Terminating·cluster·transactions on {node['name']}",
            host=node["ip_address"],
            usr=node["os_user"],
            key=node["ssh_key"],
            verbose=verbose
        )

def extract_psql_value(psql_output: str, alias: str) -> str:
    lines = psql_output.split('\n')
    if len(lines) < 3:
        return ""
    header_line = lines[0]
    headers = [header.strip() for header in header_line.split('|')]

    alias_index = -1
    for i, header in enumerate(headers):
        if header == alias:
            alias_index = i
            break

    if alias_index == -1:
        return ""

    for line in lines[2:]:
        if line.strip() == "":
            continue
        columns = [column.strip() for column in line.split('|')]
        if len(columns) > alias_index:
            return columns[alias_index]

    return ""


def set_cluster_readonly(nodes, readonly, dbname, stanza, verbose):
    action = "Setting" if readonly else "Removing"
    func_call = ("spock.set_cluster_readonly()" if readonly
                 else "spock.unset_cluster_readonly()")

    sql_cmd = f"SELECT {func_call}"

    for node in nodes:
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        util.run_rcommand(
            cmd,
            f"{action} readonly mode from cluster",
            host=node["ip_address"],
            usr=node["os_user"],
            key=node["ssh_key"],
            verbose=verbose
        )

def check_cluster_lag(n, dbname, stanza, verbose, timeout=600, interval=1):
    sql_cmd = """
    SELECT COALESCE(
    (SELECT pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn())),
    0
    ) AS lag_bytes
    """

    start_time = time.time()
    lag_bytes = 1

    while lag_bytes > 0:
        if time.time() - start_time > timeout:
            return

        cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        result = util.run_rcommand(
            cmd,
            f"Checking lag time of new cluster",
            host=n["ip_address"],
            usr=n["os_user"],
            key=n["ssh_key"],
            verbose=verbose,
            capture_output=True
        )
        print(result.stdout)
        lag_bytes = int(extract_psql_value(result.stdout, "lag_bytes"))

def check_wal_rec(n, dbname, stanza, verbose, timeout=600, interval=1):
    sql_cmd = """
    SELECT
        COALESCE(SUM(CASE
            WHEN pub.confirmed_flush_lsn <= sub.latest_end_lsn THEN 1
            ELSE 0
        END), 0) AS total_all_flushed
    FROM
        pg_stat_subscription AS sub
    JOIN
        pg_replication_slots AS pub ON sub.subname = pub.slot_name
    WHERE
        pub.slot_name IS NOT NULL
    """

    lag_bytes = 1
    start_time = time.time()

    while lag_bytes > 0:
        if time.time() - start_time > timeout:
            return

        cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        result, output, error = util.run_rcommand(
            cmd,
            "Checking wal receiver",
            host=n["ip_address"],
            usr=n["os_user"],
            key=n["ssh_key"],
            verbose=verbose,
            capture_output=True
        )

        time.sleep(interval)
        lag_bytes = int(extract_psql_value(result.stdout, "total_all_flushed"))

if __name__ == "__main__":
    fire.Fire(
        {
            "json-template": create_remote_json,
            "json-validate": validate,
            "init": init,
            "list-nodes": list_nodes,
            "add-node": add_node,
            "remove-node": remove_node,
            "replication-begin": replication_all_tables,
            "replication-check": replication_check,
            "add-db": add_db,
            "remove": remove,
            "command": command,
            "set-firewalld": set_firewalld,
            "ssh": ssh,
            "app-install": app_install,
            "app-remove": app_remove
        }
    )
