import os, json, datetime
import util, fire, meta, time, sys
try:
    import etcd, patroni
except ImportError:
    pass

BASE_DIR = "cluster"

def run_cmd(cmd, node, message, verbose, capture_output=False, ignore=False,
            important=False):
    name = node["name"]
    msg = name + " - " + message
    return util.run_rcommand(
        cmd=cmd,
        message=msg,
        host=node["ip_address"],
        usr=node["os_user"],
        key=node["ssh_key"],
        verbose=verbose,
        capture_output=capture_output,
        ignore=ignore,
        important=important
    )

def ssh(cluster_name, node_name):
    """An SSH Terminal session into the specified node"""
    db, db_settings, nodes = load_json(cluster_name)

    for nd in nodes:
        if node_name == nd["name"]:
            util.echo_cmd(
                f'ssh -i {nd["ssh_key"]} {nd["os_user"]}@{nd["ip_address"]}')
            util.exit_cleanly(0)

    util.exit_message(f"Could not locate node '{node_name}'")

def get_connection_info(cluster_name):
    cluster_dir = os.path.join(util.MY_HOME, BASE_DIR, cluster_name)
    os.system("mkdir -p " + cluster_dir)
    cluster_file = os.path.join(cluster_dir, "connection.json")
    return (cluster_dir, cluster_file)

def get_connection_json(cluster_name):
    cluster_dir, cluster_file = get_connection_info(cluster_name)

    if not os.path.isdir(cluster_dir):
        util.exit_message(f"Cluster directory '{cluster_dir}' not found")

    if not os.path.isfile(cluster_file):
        util.message(f"Cluster connection file '{cluster_file}' not found", "warning")
        return None

    try:
        with open(cluster_file, "r") as f:
            return json.load(f)
    except Exception as e:
        util.exit_message(
            f"Unable to load cluster connection def file '{cluster_file}'\n{e}")

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

    try:
        with open(cluster_file, "r") as f:
            return json.load(f)
    except Exception as e:
        util.exit_message(
            f"Unable to load cluster def file '{cluster_file}\n{e}")

def write_cluster_json(cluster_name, cj):
    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    try:
        cjs = json.dumps(cj, indent=2)
        util.message(f"write_cluster_json {cluster_name}, {cluster_dir}, "
                     f"{cluster_file},\n{cjs}", "debug")
        with open(cluster_file, "w") as f:
            f.write(cjs)
    except Exception as e:
        util.exit_message(
            f"Unable to write_cluster_json {cluster_file}\n{str(e)}")

def json_create(cluster_name, style, db="demo", user="user1", passwd="passwd1",
                pg="16", os_user=None, ssh_key=None):
    cluster_json = {
        "json_version": 1,
        "name": cluster_name,
        "pg_version": pg,
        "log_level": "none",
        "create_date": datetime.datetime.now().isoformat(),
        "spock": {
            "spock_version": "",
            "auto_ddl": "off",
            "auto_start": "off"
        },
        "node_groups": {},
        "database": {
            "databases": [
                {
                    "name": db,
                    "username": user,
                    "password": passwd
                }
            ]
        }
    }

    write_cluster_json(cluster_name, cluster_json)

def json_add_node(cluster_name, node_group, node_name, is_active, ip_address, 
                  port, path, os_user=None, ssh_key=None, provider=None, 
                  airport=None):
    cj = get_cluster_json(cluster_name)
    if cj is None:
        util.exit_message("Unable to load cluster JSON")

    node_json = {
        "name": node_name,
        "is_active": is_active,
        "ip_address": ip_address,
        "port": port,
        "path": path,
        "os_user": os_user,
        "ssh_key": ssh_key,
        "provider": provider,
        "airport": airport
    }

    nodes = {"nodes": [node_json]}
    lhn = cj["node_groups"]
    if node_group not in lhn:
        lhn[node_group] = []
    lhn[node_group].append(nodes)

    write_cluster_json(cluster_name, cj)

def json_template(cluster_name, db, num_nodes, usr, passwd, pg, port):
    """Create a template for a Cluster Configuration JSON file."""
    cluster_dir, cluster_file = get_cluster_info(cluster_name)
    os.system("mkdir -p " + cluster_dir)

    demo_json = {
        "json_version": 1,
        "name": cluster_name,
        "pg_version": pg,
        "log_level": "none",
        "create_date": datetime.datetime.now().isoformat(),
        "spock": {
            "spock_version": "",
            "auto_ddl": "off",
            "auto_start": "off"
        },
        "database": {
            "databases": [
                {
                    "name": db,
                    "username": usr,
                    "password": passwd
                }
            ]
        },
        "node_groups": {}
    }

    connection_json = {
        "pg": {
            "connection_profiles": {},
        },
        "ssh": {
            "connection_profiles": {},
        }
    }

    for n in range(1, num_nodes + 1):
        conn_name = f"conn{n}"
        node_name = f"n{n}"

        demo_json["node_groups"][conn_name] = [{
            "nodes": [{
                "name": node_name,
                "is_active": True,
                "ip_address": "",
                "port": port,
                "path": f"/path/to/{node_name}"
            }]
        }]

        connection_json["pg"]["connection_profiles"][conn_name] = {
            "host": "127.0.0.1",
            "port": port
        }

        connection_json["ssh"]["connection_profiles"][conn_name] = {
            "user": usr,
            "private_key": "/path/to/private/key"
        }

    try:
        with open(os.path.join(cluster_dir, f"{cluster_name}.json"), "w") as text_file:
            text_file.write(json.dumps(demo_json, indent=2))

        with open(os.path.join(cluster_dir, "connection.json"), "w") as text_file:
            text_file.write(json.dumps(connection_json, indent=2))
    except Exception:
        util.exit_message("Unable to create JSON files", 1)

def load_json(cluster_name):
    """Load a JSON config file for a cluster."""
    parsed_json = get_cluster_json(cluster_name)
    if parsed_json is None:
        util.exit_message("Unable to load cluster JSON")

    if parsed_json.get("json_version", 0) < 1:
        util.exit_message("Invalid or missing json_version")

    db_settings = {
        "pg_version": parsed_json["pg_version"],
        "spock_version": parsed_json["spock"].get("spock_version", ""),
        "auto_ddl": parsed_json["spock"].get("auto_ddl", "off"),
        "auto_start": parsed_json["spock"].get("auto_start", "on")
    }

    demo_data = parsed_json
    connection_data = get_connection_json(cluster_name)

    nodes = []
    db = []

    def process_nodes(group, conn_name):
        for n in group["nodes"]:
            node = {
                "name": n["name"],
                "is_active": n["is_active"],
                "ip_address": n["ip_address"],
                "port": n["port"],
                "path": n["path"]
            }
            if conn_name in connection_data["ssh"]["connection_profiles"]:
                ssh_conn = connection_data["ssh"]["connection_profiles"][conn_name]
                node["os_user"] = ssh_conn["user"]
                node["ssh_key"] = ssh_conn["private_key"]
            else:
                util.exit_message(f"{conn_name} SSH connection info missing from connection.json")
            nodes.append(node)

    def process_db():
        if "databases" in demo_data:
            for database in demo_data["databases"]:
                db.append({
                    "name": database["name"],
                    "username": database["username"],
                    "password": database["password"],
                    "host": connection_data["pg"]["connection_profiles"]["conn1"]["host"],
                    "port": connection_data["pg"]["connection_profiles"]["conn1"]["port"]
                })
        else:
            util.exit_message("Database info missing from cluster.json")

    if "node_groups" in parsed_json:
        for conn_name, groups in parsed_json["node_groups"].items():
            for group in groups:
                process_nodes(group, conn_name)
        process_db()
    else:
        util.exit_message("node_groups info missing from JSON", 1)

    return db, db_settings, nodes

def json_validate(cluster_name):
    """Validate a Cluster Configuration JSON file"""
    parsed_json = get_cluster_json(cluster_name)

    if "name" not in parsed_json:
        util.exit_message("Cluster name missing")

    if "pg_version" not in parsed_json:
        util.exit_message("pg_version is missing")

    if "node_groups" not in parsed_json:
        util.exit_message("Node Group section missing")

    db, db_settings, nodes = load_json(cluster_name)
    util.message(f"JSON defines a {len(nodes)} node cluster", 'success')

def remove(cluster_name, force=False):
    """Remove a test cluster.
    
       Remove a cluster. This will remove spock subscriptions and nodes, and
       then stop postgres on each node. If the flag force is set to true, 
       then it will also remove the pgedge directory on each node.
       This command requires a JSON file with the same name as the cluster to
       be in the cluster/<cluster_name>. 
       
       Example: cluster remove demo 
       :param cluster_name: The name of the cluster. 
    """
    db, db_settings, nodes = load_json(cluster_name)

    ssh_un_cross_wire(
        cluster_name, db[0]["name"], db_settings, db[0]["username"],
        db[0]["password"], nodes
    )

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = f"{nd['path']}{os.sep}pgedge stop 2> {os.sep}dev{os.sep}null"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])

    if force:
        util.message("\n## Ensure that pgEdge root directory is gone")
        for nd in nodes:
            cmd = f"rm -rf {nd['path']}{os.sep}pgedge"
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
   
    verbose = parsed_json.get("log_level", "none")

    for nd in nodes:
        message = f"Checking ssh on {nd['ip_address']}"
        run_cmd(cmd="hostname", node=nd, message=message, verbose=verbose)

    ssh_install_pgedge(
        cluster_name, db[0]["name"], db_settings, db[0]["username"],
        db[0]["password"], nodes, True, " ", verbose
    )
    ssh_cross_wire_pgedge(
        cluster_name, db[0]["name"], db_settings, db[0]["username"],
        db[0]["password"], nodes, verbose
    )

    if len(db) > 1:
        for database in db[1:]:
            create_spock_db(nodes, database, db_settings)
            ssh_cross_wire_pgedge(
                cluster_name, database["name"], db_settings, database["username"],
                database["password"], nodes, verbose
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
    pg = db_settings["pg_version"]
    if db_settings.get("log_level"):
        verbose = db_settings["log_level"]
    else:
        verbose = "none"

    db_json = {}
    db_json["username"] = username
    db_json["password"] = password
    db_json["name"] = database_name

    util.message(f"## Creating database {database_name}")
    create_spock_db(nodes, db_json, db_settings)
    ssh_cross_wire_pgedge(cluster_name, database_name, db_settings, username, password, nodes, verbose)
    util.message(f"## Updating cluster '{cluster_name}' json definition file")
    update_json(cluster_name, db_json)

def print_install_hdr(cluster_name, db, db_user, count, name, path, ip, port,
                      repo, primary, primary_name):
    
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

def ssh_install(cluster_name, db, db_settings, db_user, db_passwd, n, primary, primary_name, num_nodes):
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
    
    verbose = db_settings.get("log_level", "none")
        
    print_install_hdr(cluster_name, db, db_user, num_nodes, n["name"],
                          n["path"], n["ip_address"], n["port"], REPO, primary,
                          primary_name)

    install_py = "install.py"
    spock = db_settings["spock_version"]

    cmd0 = f"export REPO={REPO}; "
    cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
    cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
   
    message = f"Installing pgedge"
    run_cmd(cmd0 + cmd1 + cmd2, n, message=message, verbose=verbose)

    nc = os.path.join(ndpath, "pgedge", "pgedge ")
    parms = f" -U {db_user} -P {db_passwd} -d {db} --port {ndport}"
    if pg is not None and pg != '':
        parms = parms + f" --pg {pg}"
    if spock is not None and spock != '':
        parms = parms + f" --spock_ver {spock}"
    if db_settings["auto_start"] == "on":
        parms = f"{parms} --autostart"
    
    cmd = f"{nc} setup {parms}"
    message = f"Setup pgedge"
    run_cmd(cmd, n, message=message, verbose=verbose)
        
    if db_settings["auto_ddl"] == "on":
        cmd = nc + " db guc-set spock.enable_ddl_replication on;"
        cmd = cmd + " " + nc + " db guc-set spock.include_ddl_repset on;"
        cmd = cmd + " " + nc + " db guc-set spock.allow_ddl_from_functions on;"
        
        message = f"Setup spock"
        run_cmd(cmd, n, message=message, verbose=verbose)
        
        if db_settings["auto_ddl"] == "on":
            util.message("#")
    return 0


def ssh_install_pgedge(cluster_name, db, db_settings, db_user, db_passwd, nodes, primary, primary_name, verbose):
    count = len(nodes)
    pg = db_settings["pg_version"]
    spock = db_settings["spock_version"]

    for n in nodes:
        ssh_install(cluster_name, db, db_settings, db_user, db_passwd, n, primary, primary_name, len(nodes))


def ssh_cross_wire_pgedge(cluster_name, db, db_settings, db_user, db_passwd, nodes, verbose):
    """Create nodes and subs on every node in a cluster."""

    sub_array = []
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
        
        message = f"Creating node {ndnm}"
        run_cmd(cmd1, prov_n, message=message, verbose=verbose)
        
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
                sub_name = f"sub_{ndnm}{sub_ndnm}"
                cmd = f"{nc} spock sub-create sub_{ndnm}{sub_ndnm} 'host={sub_ndip_private} user={os_user} dbname={db} port={sub_ndport}' {db}"
                sub_array.append([cmd, ndip, os_user, ssh_key, prov_n, sub_name])
    for n in sub_array:
        cmd = n[0]
        node = n[4]
        sub_name = n[5]
        message = f"Creating subscriptions {sub_name}"
        run_cmd(cmd, node, message=message, verbose=verbose)
    
    cmd = f'{nc} spock node-list {db}'
    message = f"Listing spock nodes"
    result = run_cmd(cmd, prov_n, message=message, verbose=verbose, capture_output=True)
    print(f"\n{result.stdout}")

def ssh_un_cross_wire(cluster_name, db, db_settings, db_user, db_passwd,
                      nodes):
    """
    Remove a cluster's spock connections.
    """
    pg = db_settings["pg_version"]
    spock = db_settings["spock_version"]
    for n in nodes:
        for m in nodes:
            if m["name"] == n["name"]:
                continue
            util.message(f"Dropping spock subscription from {n['name']} "
                         f"to {m['name']}")
            nc = os.path.join(n["path"], "pgedge", "pgedge")
            cmd = f"{nc} spock sub-drop --subname={m['name']} --subdb={db}"
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"],
                          key=n["ssh_key"])

    for n in nodes:
        nc = os.path.join(n["path"], "pgedge", "pgedge")
        cmd = f"{nc} db unconfig --pguser={db_user} --pgdb={db}"

        util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"],
                      key=n["ssh_key"])

def create_spock_db(nodes, db, db_settings):
    for n in nodes:
        nc = os.path.join(n["path"], "pgedge", "pgedge")
        cmd = f"{nc} db create -U {db['username']} -d {db['name']} -p {db['password']}"
        util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])

        if db_settings["auto_ddl"] == "on":
            cmd = (
                f"{nc} db guc-set spock.enable_ddl_replication on;"
                f" {nc} db guc-set spock.include_ddl_repset on;"
                f" {nc} db guc-set spock.allow_ddl_from_functions on;"
            )
            util.echo_cmd(cmd, host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"])

def add_node(cluster_name, source_node, target_node, repo1_path=None, backup_id=None, script=" ", stanza=" "):
    """
    Adds a new node to a cluster, copying configurations from a specified 
    source node.

    Args:
        cluster_name (str): The name of the cluster to which the node is being 
                            added.
        source_node (str): The node from which configurations are copied.
        target_node (str): The new node being added.
        repo1_path (str): The repo1 path to use.
        backup_id (str): Backup ID.
        stanza (str): Stanza name.
        script (str): Bash script.
    """
    if (repo1_path and not backup_id) or (backup_id and not repo1_path):
        util.exit_message("Both repo1_path and backup_id must be supplied together.")

    cluster_data = get_cluster_json(cluster_name)
    parsed_json = get_cluster_json(cluster_name)
    if "json_version" not in parsed_json or parsed_json["json_version"] <= 0:
        util.exit_message("Invalid or missing JSON version.")

    pg = parsed_json.get("pg_version", None)
    if pg is None:
        util.exit_message("pg_version missing from JSON.")
    
    stanza_create = False
    if stanza == " ":
        stanza = f"pg{pg}"
    pgV = f"pg{pg}"

    verbose = parsed_json.get("log_level", "none")

    node_file = f"{target_node}.json"
    if not os.path.exists(node_file):
        util.exit_message(f"Missing node configuration file '{node_file}'.")
        return

    with open(node_file, 'r') as file:
        try:
            data = json.load(file)
            validate_json(data)
        except json.JSONDecodeError as e:
            util.exit_message(f"Invalid JSON: {e}")

    node_groups = list(data.get("node_groups", {}).keys())
    node_config = None
    node_group_name = None
    node_data = None
    for group in node_groups:
        group_config = data["node_groups"][group]
        for config in group_config:
            node_data = config['nodes']
            for node in node_data:
                if node['name'] == target_node:
                    node_config = node
                    node_group_name = group
                    break
            if node_config:
                break
        if node_config:
            break

    if not node_config:
        util.exit_message(f"Target node '{target_node}' not found in node groups.")
        return

    target_json = group_config[0]
    n = node_data[0]

    db, db_settings, nodes = load_json(cluster_name)
    s = next((node for node in nodes if node['name'] == source_node), None)
    if s is None:
        util.exit_message(f"Source node '{source_node}' not found in cluster data.")
        return

    for node in nodes:
        if node.get('name') == n['name']:
            util.exit_message(f"Node {n['name']} already exists.")
            break

    dbname = db[0]["name"]
    n.update({
        'os_user': s['os_user'],
        'ssh_key': s['ssh_key'],
    })
    util.echo_message(f"Installing and Configuring new node\n", bold=True)
    rc = ssh_install_pgedge(cluster_name, dbname, db_settings, db[0]["username"],
                            db[0]["password"], node_data, True, " ", verbose)

    os_user = n["os_user"]
    repo1_type = n.get("repo1_type", "posix")
    port = s["port"]
    pg1_path = f"{s['path']}/pgedge/data/{stanza}"
    
    if not repo1_path:
        cmd = f"{s['path']}/pgedge/pgedge install backrest"
        message = f"Installing backrest"
        run_cmd(cmd, s, message=message, verbose=verbose)

        repo1_path = f"/var/lib/pgbackrest/{s['name']}"
        cmd = f"sudo rm -rf {repo1_path}"
        message = f"Removing the repo-path"
        run_cmd(cmd, s, message=message, verbose=verbose)

        args = (f'--repo1-path {repo1_path} --stanza {stanza} '
                f'--pg1-path {pg1_path} --repo1-type {repo1_type} '
                f'--log-level-console info --pg1-port {port} '
                f'--db-socket-path /tmp --repo1-cipher-type aes-256-cbc')

        cmd = f"{s['path']}/pgedge/pgedge backrest command stanza-create '{args}'"
        message = f"Creating stanza {stanza}"
        run_cmd(cmd, s, message=message, verbose=verbose)

        cmd = (f"{s['path']}/pgedge/pgedge backrest set_postgresqlconf {stanza} "
               f"{pg1_path} {repo1_path} {repo1_type}")
        message = f"Modifying postgresql.conf file"
        run_cmd(cmd, s, message=message, verbose=verbose)

        cmd = f"{s['path']}/pgedge/pgedge backrest set_hbaconf"
        message = f"Modifying pg_hba.conf file"
        run_cmd(cmd, s, message=message, verbose=verbose)

        sql_cmd = "select pg_reload_conf()"
        cmd = f"{s['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"Reload configuration pg_reload_conf()"
        run_cmd(cmd, s, message=message, verbose=verbose)

        args = args + f' --repo1-retention-full=7 --type=full'
        cmd = f"{s['path']}/pgedge/pgedge backrest command backup '{args}'"
        message = f"Creating full backup"
        run_cmd(cmd, s, message=message, verbose=verbose)
    else:
        cmd = (f"{s['path']}/pgedge/pgedge backrest set_postgresqlconf {stanza} "
               f"{pg1_path} {repo1_path} {repo1_type}")
        message = f"Modifying postgresql.conf file"
        run_cmd(cmd, s, message=message, verbose=verbose)

        cmd = f"{s['path']}/pgedge/pgedge backrest set_hbaconf"
        message = f"Modifying pg_hba.conf file"
        run_cmd(cmd, s, message=message, verbose=verbose)

        sql_cmd = "select pg_reload_conf()"
        cmd = f"{s['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"Reload configuration pg_reload_conf()"
        run_cmd(cmd, s, message=message, verbose=verbose)

        repo1_type = n.get("repo1_type", "posix")
        if repo1_type == "s3":
            for env_var in ["PGBACKREST_REPO1_S3_KEY", "PGBACKREST_REPO1_S3_BUCKET", 
                            "PGBACKREST_REPO1_S3_KEY_SECRET", "PGBACKREST_REPO1_CIPHER_PASS"]:
                if env_var not in os.environ:
                    util.exit_message(f"Environment variable {env_var} not set.")
            s3_export_cmds = [f'export {env_var}={os.environ[env_var]}' for env_var in [
                "PGBACKREST_REPO1_S3_KEY", "PGBACKREST_REPO1_S3_BUCKET", 
                "PGBACKREST_REPO1_S3_KEY_SECRET", "PGBACKREST_REPO1_CIPHER_PASS"]]
            run_cmd(" && ".join(s3_export_cmds), s, message="Setting S3 environment variables on source node", verbose=verbose)
            run_cmd(" && ".join(s3_export_cmds), n, message="Setting S3 environment variables on target node", verbose=verbose)

    cmd = f"{n['path']}/pgedge/pgedge install backrest"
    message = f"Installing backrest"
    run_cmd(cmd, n, message=message, verbose=verbose)

    manage_node(n, "stop", pgV, verbose)
    cmd = f'rm -rf {n["path"]}/pgedge/data/{stanza}'
    message = f"Removing old data directory"
    run_cmd(cmd, n, message=message, verbose=verbose)

    args = (f'--repo1-path {repo1_path} --repo1-cipher-type aes-256-cbc ')

    if backup_id:
        args += f'--set={backup_id} '

    cmd = (f'{n["path"]}/pgedge/pgedge backrest command restore '
           f'--repo1-type={repo1_type} --stanza={stanza} '
           f'--pg1-path={n["path"]}/pgedge/data/{stanza} {args}')

    message = f"Restoring backup"
    run_cmd(cmd, n, message=message, verbose=verbose)

    pgd = f'{n["path"]}/pgedge/data/{stanza}'
    pgc = f'{pgd}/postgresql.conf'

    cmd = f'echo "ssl_cert_file=\'{pgd}/server.crt\'" >> {pgc}'
    message = f"Setting ssl_cert_file"
    run_cmd(cmd, n, message=message, verbose=verbose)

    message = f"Setting ssl_key_file"
    cmd = f'echo "ssl_key_file=\'{pgd}/server.key\'" >> {pgc}'
    run_cmd(cmd, n, message=message, verbose=verbose)

    cmd = f'echo "log_directory=\'{pgd}/log\'" >> {pgc}'
    message = f"Setting log_directory"
    run_cmd(cmd, n, message=message, verbose=verbose)

    cmd = (f'echo "shared_preload_libraries = '
           f'\'pg_stat_statements, snowflake, spock\'" >> {pgc}')
    message = f"Setting shared_preload_libraries"
    run_cmd(cmd, n, message=message, verbose=verbose)

    cmd = (f'{n["path"]}/pgedge/pgedge backrest configure_replica {stanza} '
           f'{n["path"]}/pgedge/data/{stanza} {s["ip_address"]} '
           f'{s["port"]} {s["os_user"]}')
    message = f"Configuring PITR on replica"
    run_cmd(cmd, n, message=message, verbose=verbose)

    if script.strip() and os.path.isfile(script):
        util.echo_cmd(f'{script}')

    terminate_cluster_transactions(nodes, dbname, stanza, verbose)

    spock = db_settings["spock_version"]
    v4 = False
    spock_maj = 3
    if spock:
        ver = [int(x) for x in spock.split('.')]
        spock_maj = ver[0]
        spock_min = ver[1]
        if spock_maj >= 4:
            v4 = True

    set_cluster_readonly(nodes, True, dbname, stanza, v4, verbose)
    manage_node(n, "start", pgV, verbose)
    time.sleep(5)

    check_cluster_lag(n, dbname, stanza, verbose)

    sql_cmd = "SELECT pg_promote()"
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    message = f"Promoting standby to primary"
    run_cmd(cmd, n, message=message, verbose=verbose)

    sql_cmd = "DROP extension spock cascade"
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    message = f"DROP extension spock cascade"
    run_cmd(cmd, n, message=message, verbose=verbose)

    parms = f"spock{spock_maj}{spock_min}" if spock else "spock"

    cmd = (f'cd {n["path"]}/pgedge/; ./pgedge install {parms}')
    message = f"Re-installing spock"
    run_cmd(cmd, n, message=message, verbose=verbose)

    sql_cmd = "CREATE EXTENSION spock"
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    message = f"Create extension spock"
    run_cmd(cmd, n, message=message, verbose=verbose)

    create_node(n, dbname, verbose)

    if not v4:
        set_cluster_readonly(nodes, False, dbname, stanza, v4, verbose)

    create_sub(nodes, n, dbname, verbose)
    create_sub_new(nodes, n, dbname, verbose)

    if v4:
        set_cluster_readonly(nodes, False, dbname, stanza, v4, verbose)

    cmd = (f'cd {n["path"]}/pgedge/; ./pgedge spock node-list {dbname}')
    message = f"Listing spock nodes"
    result = run_cmd(cmd, node=n, message=message, verbose=verbose,
                     capture_output=True)
    print(f"\n{result.stdout}")

    sql_cmd = "select node_id,node_name from spock.node"
    cmd = f"{s['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    message = f"List nodes"
    result = run_cmd(cmd, node=s, message=message, verbose=verbose,
                     capture_output=True)
    print(f"\n{result.stdout}")

    for node in nodes:
        sql_cmd = ("select sub_id,sub_name,sub_enabled,sub_slot_name,"
                   "sub_replication_sets from spock.subscription")
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"List subscriptions"
        result = run_cmd(cmd, node=node, message=message, verbose=verbose,
                         capture_output=True)
        print(f"\n{result.stdout}")

    sql_cmd = ("select sub_id,sub_name,sub_enabled,sub_slot_name,"
               "sub_replication_sets from spock.subscription")
    cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
    message = f"List subscriptions"
    result = run_cmd(cmd, node=n, message=message, verbose=verbose,
                     capture_output=True)
    print(f"\n{result.stdout}")

    for node in target_json['nodes']:
        node.pop('repo1_type', None)
        node.pop('os_user', None)
        node.pop('ssh_key', None)

    if node_group_name not in cluster_data["node_groups"]:
        cluster_data["node_groups"][node_group_name] = []
    cluster_data["node_groups"][node_group_name].append(target_json)

    # Ensure the connection group exists in the main JSON
    if node_group_name not in cluster_data:
        cluster_data[node_group_name] = {
            "os_user": data["conn1"]["os_user"],
            "ssh_key": data["conn1"]["ssh_key"]
        }

    write_cluster_json(cluster_name, cluster_data)

def validate_json(data):
    """Validate the structure of a node configuration JSON file."""
    required_keys = ["node_groups"]
    node_keys = ["name", "is_active", "ip_address", "port", "path"]

    for key in required_keys:
        if key not in data:
            util.exit_message(f"Key '{key}' missing from JSON data.")

    for group_name, group_data in data["node_groups"].items():
        for group in group_data:
            if "nodes" not in group:
                util.exit_message(f"Key 'nodes' missing from node group '{group_name}'.")
            for node in group["nodes"]:
                for node_key in node_keys:
                    if node_key not in node:
                        util.exit_message(f"Key '{node_key}' missing from node in group '{group_name}'.")

def remove_node(cluster_name, node_name):
    """
    Remove node from cluster.
    """
    cluster_data = get_cluster_json(cluster_name)
    if cluster_data is None:
        util.exit_message("Cluster data is missing.")
    parsed_json = get_cluster_json(cluster_name)
    if "json_version" not in parsed_json or parsed_json["json_version"] <= 0:
        util.exit_message("Invalid or missing JSON version.")

    pg = parsed_json.get("pg_version", None)
    if pg is None:
        util.exit_message("pg_version missing from JSON.")
    
    pgV = f"pg{pg}"

    if "json_version" not in cluster_data or cluster_data["json_version"] <= 0:
        util.exit_message("Invalid or missing JSON version.")
 
    db, db_settings, nodes = load_json(cluster_name)
    dbname = db[0]["name"]
    verbose = cluster_data.get("log_level", "none")

    for node in nodes:
        os_user = node["os_user"]
        ssh_key = node["ssh_key"]
        message = f"Checking ssh on {node['ip_address']}"
        cmd = "hostname"
        run_cmd(cmd, node, message=message, verbose=verbose)

    for node in nodes:
        if node.get('name') != node_name:
            sub_name = f"sub_{node['name']}{node_name}"
            cmd = (f"cd {node['path']}/pgedge/; "
                   f"./pgedge spock sub-drop {sub_name} {dbname}")
            message = f"Dropping subscriptions {sub_name}"
            run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)

    sub_names = []
    for node in nodes:
        if node.get('name') != node_name:
            sub_name = f"sub_{node_name}{node['name']}"
            sub_names.append(sub_name)

    for node in nodes:
        if node.get('name') == node_name:
            for sub_name in sub_names:
                cmd = (f"cd {node['path']}/pgedge/; "
                       f"./pgedge spock sub-drop {sub_name} {dbname}")
                message = f"Dropping subscription {sub_name}"
                run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)
            
            cmd = (f"cd {node['path']}/pgedge/; "
                   f"./pgedge spock node-drop {node['name']} {dbname}")
            message = f"Dropping node {node['name']}"
            run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)

    for node in nodes:
        if node.get('name') == node_name:
            manage_node(node, "stop", pgV, verbose)
        else:
            cmd = (f'cd {node["path"]}/pgedge/; ./pgedge spock node-list {dbname}')
            message = f"Listing spock nodes"
            result = run_cmd(cmd, node=node, message=message, verbose=verbose,
                         capture_output=True)
        print(f"\n{result.stdout}")

    empty_groups = []
    for group, group_data in cluster_data["node_groups"].items():
        for config in group_data:
            config["nodes"] = [n for n in config["nodes"] if n["name"] != node_name]
        cluster_data["node_groups"][group] = [g for g in group_data if g["nodes"]]
        if not cluster_data["node_groups"][group]:
            empty_groups.append(group)

    # Remove empty connection groups
    for group in empty_groups:
        if group in cluster_data["node_groups"]:
            del cluster_data["node_groups"][group]

    write_cluster_json(cluster_name, cluster_data)

def manage_node(node, action, pgV, verbose):
    """
    Starts or stops a cluster based on the provided action.
    """
    if action not in ['start', 'stop']:
        raise ValueError("Invalid action. Use 'start' or 'stop'.")

    action_message = "Starting" if action == 'start' else "Stopping"

    if action == 'start':
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge config {pgV} --port={node['port']}; "
               f"./pgedge start;")
    else:
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge stop")

    message=f"{action_message} node"
    run_cmd(cmd, node, message=message, verbose=verbose)

def create_node(node, dbname, verbose):
    """
    Creates a new node in the database cluster.
    """
    cmd = (f"cd {node['path']}/pgedge/; "
           f"./pgedge spock node-create {node['name']} "
           f"'host={node['ip_address']} user=pgedge dbname={dbname} "
           f"port={node['port']}' {dbname}")
    message=f"Creating new node {node['name']}"
    run_cmd(cmd, node, message=message, verbose=verbose)

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
        message=f"Creating new subscriptions {sub_name}"
        run_cmd(cmd = cmd, node=n, message=message, verbose=verbose)

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
        message=f"Creating subscriptions {sub_name}"
        run_cmd(cmd = cmd, node=n, message=message, verbose=verbose)

def terminate_cluster_transactions(nodes, dbname, stanza, verbose):
    sql_cmd = "SELECT spock.terminate_active_transactions()"
    for node in nodes:
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"Terminating cluster transactions"
        result = run_cmd(cmd = cmd, node=node, message=message, verbose=verbose, capture_output=True)

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

def set_cluster_readonly(nodes, readonly, dbname, stanza, v4, verbose):
    action = "Setting" if readonly else "Removing"
    
    if v4:
        sql_cmd = ('ALTER SYSTEM SET spock.readonly TO \\\\"all\\\\"' if readonly
                   else 'ALTER SYSTEM SET spock.readonly TO \\\\"off\\\\"') 
        for node in nodes:
            cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
            message = f"{action} readonly mode from cluster"
            run_cmd(cmd, node=node, message=message, verbose=verbose, important=True)

        sql_cmd = "select pg_reload_conf()"
        for node in nodes:
            cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
            message = f"Reload configuration pg_reload_conf()"
            run_cmd(cmd, node=node, message=message, verbose=verbose, important=False)
    else:
        func_call = ("spock.set_cluster_readonly()" if readonly
                     else "spock.unset_cluster_readonly()")

        sql_cmd = f"SELECT {func_call}"

        for node in nodes:
            cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
            message = f"{action} readonly mode from cluster"
            run_cmd(cmd, node=node, message=message, verbose=verbose, important=True)

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
        message = f"Checking lag time of new cluster"
        result = run_cmd(cmd = cmd, node=n, message=message, verbose=verbose, capture_output=True)
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
        message = "Checking wal receiver"
        result = run_cmd(cmd = cmd, node=n, message=message, verbose=verbose, capture_output=True)
        time.sleep(interval)
        lag_bytes = int(extract_psql_value(result.stdout, "total_all_flushed"))

def list_nodes(cluster_name):
    """List all nodes in the cluster."""
    db, db_settings, nodes = load_json(cluster_name)
    dbname = db[0]["name"]
    verbose = db_settings.get("log_level", "none")
    for n in nodes:
        ndpath = n["path"]
        cmd = f'{ndpath}/pgedge/pgedge spock node-list {dbname}'
        ndip = n["ip_address"]
        result = run_cmd(cmd, n, f"Listing nodes for {n['name']}", verbose=verbose, capture_output=True)
        print(result.stdout)

def replication_check(cluster_name, show_spock_tables=False, database_name=None):
    """Print replication status on every node"""
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None

    if database_name is None:
        db_name = db[0]["name"]
    else:
        for i in db:
            if i["name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["ip_address"]
        os_user = n["os_user"]
        ssh_key = n["ssh_key"]

        if show_spock_tables:
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
    db, db_settings, nodes = load_json(cluster_name)
    rc = 0
    knt = 0
    for nd in nodes:
        if node == "all" or node == nd["name"]:
            knt += 1
            rc = util.echo_cmd(
                f"{nd['path']}/pgedge/pgedge {cmd}",
                host=nd["ip_address"],
                usr=nd["os_user"],
                key=nd["ssh_key"]
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
       :param app_name: The application name, pgbench or northwind.
       :param factor: The scale flag for pgbench.
    """
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["name"]
    else:
        for i in db:
            if i["name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    ctl = os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app pgbench-install {db_name} {factor} default",
                          host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app northwind-install {db_name} default",
                          host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")

def app_remove(cluster_name, app_name, database_name=None):
    """Remove test application [ pgbench | northwind ].

       Remove a test application from all of the nodes in a cluster.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n
       Example: cluster app-remove pgbench
       :param cluster_name: The name of the cluster.
       :param app_name: The application name, pgbench or northwind.
    """
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["name"]
    else:
        for i in db:
            if i["name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    ctl = os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app pgbench-remove {db_name} default",
                          host=ndip, usr=n["os_user"], key=n["ssh_key"])
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["ip_address"]
            util.echo_cmd(f"{ndpath}{ctl} app northwind-remove {db_name} default",
                          host=ndip, usr=n["os_user"], key=n["ssh_key"])
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")

def replication_all_tables(cluster_name, database_name=None):
    """Add all tables in the database to replication on every node."""
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None

    if database_name is None:
        db_name = db[0]["name"]
    else:
        for i in db:
            if i["name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    if "auto_ddl" in db_settings and db_settings["auto_ddl"] == "on":
        util.exit_message(f"Auto DDL enabled for db {database_name}")

    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["ip_address"]
        os_user = n["os_user"]
        ssh_key = n["ssh_key"]
        cmd = f"{nc} spock repset-add-table default '*' {db_name}"
        util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)

if __name__ == "__main__":
    fire.Fire(
        {
            "json-template": json_template,
            "json-validate": json_validate,
            "init": init,
            "list-nodes": list_nodes,
            "add-node": add_node,
            "remove-node": remove_node,
            "replication-begin": replication_all_tables,
            "replication-check": replication_check,
            "add-db": add_db,
            "remove": remove,
            "command": command,
            "ssh": ssh,
            "app-install": app_install,
            "app-remove": app_remove
        }
    )

