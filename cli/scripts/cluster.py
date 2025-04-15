#  Copyright 2022-2025 PGEDGE  All rights reserved. #
import json
import datetime
import os
import util
import fire
import meta
import time
import sys
import getpass
import re
from tabulate import tabulate # type: ignore
from ipaddress import ip_address

try:
    import etcd
    import ha_patroni
except Exception:
    pass

BASE_DIR = "cluster"
DEFAULT_REPO = "https://pgedge-download.s3.amazonaws.com/REPO"

def run_cmd(
    cmd, node, message, verbose, capture_output=False, ignore=False, important=False
):
    """
    Run a command on a remote node via SSH.

    Args:
        cmd (str): The command to run.
        node (dict): The node information.
        message (str): Message to display.
        verbose (bool): Verbose output.
        capture_output (bool): Capture command output.
        ignore (bool): Ignore errors.
        important (bool): Important command.

    Returns:
        result: The result of the command execution.
    """
    name = node["name"]
    message = name + " - " + message
    return util.run_rcommand(
        cmd=cmd,
        message=message,
        host=node["public_ip"],
        usr=node["os_user"],
        key=node["ssh_key"],
        verbose=verbose,
        capture_output=capture_output,
        ignore=ignore,
        important=important,
    )

def ssh(cluster_name, node_name):
    """An SSH Terminal session into the specified node."""
    json_validate(cluster_name)
    db, db_settings, nodes = load_json(cluster_name)

    for nd in nodes:
        if node_name == nd["name"]:
            ip = nd["public_ip"] if "public_ip" in nd else nd["private_ip"]
            if not ip:
                util.exit_message(
                    f"Node '{node_name}' does not have a valid IP address."
                )
            util.echo_cmd(
                f'ssh -i {nd["ssh"]["private_key"]} {nd["ssh"]["os_user"]}@{ip}'
            )
            util.exit_cleanly(0)

    util.exit_message(f"Could not locate node '{node_name}'")


def set_firewalld(cluster_name):
    """Open up nodes only to each other on pg port (WIP)"""
    ## install & start firewalld if not present
    rc = util.echo_cmd("sudo firewall-cmd --version")
    if rc != 0:
        rc = util.echo_cmd("sudo dnf install -y firewalld")
        rc = util.echo_cmd("sudo systemctl start firewalld")

    db, db_settings, nodes = load_json(cluster_name)

    for nd in nodes:
        util.message(
            f'OUT name={nd["name"]}, ip_address={nd["public_ip"]}, port={nd["port"]}',
            "info",
        )
        out_name = nd["name"]
        for in_nd in nodes:
            if in_nd["name"] != out_name:
                print(
                    f'   IN    name={in_nd["name"]}, ip_address={in_nd["public_ip"]}, port={in_nd["port"]}'
                )


def get_cluster_info(cluster_name, create=True):
    """Returns the cluster directory and file path for a given cluster name."""
    cluster_dir = os.path.join(util.MY_HOME, BASE_DIR, cluster_name)
    cluster_file = os.path.join(cluster_dir, f"{cluster_name}.json")

    if create:
        os.makedirs(cluster_dir, exist_ok=True)

    return cluster_dir, cluster_file


def get_cluster_json(cluster_name):
    """Load the cluster JSON configuration file."""
    cluster_dir, cluster_file = get_cluster_info(cluster_name, False)

    if not os.path.isdir(cluster_dir):
        util.exit_message(f"Cluster directory '{cluster_dir}' not found")

    if not os.path.isfile(cluster_file):
        util.message(f"Cluster file '{cluster_file}' not found", "warning")
        return None

    try:
        with open(cluster_file, "r") as f:
            return json.load(f)
    except Exception as e:
        util.exit_message(f"Unable to load cluster def file '{cluster_file}\n{e}")


def write_cluster_json(cluster_name, cj):
    """Write the updated cluster configuration to the JSON file."""
    cluster_dir, cluster_file = get_cluster_info(cluster_name)
    cj["update_date"] = datetime.datetime.now().astimezone().isoformat()
    try:
        cjs = json.dumps(cj, indent=2)
        util.message(
            f"write_cluster_json {cluster_name}, {cluster_dir}, "
            f"{cluster_file},\n{cjs}",
            "debug",
        )
        with open(cluster_file, "w") as f:
            f.write(cjs)
    except Exception as e:
        util.exit_message(f"Unable to write_cluster_json {cluster_file}\n{str(e)}")


def load_json(cluster_name):
    """
    Load a JSON config file for a cluster.

    Args:
        cluster_name (str): The name of the cluster.

    Returns:
        tuple: (db, db_settings, nodes)
    """

    parsed_json = get_cluster_json(cluster_name)
    if parsed_json is None:
        util.exit_message("Unable to load cluster JSON")

    # Extract database settings
    pgedge = parsed_json.get("pgedge", {})
    db_settings = {
        "pg_version": pgedge.get("pg_version", ""),
        "spock_version": pgedge.get("spock", {}).get("spock_version", ""),
        "auto_ddl": pgedge.get("spock", {}).get("auto_ddl", "on"),
        "auto_start": pgedge.get("auto_start", "on"),
    }

    db = []
    if "databases" not in pgedge:
        util.exit_message("databases key is missing")

    for database in pgedge.get("databases"):
        if set(database.keys()) != {"db_name", "db_user", "db_password"}:
            util.exit_message(
                "Each database entry must contain db_name, db_user, and db_password"
            )

        db.append(
            {
                "db_name": database["db_name"],
                "db_user": database["db_user"],
                "db_password": database["db_password"],
            }
        )

    # Extract node information
    nodes = []
    for group in parsed_json.get("node_groups", []):
        ssh_info = group.get("ssh", {})
        os_user = ssh_info.get("os_user", "")
        ssh_key = ssh_info.get("private_key", "")

        node_info = {
            "name": group.get("name", ""),
            "is_active": group.get("is_active", ""),
            "public_ip": group.get("public_ip", ""),
            "private_ip": group.get("private_ip", ""),
            "port": group.get("port", ""),
            "path": group.get("path", ""),
            "os_user": os_user,
            "ssh_key": ssh_key,
            "backrest": group.get("backrest", {}),
        }

        if not node_info["public_ip"] and not node_info["private_ip"]:
            util.exit_message(
                f"Node '{node_info['name']}' must have either a public_ip or private_ip defined."
            )
        # Process sub_nodes
        sub_node_list = []
        for sub_node in group.get("sub_nodes", []):
            sub_node_info = {
                "name": sub_node.get("name", ""),
                "is_active": sub_node.get("is_active", ""),
                "public_ip": sub_node.get("public_ip", ""),
                "private_ip": sub_node.get("private_ip", ""),
                "port": sub_node.get("port", ""),
                "path": sub_node.get("path", ""),
                "os_user": os_user,
                "ssh_key": ssh_key,
            }

            if not sub_node_info["public_ip"] and not sub_node_info["private_ip"]:
                util.exit_message(
                    f"Sub-node '{sub_node_info['name']}' must have either a public_ip or private_ip defined."
                )
            sub_node_list.append(sub_node_info)
        node_info["sub_nodes"] = sub_node_list

        nodes.append(node_info)

    return db, db_settings, nodes


def save_updated_json(cluster_name, updated_json):
    """
    Save the updated JSON configuration back to the appropriate file.
    Args:
        cluster_name (str): The name of the cluster.
        updated_json (dict): The updated JSON data to be saved.
    """
    # Define the path to the JSON file
    cluster_path = f"cluster/{cluster_name}/{cluster_name}.json"

    # Ensure the directory exists
    directory = os.path.dirname(cluster_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the updated JSON to the file
    with open(cluster_path, "w") as json_file:
        json.dump(updated_json, json_file, indent=4)
    print(f"Updated JSON saved to {cluster_path}")


def json_validate(cluster_name):
    """Validate and update a cluster configuration JSON file."""

    # Function to exit with a message
    class Util:
        @staticmethod
        def exit_message(message, code=1):
            print(f"✘ {message}")
            sys.exit(code)

        @staticmethod
        def message(message, level="info"):
            print(f"{message}")

    util = Util()

    pg_default, pgs = meta.get_default_pg()

    # Function to get cluster directory and file paths
    def get_cluster_info(cluster_name):
        cluster_dir = os.path.join(os.getcwd(), "cluster", cluster_name)
        cluster_file = os.path.join(cluster_dir, f"{cluster_name}.json")
        return cluster_dir, cluster_file

    # Load the cluster JSON configuration file
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
                f"Unable to load cluster definition file '{cluster_file}': {e}"
            )

    # Save the updated JSON configuration back to the appropriate file
    def save_updated_json(cluster_name, updated_json):
        cluster_dir, cluster_file = get_cluster_info(cluster_name)
        updated_json["update_date"] = datetime.datetime.now().astimezone().isoformat()
        try:
            with open(cluster_file, "w") as json_file:
                json.dump(updated_json, json_file, indent=2)
            print(f"Updated JSON saved to {cluster_file}")
        except Exception as e:
            util.exit_message(f"Unable to save updated JSON: {e}")

    parsed_json = get_cluster_json(cluster_name)
    if parsed_json is None:
        util.exit_message("Unable to load cluster JSON")

    # Initialize a summary dictionary
    summary = {
        "cluster_name": cluster_name,
        "total_nodes": 0,
        "node_details": [],
        "subnodes_info": [],
    }

    # Check for required top-level keys
    required_top_keys = ["cluster_name", "pgedge", "node_groups"]
    for key in required_top_keys:
        if key not in parsed_json:
            util.exit_message(f"{key} is missing")

    # Ensure pgedge section is complete
    pgedge_defaults = {
        "pg_version": pg_default,
        "spock": {"spock_version": ""},
        "databases": [],
    }
    if "pgedge" not in parsed_json:
        parsed_json["pgedge"] = pgedge_defaults

    # Ensure json_version is correct
    if parsed_json.get("json_version") != "1.0":
        parsed_json["json_version"] = "1.0"

    # Validate Spock version
    pg_version = parsed_json["pgedge"].get("pg_version", pg_default)
    spock_version = parsed_json["pgedge"].get("spock", {}).get("spock_version", "")
    # Allow empty spock_version
    if spock_version.lower() == "default":
        util.exit_message(
            "Spock version cannot be 'default'. Please specify a valid version or leave it blank."
        )

    # Fetch databases info (if any)
    databases = parsed_json["pgedge"].get("databases", [])
    summary["databases"] = databases

    # Validate and update node_groups
    for idx, node in enumerate(parsed_json.get("node_groups", [])):
        summary["total_nodes"] += 1  # Increment total node count
        node_info = {
            "node_index": idx + 1,  # Start numbering nodes from 1
            "public_ip": node.get("public_ip", ""),
            "private_ip": node.get("private_ip", ""),
            "port": node.get("port", 5432),
            "is_active": node.get("is_active", "off"),
            "path": node.get("path", "/var/lib/postgresql"),
            "replicas": node.get("replicas", 0),  # Default to 0 if not present
        }

        # Validate subnodes
        sub_nodes = node.get("sub_nodes", [])
        subnode_count = len(sub_nodes) if isinstance(sub_nodes, list) else 0
        if subnode_count > 0:
            subnode_info = f"Node {idx + 1} Subnodes: {subnode_count}"
        else:
            subnode_info = f"Node {idx + 1} Subnodes: None"
        summary["subnodes_info"].append(subnode_info)

        # Append node details
        summary["node_details"].append(node_info)

    # Save updated JSON
    save_updated_json(cluster_name, parsed_json)

    lines = []
    lines.append(f"# Updated JSON saved to cluster/{cluster_name}/{cluster_name}.json")
    lines.append(f"Cluster Name: {summary['cluster_name']}")
    lines.append(f"Total Nodes: {summary['total_nodes']}")
    lines.append(f"PostgreSQL Version: {pg_version}")
    lines.append(
        f"Spock Version: {spock_version if spock_version else 'Not specified'}"
    )

    #
    # 1) TEXTUAL SUMMARY DATABASE DISPLAY
    #
    if len(databases) == 0:
        lines.append("Databases: None")
    elif len(databases) == 1:
        db = databases[0]
        lines.append(f"Database: {db.get('db_name', '')}")
        lines.append(f"    User: {db.get('db_user', '')}")
    else:
        # Two or more databases
        i = 1
        for db in databases:
            lines.append(f"Database {i}: {db.get('db_name', '')}")
            lines.append(f"     User: {db.get('db_user', '')}")
            i += 1

    lines.append("Node Details:")
    for node in summary["node_details"]:
        lines.append(
            f"  Node {node['node_index']}: Public IP={node['public_ip']}, "
            f"Private IP={node['private_ip']}, Port={node['port']}, "
            f"Active={node['is_active']}, Path={node['path']}, Replicas={node['replicas']}"
        )
    lines.append("Subnodes Info:")
    for subnode in summary["subnodes_info"]:
        lines.append(f"  {subnode}")

    # Determine the maximum line length based on actual content
    max_length = max(len(line.rstrip()) for line in lines)  # Exclude trailing spaces

    # Bold formatting for the display
    bold_start = "\033[1m"
    bold_end = "\033[0m"

    # Create the dynamic border based on max_length
    border = "#" * (max_length + 4)  # Add padding for aesthetics

    # Display the updated summary with borders aligned to content
    print(border)
    print(
        f"# {bold_start}Cluster JSON cluster/{cluster_name}/{cluster_name}.json validated{bold_end}".center(
            max_length + 4
        )
    )
    print(
        f"# {bold_start}Cluster Name{bold_end}       : {summary['cluster_name']}".ljust(
            max_length + 4
        )
    )
    print(
        f"# {bold_start}Number of Nodes{bold_end}    : {summary['total_nodes']}".ljust(
            max_length + 4
        )
    )
    print(
        f"# {bold_start}PostgreSQL Version{bold_end} : {pg_version}".ljust(
            max_length + 4
        )
    )
    print(
        f"# {bold_start}Spock Version{bold_end}      : {spock_version if spock_version else 'Not specified'}".ljust(
            max_length + 4
        )
    )

    #
    # 2) BORDERED SUMMARY DATABASE DISPLAY
    #
    if len(databases) == 0:
        print(
            f"# {bold_start}Databases{bold_end}          : None".ljust(
                max_length + 4
            )
        )
    elif len(databases) == 1:
        db = databases[0]
        print(
            f"# {bold_start}Database{bold_end}           : {db.get('db_name','')}".ljust(
                max_length + 4
            )
        )
        # Align "User" nicely
        user_line = f"#      {bold_start}User{bold_end}          : {db.get('db_user','')}"
        print(user_line.ljust(max_length + 4))
    else:
        # Two or more databases
        print(f"# {bold_start}Databases{bold_end}:".ljust(max_length + 4))
        for i, db in enumerate(databases, start=1):
            db_line = f"#  {bold_start} Database {i} {bold_end}      : {db.get('db_name','')}"
            user_line = f"# {bold_start}     User   {bold_end}       : {db.get('db_user','')}"
            print(db_line.ljust(max_length + 4))
            print(user_line.ljust(max_length + 4))

    for node in summary["node_details"]:
        print(f"# {bold_start}Node {node['node_index']}{bold_end}")
        print(f"#      {bold_start}Public IP{bold_end}     : {node['public_ip']}")
        print(f"#      {bold_start}Private IP{bold_end}    : {node['private_ip']}")
        print(f"#      {bold_start}Port{bold_end}          : {node['port']}")
        print(f"#      {bold_start}Replicas{bold_end}      : {node['replicas']}")
    print(border)

def ssh_install_pgedge(
    cluster_name,db_name, db_settings, db_user, db_passwd, nodes, install, verbose
):
    """
    Install and configure pgEdge on a list of nodes.

    Args:
        cluster_name (str): The name of the cluster.
        db (str): The database name.
        db_settings (dict): Database settings (including auto_ddl).
        db_user (str): The database user.
        db_passwd (str): The database user password.
        nodes (list): The list of nodes (each node is a dict).
        install (bool): Whether or not to perform 'pgedge install'.
        verbose (bool): Whether to produce verbose output.
    """

    if install is None:
        install = True

    # Count total nodes (including sub-nodes, if needed)
    total_nodes = len(nodes)

    for n in nodes:
        # Fall back to default repo if none provided
        REPO = os.getenv("REPO", "") or DEFAULT_REPO
        os.environ["REPO"] = REPO

        ndnm = n["name"]
        ndpath = n["path"]
        ndip = n["public_ip"] or n["private_ip"]
        ndport = str(n.get("port", "5432"))
        pg = db_settings["pg_version"]
        spock = db_settings["spock_version"]

        # Print an informational header
        print_install_hdr(
            cluster_name,
            db_name,
            db_user,
            total_nodes,
            ndnm,
            ndpath,
            ndip,
            ndport,
            REPO
        )

        # 1) Optionally install pgEdge software
        if install:
            install_py = "install.py"
            cmd0 = f"export REPO={REPO}; "
            cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
            cmd2 = f'python3 -c "\\$(curl -fsSL {REPO}/{install_py})"'
            message = f"Installing pgEdge on {ndnm}"
            run_cmd(cmd0 + cmd1 + cmd2, n, message=message, verbose=verbose)

        # 2) Run pgEdge setup command
        nc = os.path.join(ndpath, "pgedge", "pgedge ")
        setup_parms = f" -U {db_user} -P {db_passwd} -d {db_name} --port {ndport}"
        if pg:
            setup_parms += f" --pg_ver {pg}"
        if spock:
            setup_parms += f" --spock_ver {spock}"
        if db_settings.get("auto_start") == "on":
            setup_parms += " --autostart"

        cmd_setup = f"{nc} setup {setup_parms}"
        message = f"Setting up pgEdge on {ndnm}"
        run_cmd(cmd_setup, n, message=message, verbose=verbose)
        if db_settings.get("auto_ddl") == "on":
            # Build the minimal db dict and call create_spock_db
            spock_db = {
                "db_name": db_name,
                "db_user": db_user,
                "db_password": db_passwd
            }
            create_spock_db([n], spock_db, db_settings, initial=True)


def ssh_cross_wire_pgedge(
    cluster_name, db, db_settings, db_user, db_passwd, nodes, verbose
):
    """
    Create nodes and subscriptions on every node in a cluster.

    Args:
        cluster_name (str): The name of the cluster.
        db (str): The database name.
        db_settings (dict): Database settings.
        db_user (str): The database user.
        db_passwd (str): The database password.
        nodes (list): The list of nodes.
        verbose (bool): Verbose output.
    """
    sub_array = []
    for prov_n in nodes:
        ndnm = prov_n["name"]
        ndpath = prov_n["path"]
        nc = os.path.join(ndpath, "pgedge", "pgedge")
        ndip = prov_n["private_ip"] if prov_n["private_ip"] else prov_n["public_ip"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]

        try:
            ndport = str(prov_n["port"])
        except KeyError:
            ndport = "5432"

        cmd1 = (
            f"{nc} spock node-create {ndnm} "
            f"'host={ndip} user={os_user} "
            f"dbname={db} port={ndport}' {db}"
        )
        message = f"Creating node {ndnm}"
        run_cmd(cmd1, prov_n, message=message, verbose=verbose)

        for sub_n in nodes:
            sub_ndnm = sub_n["name"]
            if sub_ndnm != ndnm:
                sub_ndip = (
                    sub_n["private_ip"] if sub_n["private_ip"] else sub_n["public_ip"]
                )
                sub_name = f"sub_{ndnm}{sub_ndnm}"
                cmd = f"{nc} spock sub-create {sub_name} 'host={sub_ndip} user={os_user} dbname={db} port={sub_n['port']}' {db}"
                sub_array.append([cmd, ndip, os_user, ssh_key, prov_n, sub_name])

    for n in sub_array:
        cmd = n[0]
        node = n[4]
        sub_name = n[5]
        message = f"Creating subscriptions {sub_name}"
        run_cmd(cmd, node, message=message, verbose=verbose)

    cmd = f"{nc} spock node-list {db}"
    message = "Listing spock nodes"
    result = run_cmd(cmd, prov_n, message=message, verbose=verbose, capture_output=True)

    print("\n")
    print(result.stdout)


def remove(cluster_name, force=False):
    """Remove a cluster. 
    
    This will remove spock subscriptions and nodes, and
    then stop postgres on each node. If the flag force is set to true,
    then it will also remove the pgedge directory on each node.
    This command requires a JSON file with the same name as the cluster to
    be in the cluster/<cluster_name>.
    Example: cluster remove demo
    :param cluster_name: The name of the cluster.
    """
    db, db_settings, nodes = load_json(cluster_name)

    ssh_un_cross_wire(
        cluster_name,
        db[0]["db_name"],
        db_settings,
        db[0]["db_user"],
        db[0]["db_password"],
        nodes,
    )

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + os.sep + "pgedge" + os.sep + "pgedge stop"
        util.echo_cmd(cmd, host=nd["public_ip"], usr=nd["os_user"], key=nd["ssh_key"])
    if force == True:
        for nd in nodes:
            util.message("\n## Ensure that pgEdge root directory is gone")
            cmd = f"rm -rf {nd['path']}{os.sep}pgedge"
            util.echo_cmd(
                cmd, host=nd["public_ip"], usr=nd["os_user"], key=nd["ssh_key"]
            )


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

    verbose = db_settings.get("log_level", "none")

    db_json = {}
    db_json["db_user"] = username
    db_json["db_password"] = password
    db_json["db_name"] = database_name

    util.message(f"## Creating database {database_name}")
    create_spock_db(nodes, db_json, db_settings, initial=False)
    ssh_cross_wire_pgedge(
        cluster_name, database_name, db_settings, username, password, nodes, verbose
    )
    util.message(f"## Updating cluster '{cluster_name}' json definition file")
    update_json(cluster_name, db_json)


def json_template(cluster_name, db, num_nodes, usr, passwd, pg, port):
    """Create a template for a cluster configuration JSON file.
   
       Create a JSON configuration file template that can be modified to fully define a remote cluster. \n
       Example: cluster define-remote demo db 3 lcusr lcpasswd 16 5432
       :param cluster_name: The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
       :param db: The database name.
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgres version of the database.
       :param port1: The port number for the database.
    """
    json_create(cluster_name, num_nodes, db, usr, passwd, pg, port, True)


def json_create(
    cluster_name, num_nodes, db, usr, passwd, pg_ver=None, port=None, force=False
):
    """
    Create a cluster configuration JSON file with options for spock and pgBackRest.

    Usage:
        ./pgedge cluster json-create CLUSTER_NAME NUM_NODES DB USR PASSWD [pg_ver=PG_VERSION] [--port PORT]

    Args:
        cluster_name (str): The name of the cluster.
        num_nodes (int): The number of main nodes in the cluster.
        db (str): The database name.
        usr (str): The username of the superuser created for this database.
        passwd (str): The password for the above user.
        pg_ver (str or int, optional): The PostgreSQL version of the database.
        port (str or int, optional): The port number for the primary nodes. Must be between 1 and 65535. Defaults to '5432'.
    """

    # Function to exit with a message
    class Util:
        @staticmethod
        def exit_message(message, code=1):
            print(f"✘ {message}")
            sys.exit(code)

        @staticmethod
        def message(message, level="info"):
            print(f"{message}")

    util = Util()
    
    # Assuming meta is a module that provides default PostgreSQL and Spock versions
    pg_default, pgs = meta.get_default_pg()
    if not pg_ver:
        spock_default, spocks = meta.get_default_spock(str(pg_default))
    else:
        spock_default, spocks = meta.get_default_spock(str(pg_ver))
        pg_default = pg_ver

    # Check if 'json-template' alias was used and display a warning
    if "json-template" in sys.argv:
        util.message(
            "⚠️  Warning: The 'json-template' command will be deprecated in future releases. "
            "Please use 'json-create' for creating cluster JSON configurations.",
            "warning",
        )

    # Validate and process parameters
    try:
        # Ensure required parameters are provided
        if not cluster_name:
            raise ValueError("CLUSTER_NAME is required.")
        if not num_nodes:
            raise ValueError("NUM_NODES is required.")
        if not db:
            raise ValueError("DB is required.")
        if not usr:
            raise ValueError("USR is required.")
        if not passwd:
            raise ValueError("PASSWD is required.")

        # Convert num_nodes to int
        try:
            num_nodes = int(num_nodes)
            if num_nodes <= 0:
                raise ValueError("NUM_NODES must be a positive integer.")
        except ValueError:
            raise ValueError("NUM_NODES must be a positive integer.")

        # Handle PostgreSQL version
        if pg_ver is not None:
            pg_str = str(pg_ver).strip()
            if pg_str not in pgs:
                raise ValueError(
                    f"Invalid PostgreSQL version. Allowed versions are {pgs}."
                )
            pg_version_int = int(pg_str)
        else:
            pg_version_int = None  # Will prompt later if not provided

        # Handle port number
        if port is not None:
            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError("PORT must be an integer between 1 and 65535.")
            except ValueError:
                raise ValueError("PORT must be an integer between 1 and 65535.")
        else:
            port = None  # Will use default later if not provided

    except ValueError as e:
        print(f"Error: {e}")
        print("\nUsage:")
        print(
            "    ./pgedge cluster json-create CLUSTER_NAME NUM_NODES DB USR PASSWD [pg_ver=PG_VERSION] [--port PORT]"
        )
        print("\nFor more help, run:")
        print("    ./pgedge cluster json-create --help")
        sys.exit(1)

    # Function to get cluster directory and file paths
    def get_cluster_info(cluster_name):
        cluster_dir = os.path.join(os.getcwd(), "cluster", cluster_name)
        cluster_file = os.path.join(cluster_dir, f"{cluster_name}.json")
        return cluster_dir, cluster_file

    # Get cluster directory and file paths
    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    try:
        os.makedirs(cluster_dir, exist_ok=True)
    except OSError as e:
        util.exit_message(f"Error creating directory '{cluster_dir}': {e}")

    cluster_json = {
        "json_version": "1.0",
        "cluster_name": cluster_name,
        "log_level": "debug",
        "update_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S GMT"),
    }

    # Handle PostgreSQL version
    if force:
        pg_version_int = pg_default
    else:
        while True:
            if pg_version_int is not None:
                pg_input = str(pg_version_int)
            else:
                pg_input = (
                    input(f"PostgreSQL version {pgs} (default: '{pg_default}'): ").strip()
                    or pg_default
                )

            if pg_input in pgs:
                pg_version_int = int(pg_input)
                break
            else:
                print(f"Invalid PostgreSQL version. Allowed versions are: {pgs}.")

    pgedge_json = {"pg_version": str(pg_version_int), "auto_start": "off"}

    # Prompt for Spock version
    if force:
        spock_version = spock_default
    else:
        while True:
            spock_version = (
                input(
                    f"Spock version {spocks} (default: '{spock_default}'): "
                ).strip()
                or spock_default
            )
            if spock_version not in spocks:
                print(f"Invalid spock version. Allowed versions are: {spocks}.")
            else:
                break

    spock_json = {"spock_version": spock_version, "auto_ddl": "on"}
    pgedge_json["spock"] = spock_json

    database_json = [{"db_name": db, "db_user": usr, "db_password": passwd}]
    pgedge_json["databases"] = database_json

    cluster_json["pgedge"] = pgedge_json

    # Ask if this is an HA Cluster
    if True:
        is_ha_cluster = False
    else:
        ha_cluster_input = input("Is this an HA Cluster? (Y/N): ").strip().lower()
        is_ha_cluster = ha_cluster_input in ["y", "yes"]

    # Store 'is_ha_cluster' in the cluster JSON
    cluster_json["is_ha_cluster"] = is_ha_cluster

    # Ask if pgBackRest should be enabled
    if force:
        backrest_enabled = False
    else:
        backrest_enabled_input = (
            input("Enable pgBackRest? (Y/N) (default: 'N'): ")
            .strip()
            .lower()
        )
        backrest_enabled = backrest_enabled_input in ["y", "yes"]

    # Initialize backrest_json based on user input
    if backrest_enabled:
        backrest_storage_path = (
            input("   pgBackRest storage path (default: '/var/lib/pgbackrest'): ").strip()
            or "/var/lib/pgbackrest"
        )
        backrest_archive_mode = (
            input("   pgBackRest archive mode (on/off) (default: 'on'): ").strip().lower()
            or "on"
        )
        if backrest_archive_mode not in ["on", "off"]:
            util.exit_message(
                "Invalid pgBackRest archive mode. Allowed values are 'on' or 'off'."
            )
         # Optionally, ask for repo1_type or default to posix
        repo1_type = (
            input("   pgBackRest repository type (posix/s3) (default: 'posix'): ")
            .strip()
            .lower()
            or "posix"
        )
        if repo1_type not in ["posix", "s3"]:
            util.exit_message(
                "Invalid pgBackRest repository type. Allowed values are 'posix' or 's3'."
            )
        # Create base pgBackRest configuration
        backrest_json = {
            "stanza": f"{cluster_name}_stanza_",  # base stanza; node name will be appended later
            "repo1_path": backrest_storage_path,
            "repo1_retention_full": "7",
            "log_level_console": "info",
            "repo1_cipher-type": "aes-256-cbc",
            "archive_mode": backrest_archive_mode,
            "repo1_type": repo1_type,
        }
    else:
        backrest_json = None

    node_groups = []
    os_user = getpass.getuser()
    default_ip = "127.0.0.1"
    default_port = port if port is not None else 5432

    current_replica_port = 6432  # Starting port for replica nodes

    for n in range(1, num_nodes + 1):
        print(f"\nConfiguring Node {n}")
        node_json = {
            "ssh": {"os_user": os_user, "private_key": ""},
            "name": f"n{n}",
            "is_active": "on",
        }
        if force:
            public_ip = default_ip
            private_ip = default_ip
        else:
            public_ip = (
                input(
                    f"  Public IP address for Node {n} (default: '{default_ip}'): "
                ).strip()
                or default_ip
            )
            private_ip = (
                input(
                    f"  Private IP address for Node {n} (default: '{public_ip}'): "
                ).strip()
                or public_ip
            )
        node_json["public_ip"] = public_ip
        node_json["private_ip"] = private_ip

        # Set node_port based on the port flag or default
        if port is not None:
            node_port = port
            print(f"  Using port {node_port} for Node {n} ")
            port = port + 1
        elif force:
            node_port = default_port
            default_port = default_port + 1
        else:
            node_default_port = default_port
            while True:
                node_port_input = input(
                    f"  PostgreSQL port for Node {n} (default: '{node_default_port}'): "
                ).strip()
                if not node_port_input:
                    node_port = node_default_port
                    break
                else:
                    try:
                        node_port = int(node_port_input)
                        if node_port < 1 or node_port > 65535:
                            print("  Invalid port number. Please enter a number between 1 and 65535.")
                            continue
                        break
                    except ValueError:
                        print("  Invalid port input. Please enter a valid integer.")
        node_json["port"] = str(node_port)

        node_json["path"] = f"/home/{os_user}/{cluster_name}/n{n}"
        
        # Update backrest configuration to always append the node name to the repo1_path.
        if backrest_enabled:
            # Create a copy of the global backrest_json to avoid modifying it for all nodes.
            node_backrest = backrest_json.copy()
            # Append the node name to the repo1_path so each node gets a unique backup directory.
            node_backrest["repo1_path"] = f"{node_backrest['repo1_path'].rstrip('/')}/{node_json['name']}"
            # Update the stanza value to include the node name.
            node_backrest["stanza"] = f"{cluster_name}_stanza_{node_json['name']}"
            node_json["backrest"] = node_backrest

        if is_ha_cluster:
            while True:
                replicas_for_node_input = input(
                    f"  Number of replica nodes for Node {n}: "
                ).strip()
                try:
                    replicas_for_node = int(replicas_for_node_input)
                    if replicas_for_node < 0:
                        print("  Number of replicas cannot be negative. Please enter 0 or a positive integer.")
                        continue
                    break
                except ValueError:
                    print("  Invalid input. Please enter a numeric value.")
        else:
            replicas_for_node = 0

        node_json["replicas"] = replicas_for_node

        if replicas_for_node > 0:
            node_json["sub_nodes"] = []
            for i in range(1, replicas_for_node + 1):
                print(f"\n  Configuring Replica Node {i} for Node {n}:")
                sub_node_json = {
                    "ssh": {"os_user": os_user, "private_key": ""},
                    "name": f"{node_json['name']}_ro_{i}",
                    "is_active": "off",
                }

                public_ip = (
                    input(
                        f"    Public IP address of replica Node {i} (default: '{default_ip}'): "
                    ).strip()
                    or default_ip
                )
                private_ip = (
                    input(
                        f"    Private IP address of replica Node {i} (default: '{public_ip}'): "
                    ).strip()
                    or public_ip
                )
                sub_node_json["public_ip"] = public_ip
                sub_node_json["private_ip"] = private_ip

                while True:
                    replica_port_input = input(
                        f"    PostgreSQL port of replica Node {i} (default: '{current_replica_port}'): "
                    ).strip()
                    if not replica_port_input:
                        replica_port = current_replica_port
                        current_replica_port += 1
                        break
                    else:
                        try:
                            replica_port = int(replica_port_input)
                            if replica_port < 1 or replica_port > 65535:
                                print("    Invalid port number. Please enter a number between 1 and 65535.")
                                continue
                            current_replica_port = replica_port + 1
                            break
                        except ValueError:
                            print("    Invalid port input. Please enter a valid integer.")
                sub_node_json["port"] = str(replica_port)
                sub_node_json["path"] = f"/home/{os_user}/{cluster_name}/{sub_node_json['name']}"
                
                # Update backrest configuration for replica nodes similarly.
                if backrest_enabled:
                    sub_node_backrest = backrest_json.copy()
                    sub_node_backrest["repo1_path"] = f"{sub_node_backrest['repo1_path'].rstrip('/')}/{sub_node_json['name']}"
                    sub_node_backrest["stanza"] = f"{cluster_name}_stanza_{sub_node_json['name']}"
                    sub_node_json["backrest"] = sub_node_backrest

                node_json.setdefault("sub_nodes", []).append(sub_node_json)

        node_groups.append(node_json)

    cluster_json["node_groups"] = node_groups

    # Validate configuration
    validation_errors = []

    for node in node_groups:
        if not node.get("name"):
            validation_errors.append("Node name is missing.")
        if not node.get("port"):
            validation_errors.append(f"Port is missing for node {node.get('name')}.")
        else:
            try:
                port_int = int(node["port"])
                if port_int < 1 or port_int > 65535:
                    validation_errors.append(
                        f"Invalid port number {port_int} for node {node.get('name')}."
                    )
            except ValueError:
                validation_errors.append(
                    f"Port must be a valid number for node {node.get('name')}."
                )

        public_ip = node.get("public_ip", "")
        private_ip = node.get("private_ip", "")
        if not public_ip and not private_ip:
            validation_errors.append(
                f"Either public_ip or private_ip must be provided for node {node.get('name')}."
            )
        try:
            if public_ip:
                ip_address(public_ip)
            if private_ip:
                ip_address(private_ip)
        except ValueError:
            validation_errors.append(
                f"Invalid IP address provided for node {node.get('name')}."
            )

        for sub_node in node.get("sub_nodes", []):
            if not sub_node.get("name"):
                validation_errors.append("Sub-node name is missing.")
            if not sub_node.get("port"):
                validation_errors.append(
                    f"Port is missing for sub-node {sub_node.get('name')}."
                )
            else:
                try:
                    port_int = int(sub_node["port"])
                    if port_int < 1 or port_int > 65535:
                        validation_errors.append(
                            f"Invalid port number {port_int} for sub-node {sub_node.get('name')}."
                        )
                except ValueError:
                    validation_errors.append(
                        f"Port must be a valid number for sub-node {sub_node.get('name')}."
                    )

            public_ip = sub_node.get("public_ip", "")
            private_ip = sub_node.get("private_ip", "")
            if not public_ip and not private_ip:
                validation_errors.append(
                    f"Either public_ip or private_ip must be provided for sub-node {sub_node.get('name')}."
                )
            try:
                if public_ip:
                    ip_address(public_ip)
                if private_ip:
                    ip_address(private_ip)
            except ValueError:
                validation_errors.append(
                    f"Invalid IP address provided for sub-node {sub_node.get('name')}."
                )

    if validation_errors:
        print("\nValidation Errors:")
        for error in validation_errors:
            print(f" - {error}")
        util.exit_message(
            "Configuration validation failed. Please correct the errors and try again."
        )

    bold_start = "\033[1m"
    bold_end = "\033[0m"

    print("\n" + "#" * 80)
    print(f"# {bold_start}Cluster Name{bold_end}       : {cluster_name}")
    print(f"# {bold_start}PostgreSQL Version{bold_end} : {pg_version_int}")
    print(
        f"# {bold_start}Spock Version{bold_end}      : {spock_version if spock_version else 'Not specified'}"
    )
    print(f"# {bold_start}Number of Nodes{bold_end}    : {num_nodes}")
    print(f"# {bold_start}Database Name{bold_end}      : {db}")
    print(f"# {bold_start}User{bold_end}               : {usr}")
    print(
        f"# {bold_start}pgBackRest Enabled{bold_end} : {'Yes' if backrest_enabled else 'No'}"
    )
    if backrest_enabled:
        print(f"#    {bold_start}Storage Path{bold_end}    : {backrest_storage_path}")
        print(f"#    {bold_start}Archive Mode{bold_end}    : {backrest_archive_mode}")
        print(f"#    {bold_start}Repository Type{bold_end} : {repo1_type}")
    for idx, node in enumerate(node_groups, start=1):
        print(f"# {bold_start}Node {idx}{bold_end}")
        print(f"#    {bold_start}Public IP{bold_end}       : {node['public_ip']}")
        print(f"#    {bold_start}Private IP{bold_end}      : {node['private_ip']}")
        print(f"#    {bold_start}Port{bold_end}            : {node['port']}")
    
    print("#" * 80)

    if not force:
        confirm_save = (
            input("Do you want to save this configuration? (Y/N): ").strip().lower()
        )
        if confirm_save not in ["yes", "y"]:
            util.exit_message("Configuration not saved.")

    try:
        with open(cluster_file, "w") as text_file:
            text_file.write(json.dumps(cluster_json, indent=2))
        print(f"\nCluster configuration saved to {cluster_file}")
    except Exception as e:
        util.exit_message(f"Unable to create JSON file: {e}", 1)

def create_spock_db(nodes, db, db_settings, initial=True):
    """
    Create a database on each node using the specified credentials.
    If 'auto_ddl' is on (and this is the initial call), also set Spock GUCs
    via 'db guc-set' for DDL replication.

    :param nodes: List of node dicts with entries like:
                  {
                    "name": str,
                    "public_ip": str (or None),
                    "private_ip": str (or None),
                    "port": int,
                    "path": str,
                    "os_user": str,
                    "ssh_key": str
                  }
    :param db: Dictionary with keys:
                  {
                    "db_name": str,
                    "db_user": str,
                    "db_password": str
                  }
    :param db_settings: Dict that may contain:
                        {
                          "auto_ddl": "on"/"off",
                          ...
                        }
    :param initial: If True, set spock.* GUCs for DDL replication. 
                    If False, just create the DB.
    """

    db_name = db["db_name"]
    db_user = db["db_user"]
    db_pass = db["db_password"]

    auto_ddl = db_settings.get("auto_ddl", "off")

    for n in nodes:
        # Choose whichever IP is present
        ip = n.get("public_ip") or n.get("private_ip")
        port = str(n.get("port", 5432))

        # Full path to pgedge CLI. Example: "/home/ubuntu/n1/pgedge/pgedge"
        pgedge_cli = os.path.join(n["path"], "pgedge", "pgedge")

        #
        # 1) Create DB using "pgedge db create"
        #
        # The pgEdge CLI syntax requires:
        #   pgedge db create -User <USER> -db <DB> -Passwd <PASSWORD> --Port=<PORT>
        #
        create_cmd = (
            f"{pgedge_cli} db create "
            f"-User {db_user} "
            f"-db {db_name} "
            f"-Passwd {db_pass} "
            f"--Port={port}"
        )

        # Use run_cmd(..., ignore=True) to avoid errors if DB already exists
        run_cmd(
            cmd=create_cmd,
            node=n,
            message=f"Creating DB '{db_name}' (if missing) on node '{n['name']}'",
            verbose=False,
            ignore=True
        )

        #
        # 2) If auto_ddl=on and initial, set spock.* GUCs using "db guc-set"
        #
        # The snippet you provided:
        #    cmd = (
        #       f"{pgedge_cli} db guc-set spock.enable_ddl_replication on;"
        #       f" {pgedge_cli} db guc-set spock.include_ddl_repset on;"
        #       f" {pgedge_cli} db guc-set spock.allow_ddl_from_functions on;"
        #    )
        # does not require specifying the DB name or port.
        #
        if auto_ddl == "on" and initial:
            guc_cmd = (
                f"{pgedge_cli} db guc-set spock.enable_ddl_replication on;"
                f" {pgedge_cli} db guc-set spock.include_ddl_repset on;"
                f" {pgedge_cli} db guc-set spock.allow_ddl_from_functions on;"
            )

            run_cmd(
                cmd=guc_cmd,
                node=n,
                message=f"Configuring Spock GUCs on node '{n['name']}'",
                verbose=False,
                ignore=False
            )

def update_json(cluster_name, db_json):
    """Update the cluster JSON configuration with new database information."""
    parsed_json = get_cluster_json(cluster_name)

    cluster_dir, cluster_file = get_cluster_info(cluster_name)

    os.system(f"mkdir -p {cluster_dir}{os.sep}backup")
    timeof = datetime.datetime.now().strftime("%y%m%d_%H%M")
    os.system(
        f"cp {cluster_dir}{os.sep}{cluster_name}.json {cluster_dir}{os.sep}backup/{cluster_name}_{timeof}.json"
    )
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    parsed_json["pgedge"]["databases"].append(db_json)
    try:
        text_file.write(json.dumps(parsed_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to update JSON file", 1)


def init(cluster_name, install=True):
    """
    Initialize a cluster via cluster configuration JSON file.

    This function performs the following steps:
    1. Loads the cluster configuration.
    2. Checks SSH connectivity for all nodes.
    3. Installs pgEdge on all nodes.
    4. Configures Spock for replication.
    5. Integrates pgBackRest on nodes where it is enabled.
       - Creates unique stanza names: {cluster_name}_stanza_{node_name}
       - Removes --pg1-port from set_postgresqlconf / set_hbaconf to avoid errors.
       - Ensures that every pgBackRest configuration value is set before creating the stanza.
       - Appends the node name to both the repo1-path and restore_path.
    6. Creates an initial full backup using pgBackRest.
    7. Performs HA-specific configurations if enabled.
    8. Finalizes and saves the cluster configuration.

    Args:
        cluster_name (str): The name of the cluster.
        install (bool): Whether to install pgEdge on nodes. Defaults to True.
    """
    # 1. Load cluster configuration
    util.message(f"## Loading cluster '{cluster_name}' JSON definition file", "info")
    db, db_settings, nodes = load_json(cluster_name)
    parsed_json = get_cluster_json(cluster_name)
    if parsed_json is None:
        util.exit_message("Unable to load cluster JSON", 1)
    is_ha_cluster = parsed_json.get("is_ha_cluster", False)
    verbose = parsed_json.get("log_level", "info")
    
    # 2. Combine all nodes and sub-nodes into a single list
    all_nodes = nodes.copy()
    for node in nodes:
        if "sub_nodes" in node and node["sub_nodes"]:
            all_nodes.extend(node["sub_nodes"])
    
    # 3. Check SSH connectivity for all nodes
    util.message("## Checking SSH connectivity for all nodes", "info")
    for nd in all_nodes:
        message = f"Checking SSH connectivity on {nd['public_ip']}"
        run_cmd(cmd="hostname", node=nd, message=message, verbose=verbose)
    
    # 4. Install pgEdge on all nodes
    util.message("## Installing pgEdge on all nodes", "info")
    ssh_install_pgedge(
        cluster_name,
        db[0]["db_name"],
        db_settings,
        db[0]["db_user"],
        db[0]["db_password"],
        all_nodes,
        install,
        verbose,
    )
    
    # 5. Configure Spock replication on all nodes (for the first DB)
    util.message("## Configuring Spock replication on all nodes", "info")
    ssh_cross_wire_pgedge(
        cluster_name,
        db[0]["db_name"],
        db_settings,
        db[0]["db_user"],
        db[0]["db_password"],
        all_nodes,
        verbose,
    )
    
    # If additional databases exist, configure them as well
    if len(db) > 1:
        util.message("## Configuring additional databases", "info")
        for database in db[1:]:
            create_spock_db(all_nodes, database, db_settings, initial=False)
            ssh_cross_wire_pgedge(
                cluster_name,
                database["db_name"],
                db_settings,
                database["db_user"],
                database["db_password"],
                all_nodes,
                verbose,
            )
    
    # 6. Integrate pgBackRest (if a "backrest" block is present) on each node
    cluster_name_from_json = parsed_json["cluster_name"]
    
    for idx, node in enumerate(all_nodes, start=1):
        backrest = node.get("backrest")
        if backrest:
            util.message("## Integrating pgBackRest into the cluster", "info")
            util.message(f"### Configuring pgBackRest for node '{node['name']}'", "info")
    
            # Create a unique stanza name: {cluster_name}_stanza_{node_name}
            stanza = f"{cluster_name_from_json}_stanza_{node['name']}"
    
            # Load additional pgBackRest settings from JSON with defaults.
            repo1_retention_full = backrest.get("repo1_retention_full", "7")
            log_level_console = backrest.get("log_level_console", "info")
            repo1_cipher_type = backrest.get("repo1_cipher-type", "aes-256-cbc")
            repo1_type = backrest.get("repo1_type", "posix")  # Could also be "s3", etc.
    
            # Get repo1_path from JSON; if not provided, default to /var/lib/pgbackrest/{node_name}
            json_repo1_path = backrest.get("repo1_path")
            if json_repo1_path:
                repo1_path = json_repo1_path.rstrip('/')
                if not repo1_path.endswith(node["name"]):
                    repo1_path = repo1_path + f"/{node['name']}"
            else:
                repo1_path = f"/var/lib/pgbackrest/{node['name']}"
    
            # Similarly, set restore_path to include node name (if needed)
            restore_path = "/var/lib/pgbackrest_restore"
            if not restore_path.rstrip('/').endswith(node["name"]):
                restore_path = restore_path.rstrip('/') + f"/{node['name']}"
    
            pg_version = db_settings["pg_version"]
            pg1_path = f"{node['path']}/pgedge/data/pg{pg_version}"
            port = node["port"]  # Custom port from JSON
    
            # -- Step 1: Install pgBackRest
            cmd_install_backrest = f"cd {node['path']}/pgedge && ./pgedge install backrest"
            run_cmd(cmd_install_backrest, node=node, message="Installing pgBackRest", verbose=verbose)
    
            # -- Step 2: Configure postgresql.conf for pgBackRest (without --pg1-port)
            cmd_set_postgresqlconf = (
                f"cd {node['path']}/pgedge && "
                f"./pgedge backrest set_postgresqlconf "
                f"--stanza {stanza} "
                f"--pg1-path {pg1_path} "
                f"--repo1-path {repo1_path} "
                f"--repo1-type {repo1_type}"
            )
            run_cmd(cmd_set_postgresqlconf, node=node, message="Modifying postgresql.conf for pgBackRest", verbose=verbose)
    
            # -- Step 3: Configure pg_hba.conf for pgBackRest (without --pg1-port)
            cmd_set_hbaconf = f"cd {node['path']}/pgedge && ./pgedge backrest set_hbaconf"
            run_cmd(cmd_set_hbaconf, node=node, message="Modifying pg_hba.conf for pgBackRest", verbose=verbose)
    
            # -- Step 4: Reload PostgreSQL configuration to apply changes
            sql_reload_conf = "select pg_reload_conf()"
            cmd_reload_conf = f"cd {node['path']}/pgedge && ./pgedge psql '{sql_reload_conf}' {db[0]['db_name']}"
            run_cmd(cmd_reload_conf, node=node, message="Reloading PostgreSQL configuration", verbose=verbose)
    
            # -- Step 5: If using S3 as repository, export necessary environment variables
            if repo1_type.lower() == "s3":
                required_env_vars = [
                    "PGBACKREST_REPO1_S3_KEY",
                    "PGBACKREST_REPO1_S3_BUCKET",
                    "PGBACKREST_REPO1_S3_KEY_SECRET",
                    "PGBACKREST_REPO1_CIPHER_PASS",
                ]
                missing_env_vars = [var for var in required_env_vars if var not in os.environ]
                if missing_env_vars:
                    util.exit_message(
                        f"Environment variables {', '.join(missing_env_vars)} must be set for S3 pgBackRest configuration.",
                        1,
                    )
                s3_exports = " && ".join([f"export {var}={os.environ[var]}" for var in required_env_vars])
                cmd_export_s3 = f"cd {node['path']}/pgedge && {s3_exports}"
                run_cmd(cmd_export_s3, node=node, message="Setting S3 environment variables for pgBackRest", verbose=verbose)
    
            # -- Step 6: Set all pgBackRest backup configuration values
    
            # (a) Set the backup stanza
            cmd_set_backup_stanza = f"cd {node['path']}/pgedge && ./pgedge set BACKUP stanza {stanza}"
            run_cmd(cmd_set_backup_stanza, node=node, message=f"Setting BACKUP stanza '{stanza}' on node '{node['name']}'", verbose=verbose)
    
            # (b) Create restore directory and set restore_path for backups.
            cmd_create_restore_dir = f"sudo mkdir -p {restore_path}"
            run_cmd(cmd_create_restore_dir, node=node, message=f"Creating restore directory {restore_path}", verbose=verbose)
            cmd_set_restore_path = f"cd {node['path']}/pgedge && ./pgedge set BACKUP restore_path {restore_path}"
            run_cmd(cmd_set_restore_path, node=node, message=f"Setting BACKUP restore_path to {restore_path}", verbose=verbose)
    
            # (c) Set BACKUP repo1-host-user to the OS user (default: postgres)
            os_user = node.get("os_user", "postgres")
            cmd_set_repo1_host_user = f"cd {node['path']}/pgedge && ./pgedge set BACKUP repo1-host-user {os_user}"
            run_cmd(cmd_set_repo1_host_user, node=node, message=f"Setting BACKUP repo1-host-user to {os_user} on node '{node['name']}'", verbose=verbose)
    
            # (d) Set BACKUP pg1-path to the PostgreSQL data directory
            cmd_set_pg1_path = f"cd {node['path']}/pgedge && ./pgedge set BACKUP pg1-path {pg1_path}"
            run_cmd(cmd_set_pg1_path, node=node, message=f"Setting BACKUP pg1-path to {pg1_path} on node '{node['name']}'", verbose=verbose)
    
            # (e) Set BACKUP pg1-user to the OS user
            cmd_set_pg1_user = f"cd {node['path']}/pgedge && ./pgedge set BACKUP pg1-user {os_user}"
            run_cmd(cmd_set_pg1_user, node=node, message=f"Setting BACKUP pg1-user to {os_user} on node '{node['name']}'", verbose=verbose)
    
            # (f) Set BACKUP pg1-port to the node's port value
            cmd_set_pg1_port = f"cd {node['path']}/pgedge && ./pgedge set BACKUP pg1-port {port}"
            run_cmd(cmd_set_pg1_port, node=node, message=f"Setting BACKUP pg1-port to {port} on node '{node['name']}'", verbose=verbose)
    
            # -- Step 7: Create the pgBackRest stanza (this command uses --pg1-port because it connects to the DB)
            cmd_create_stanza = (
                f"cd {node['path']}/pgedge && "
                f"./pgedge backrest command stanza-create "
                f"--stanza '{stanza}' "
                f"--pg1-path '{pg1_path}' "
                f"--repo1-cipher-type {repo1_cipher_type} "
                f"--pg1-port {port} "
                f"--repo1-path {repo1_path}"
            )
            run_cmd(cmd_create_stanza, node=node, message=f"Creating pgBackRest stanza '{stanza}'", verbose=verbose)
    
            # -- Step 8: Initiate a full backup using pgBackRest (again, passing the port)
            backrest_backup_args = (
                f"--repo1-path {repo1_path} "
                f"--stanza {stanza} "
                f"--pg1-path {pg1_path} "
                f"--repo1-type {repo1_type} "
                f"--log-level-console {log_level_console} "
                f"--pg1-port {port} "
                f"--db-socket-path /tmp "
                f"--repo1-cipher-type {repo1_cipher_type} "
                f"--repo1-retention-full {repo1_retention_full} "
                f"--type=full"
            )
            cmd_create_backup = f"cd {node['path']}/pgedge && ./pgedge backrest command backup '{backrest_backup_args}'"
            run_cmd(cmd_create_backup, node=node, message="Creating full pgBackRest backup", verbose=verbose)
                    # (f) Set BACKUP pg1-port to the node's port value
            cmd_set_pg1_port = f"cd {node['path']}/pgedge && ./pgedge set BACKUP repo1-path {repo1_path}"
            run_cmd(cmd_set_pg1_port, node=node, message=f"Setting BACKUP repo1-path to {repo1_path} on node '{node['name']}'", verbose=verbose)
    
    # 7. If it's an HA cluster, handle Patroni/etcd, etc.
    if is_ha_cluster:
        pg_ver = db_settings["pg_version"]
        for node in nodes:
            if "sub_nodes" in node and node["sub_nodes"]:
                sub_nodes = node["sub_nodes"]
                # Stop and clean sub-nodes
                for n in sub_nodes:
                    manage_node(n, "stop", f"pg{pg_ver}", verbose)
                    pgdata = f"{n['path']}/pgedge/data/pg{pg_ver}"
                    cmd = f"rm -rf {pgdata}"
                    message = f"Removing old data directory on {n['name']}"
                    run_cmd(cmd, n, message=message, verbose=verbose)
                # Configure etcd and Patroni
                etcd.configure_etcd(node, sub_nodes)
                ha_patroni.configure_patroni(node, sub_nodes, db[0], db_settings)


def check_source_backrest_config(source_node_data):
    """
    Check the source node's JSON data for a pgBackRest configuration.
    If a non‑empty 'backrest' block is found, display its configuration.
    Otherwise, display a message that no pgBackRest configuration exists,
    and remove any leftover pgBackRest configuration.
    """
    if "backrest" in source_node_data and source_node_data["backrest"]:
        util.message(
            f"Source node '{source_node_data['name']}' already has pgBackRest configuration: {source_node_data['backrest']}",
            "info"
        )
    else:

        cmd = f"cd {source_node_data['path']}/pgedge && ./pgedge remove backrest"
        run_cmd(cmd, node=source_node_data, message="Removing pgBackRest configuration from source node", verbose=True)


def add_node(
    cluster_name,
    source_node,
    target_node,
    repo1_path=None,
    backup_id=None,
    script=" ",
    install=True,
):
    """
    Adds a new node to a cluster, copying configurations from a specified
    source node.

    Args:
        cluster_name (str): The name of the cluster to which the node is being
                            added.
        source_node (str): The node from which configurations are copied.
        target_node (str): The new node.
        repo1_path (str): The repo1 path to use.
        backup_id (str): Backup ID.
        script (str): Bash script.
    """
    db, db_settings, nodes = load_json(cluster_name)

    cluster_data = get_cluster_json(cluster_name)
    if cluster_data is None:
        util.exit_message("Cluster data is missing.")
    pg = db_settings["pg_version"]
    pgV = f"pg{pg}"
    verbose = cluster_data.get("log_level", "info")

    # Load and validate the target node JSON
    target_node_file = f"{target_node}.json"
    if not os.path.isfile(target_node_file):
        util.exit_message(f"New node json file '{target_node_file}' not found")

    try:
        with open(target_node_file, "r") as f:
            target_node_data = json.load(f)
            json_validate_add_node(target_node_data)
    except Exception as e:
        util.exit_message(
            f"Unable to load new node json def file '{target_node_file}\n{e}"
        )

    # NEW: Check if target JSON has backrest configuration
    target_backrest_settings = target_node_data.get("backrest", {})
    # Retrieve source node data
    source_node_data = next(
        (node for node in nodes if node["name"] == source_node), None
    )
    if source_node_data is None:
        util.exit_message(f"Source node '{source_node}' not found in cluster data.")

    # Extract backrest settings from source node (before using repo1_path flag)
    backrest_settings = source_node_data.get("backrest", {})
    source_repo1_path = backrest_settings.get("repo1_path")

    # Check: if source node JSON already provides repo1_path and the flag is given then exit
    if repo1_path and source_repo1_path:
        util.exit_message(
            "Error: The source node JSON already contains a repo1_path. "
            "Do not provide the repo1_path flag when the source node has it configured."
        )

    for group in target_node_data.get("node_groups", []):
        ssh_info = group.get("ssh")
        backrest_info = group.get("backrest")
        os_user = ssh_info.get("os_user", "")
        ssh_key = ssh_info.get("private_key", "")

        new_node_data = {
            "ssh": ssh_info,
            "name": group.get("name", ""),
            "is_active": group.get("is_active", ""),
            "public_ip": group.get("public_ip", ""),
            "private_ip": group.get("private_ip", ""),
            "port": group.get("port", ""),
            "path": group.get("path", ""),
            "os_user": os_user,
            "ssh_key": ssh_key,
        }

    # If backrest settings are provided in the JSON, add them to new_node_data.
    if backrest_info:
        new_node_data["backrest"] = backrest_info
    if "public_ip" not in new_node_data and "private_ip" not in new_node_data:
        util.exit_message(
            "Both public_ip and private_ip are missing in target node data."
        )

    if "public_ip" in source_node_data and "private_ip" in source_node_data:
        source_node_data["ip_address"] = source_node_data["public_ip"]
    else:
        source_node_data["ip_address"] = source_node_data.get(
            "public_ip", source_node_data.get("private_ip")
        )

    if "public_ip" in new_node_data and "private_ip" in new_node_data:
        new_node_data["ip_address"] = new_node_data["public_ip"]
    else:
        new_node_data["ip_address"] = new_node_data.get(
            "public_ip", new_node_data.get("private_ip")
        )

    # Fetch backrest settings from the source node directory
    backrest_settings = source_node_data.get("backrest", {})
    # New check: if pgBackRest is not configured on the source node
    if not backrest_settings:
        # Step 1: Install pgBackRest on the source node
        cmd_install_backrest = (
            f"cd {source_node_data['path']}/pgedge && ./pgedge install backrest"
        )
        run_cmd(
            cmd_install_backrest,
            node=source_node_data,
            message="Installing pgBackRest",
            verbose=verbose,
        )

        util.message("## Integrating pgBackRest into the cluster", "info")
        util.message(
            f"### Configuring pgBackRest for node '{source_node_data['name']}'", "info"
        )
        # Create a unique stanza name using the cluster name and node name
        stanza_source = f"{cluster_name}_stanza_{source_node_data['name']}"

        # Load additional pgBackRest settings with defaults.
        repo1_retention_full = "7"
        log_level_console = "info"
        repo1_cipher_type = "aes-256-cbc"
        repo1_type = "posix"  # Could also be "s3"
        # Determine the repository path for the source node.
        if repo1_path:
            # Use the provided flag value as-is (trimmed of any trailing slash).
            repo1_path_source = repo1_path.rstrip("/")
        else:
            # No repo1_path flag provided: check the JSON configuration or default.
            json_repo1_path = backrest_settings.get("repo1_path")
            if json_repo1_path:
                repo1_path_source = json_repo1_path.rstrip("/")
                if not repo1_path_source.endswith(source_node_data["name"]):
                    repo1_path_source = (
                        repo1_path_source + f"/{source_node_data['name']}"
                    )
            else:
                repo1_path_source = f"/var/lib/pgbackrest/{source_node_data['name']}"

        # Similarly, set restore_path to include node name
        restore_path_source = "/var/lib/pgbackrest_restore"
        if not restore_path_source.rstrip("/").endswith(source_node_data["name"]):
            restore_path_source = (
                restore_path_source.rstrip("/") + f"/{source_node_data['name']}"
            )

        pg_version = db_settings["pg_version"]
        pg1_path_source = f"{source_node_data['path']}/pgedge/data/pg{pg_version}"
        port_source = source_node_data["port"]

        # Step 2: Configure postgresql.conf for pgBackRest (without --pg1-port)
        cmd_set_postgresqlconf_source = (
            f"cd {source_node_data['path']}/pgedge && "
            f"./pgedge backrest set_postgresqlconf "
            f"--stanza {stanza_source} "
            f"--pg1-path {pg1_path_source} "
            f"--repo1-path {repo1_path_source} "
            f"--repo1-type {repo1_type}"
        )
        run_cmd(
            cmd_set_postgresqlconf_source,
            node=source_node_data,
            message="Modifying postgresql.conf for pgBackRest",
            verbose=verbose,
        )

        # Step 3: Configure pg_hba.conf for pgBackRest (without --pg1-port)
        cmd_set_hbaconf_source = (
            f"cd {source_node_data['path']}/pgedge && ./pgedge backrest set_hbaconf"
        )
        run_cmd(
            cmd_set_hbaconf_source,
            node=source_node_data,
            message="Modifying pg_hba.conf for pgBackRest",
            verbose=verbose,
        )

        # Step 4: Reload PostgreSQL configuration to apply changes
        sql_reload_conf = "select pg_reload_conf()"
        cmd_reload_conf_source = f"cd {source_node_data['path']}/pgedge && ./pgedge psql '{sql_reload_conf}' {db[0]['db_name']}"
        run_cmd(
            cmd_reload_conf_source,
            node=source_node_data,
            message="Reloading PostgreSQL configuration",
            verbose=verbose,
        )

        # Step 5: If using S3 as repository, export necessary environment variables
        if repo1_type.lower() == "s3":
            required_env_vars = [
                "PGBACKREST_REPO1_S3_KEY",
                "PGBACKREST_REPO1_S3_BUCKET",
                "PGBACKREST_REPO1_S3_KEY_SECRET",
                "PGBACKREST_REPO1_CIPHER_PASS",
            ]
            missing_env_vars = [
                var for var in required_env_vars if var not in os.environ
            ]
            if missing_env_vars:
                util.exit_message(
                    f"Environment variables {', '.join(missing_env_vars)} must be set for S3 pgBackRest configuration.",
                    1,
                )
            s3_exports = " && ".join(
                [f"export {var}={os.environ[var]}" for var in required_env_vars]
            )
            cmd_export_s3_source = (
                f"cd {source_node_data['path']}/pgedge && {s3_exports}"
            )
            run_cmd(
                cmd_export_s3_source,
                node=source_node_data,
                message="Setting S3 environment variables for pgBackRest",
                verbose=verbose,
            )

        # Step 6: Set all pgBackRest backup configuration values for the source node.
        #
        # Build one compound shell command
        compound_cmd = " && ".join(
            [
                f"cd {source_node_data['path']}/pgedge",
                f"./pgedge set BACKUP stanza {stanza_source}",
                f"sudo mkdir -p {restore_path_source}",
                f"./pgedge set BACKUP restore_path {restore_path_source}",
                f"./pgedge set BACKUP repo1-host-user {source_node_data.get('os_user', 'postgres')}",
                f"./pgedge set BACKUP pg1-path {pg1_path_source}",
                f"./pgedge set BACKUP pg1-user {source_node_data.get('os_user', 'postgres')}",
                f"./pgedge set BACKUP pg1-port {port_source}",
            ]
        )

        # Execute once with verbose disabled
        run_cmd(
            compound_cmd,
            node=source_node_data,
            message=f"Configuring BACKUP settings on node '{source_node_data['name']}'",
            verbose=False,
        )

        # Step 7:Create the pgBackRest stanza (this command uses --pg1-port because it connects to the DB)
        cmd_create_stanza_source = (
            f"cd {source_node_data['path']}/pgedge && "
            f"./pgedge backrest command stanza-create "
            f"--stanza '{stanza_source}' "
            f"--pg1-path '{pg1_path_source}' "
            f"--repo1-cipher-type {repo1_cipher_type} "
            f"--pg1-port {port_source} "
            f"--repo1-path {repo1_path_source}"
        )
        run_cmd(
            cmd_create_stanza_source,
            node=source_node_data,
            message=f"Creating pgBackRest stanza '{stanza_source}'",
            verbose=verbose,
        )
        # Step 8: Initiate a full backup using pgBackRest (again, passing the port)
        backrest_backup_args_source = (
            f"--repo1-path {repo1_path_source} "
            f"--stanza {stanza_source} "
            f"--pg1-path {pg1_path_source} "
            f"--repo1-type {repo1_type} "
            f"--log-level-console {log_level_console} "
            f"--pg1-port {port_source} "
            f"--db-socket-path /tmp "
            f"--repo1-cipher-type {repo1_cipher_type} "
            f"--repo1-retention-full {repo1_retention_full} "
            f"--type=full"
        )
        cmd_create_backup_source = f"cd {source_node_data['path']}/pgedge && ./pgedge backrest command backup '{backrest_backup_args_source}'"
        run_cmd(
            cmd_create_backup_source,
            node=source_node_data,
            message="Creating full pgBackRest backup",
            verbose=verbose,
        )
        # (i) (Optional) Reset BACKUP repo1-path if needed
        cmd_set_repo1_path_source = f"cd {source_node_data['path']}/pgedge && ./pgedge set BACKUP repo1-path {repo1_path_source}"
        run_cmd(
            cmd_set_repo1_path_source,
            node=source_node_data,
            message=f"Setting BACKUP repo1-path to {repo1_path_source} on node '{source_node_data['name']}'",
            verbose=verbose,
        )

        # Update pgbackrest_settings for further use downstream.
        backrest_settings = {
            "stanza": stanza_source,
            "repo1_path": repo1_path_source,
            "repo1-retention-full": repo1_retention_full,
            "log-level-console": log_level_console,
            "repo1-cipher-type": repo1_cipher_type,
            "repo1_type": repo1_type,
        }

    # NEW: Override pgbackrest settings with target JSON settings if present
    if target_backrest_settings:
        backrest_settings = target_backrest_settings

    # For subsequent steps we extract settings from pgbackrest_settings.
    stanza = backrest_settings.get("stanza", f"pg{pg}")
    repo1_retention_full = backrest_settings.get("repo1-retention-full", "7")
    log_level_console = backrest_settings.get("log-level-console", "info")
    repo1_cipher_type = backrest_settings.get("repo1-cipher-type", "aes-256-cbc")
    repo1_type = backrest_settings.get("repo1_type", "posix")

    rc = ssh_install_pgedge(
        cluster_name,
        db[0]["db_name"],
        db_settings,
        db[0]["db_user"],
        db[0]["db_password"],
        [new_node_data],
        install,
        verbose,
    )

    os_user = new_node_data["os_user"]
    port = source_node_data["port"]
    pg1_path = f"{source_node_data['path']}/pgedge/data/pg{pg}"

    if not repo1_path:
        # Do not install pgbackrest on source node; simply fetch the repo1_path from source's settings.
        repo1_path_default = f"/var/lib/pgbackrest/{source_node_data['name']}"
        repo1_path = backrest_settings.get("repo1_path", f"{repo1_path_default}")
    else:
        cmd = (
            f"{source_node_data['path']}/pgedge/pgedge backrest set_postgresqlconf {stanza} "
            f"{pg1_path} {repo1_path} {repo1_type}"
        )
        message = f"Modifying postgresql.conf file"
        run_cmd(cmd, source_node_data, message=message, verbose=verbose)

        cmd = f"{source_node_data['path']}/pgedge/pgedge backrest set_hbaconf"
        message = f"Modifying pg_hba.conf file"
        run_cmd(cmd, source_node_data, message=message, verbose=verbose)

        sql_cmd = "select pg_reload_conf()"
        cmd = f"{source_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {db[0]['db_name']}"
        message = f"Reload configuration pg_reload_conf()"
        run_cmd(cmd, source_node_data, message=message, verbose=verbose)

        if repo1_type == "s3":
            for env_var in [
                "PGBACKREST_REPO1_S3_KEY",
                "PGBACKREST_REPO1_S3_BUCKET",
                "PGBACKREST_REPO1_S3_KEY_SECRET",
                "PGBACKREST_REPO1_CIPHER_PASS",
            ]:
                if env_var not in os.environ:
                    util.exit_message(f"Environment variable {env_var} not set.")
            s3_export_cmds = [
                f"export {env_var}={os.environ[env_var]}"
                for env_var in [
                    "PGBACKREST_REPO1_S3_KEY",
                    "PGBACKREST_REPO1_S3_BUCKET",
                    "PGBACKREST_REPO1_S3_KEY_SECRET",
                    "PGBACKREST_REPO1_CIPHER_PASS",
                ]
            ]
            run_cmd(
                " && ".join(s3_export_cmds),
                source_node_data,
                message="Setting S3 environment variables on source node",
                verbose=verbose,
            )
            run_cmd(
                " && ".join(s3_export_cmds),
                new_node_data,
                message="Setting S3 environment variables on target node",
                verbose=verbose,
            )

    cmd = f"{new_node_data['path']}/pgedge/pgedge install backrest"
    message = f"Installing pgbackrest"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    manage_node(new_node_data, "stop", f"pg{pg}", verbose)
    cmd = f'rm -rf {new_node_data["path"]}/pgedge/data/pg{pg}'
    message = f"Removing old data directory"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    args = f"--repo1-path {repo1_path} --repo1-cipher-type {repo1_cipher_type} "
    if backup_id:
        args += f"--set={backup_id} "

    cmd = (
        f'{new_node_data["path"]}/pgedge/pgedge backrest command restore '
        f"--repo1-type={repo1_type} --stanza={stanza} "
        f'--pg1-path={new_node_data["path"]}/pgedge/data/pg{pg} {args}'
    )
    message = f"Restoring backup"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    pgd = f'{new_node_data["path"]}/pgedge/data/pg{pg}'
    pgc = f"{pgd}/postgresql.conf"

    cmd = f"echo \"ssl_cert_file='{pgd}/server.crt'\" >> {pgc}"
    message = f"Setting ssl_cert_file"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    cmd = f"echo \"ssl_key_file='{pgd}/server.key'\" >> {pgc}"
    message = f"Setting ssl_key_file"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    cmd = f"echo \"log_directory='{pgd}/log'\" >> {pgc}"
    message = f"Setting log_directory"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    cmd = (
        f'echo "shared_preload_libraries = '
        f"'pg_stat_statements, snowflake, spock'\" >> {pgc}"
    )
    message = f"Setting shared_preload_libraries"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    cmd = (
        f'{new_node_data["path"]}/pgedge/pgedge backrest configure_replica {stanza} '
        f'{new_node_data["path"]}/pgedge/data/pg{pg} {source_node_data["ip_address"]} '
        f'{source_node_data["port"]} {source_node_data["os_user"]}'
    )
    message = f"Configuring PITR on replica"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    if script.strip() and os.path.isfile(script):
        util.echo_cmd(f"{script}")

    terminate_cluster_transactions(nodes, db[0]["db_name"], f"pg{pg}", verbose)

    spock = db_settings["spock_version"]
    v4 = True
    spock_maj = 4
    if spock:
        ver = [int(x) for x in spock.split(".")]
        spock_maj = ver[0]
        spock_min = ver[1]
        if spock_maj >= 4:
            v4 = True

    set_cluster_readonly(nodes, True, db[0]["db_name"], f"pg{pg}", v4, verbose)
    manage_node(new_node_data, "start", f"pg{pg}", verbose)
    time.sleep(5)

    check_cluster_lag(new_node_data, db[0]["db_name"], f"pg{pg}", verbose)

    sql_cmd = "SELECT pg_promote()"
    cmd = f"{new_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {db[0]['db_name']}"
    message = f"Promoting standby to primary"
    run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    for mdb in db:
        sql_cmd = "SELECT sub_name FROM spock.subscription"
        cmd = f"{new_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {mdb['db_name']}"
        message = "Fetch existing subscriptions"
        result = run_cmd(
            cmd,
            node=new_node_data,
            message=message,
            verbose=verbose,
            capture_output=True,
        )

        subscriptions = [
            re.sub(r"\x1b\[[0-9;]*m", "", line.strip())
            for line in result.stdout.splitlines()[2:]
            if line.strip() and not line.strip().startswith("(")
        ]
        subscriptions = [sub for sub in subscriptions if sub]

        if subscriptions:
            for sub_name in subscriptions:
                cmd = f"{new_node_data['path']}/pgedge/pgedge spock sub-drop {sub_name} {mdb['db_name']}"
                message = f"Dropping old subscription {sub_name}"
                run_cmd(cmd, node=new_node_data, message=message, verbose=verbose)
        else:
            print("No subscriptions to drop.")

        sql_cmd = "SELECT node_name FROM spock.node"
        cmd = f"{new_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {mdb['db_name']}"
        message = "Check if there are nodes"
        result = run_cmd(
            cmd,
            node=new_node_data,
            message=message,
            verbose=verbose,
            capture_output=True,
        )

        print(f"\nRaw output:\n{result.stdout}")
        nodes_list = [
            re.sub(r"\x1b\[[0-9;]*m", "", line.strip())
            for line in result.stdout.splitlines()[2:]
            if line.strip() and not line.strip().startswith("(")
        ]
        nodes_list = [node for node in nodes_list if node]

        if nodes_list:
            for node_name in nodes_list:
                cmd = f"{new_node_data['path']}/pgedge/pgedge spock node-drop {node_name} {mdb['db_name']}"
                message = f"Dropping node {node_name}"
                run_cmd(cmd, node=new_node_data, message=message, verbose=verbose)
        else:
            print("No nodes to drop.")

        create_node(new_node_data, mdb["db_name"], verbose)

        if not v4:
            set_cluster_readonly(nodes, False, mdb["db_name"], f"pg{pg}", v4, verbose)

        create_sub(nodes, new_node_data, mdb["db_name"], verbose)
        create_sub_new(nodes, new_node_data, mdb["db_name"], verbose)

        nc = os.path.join(new_node_data["path"], "pgedge", "pgedge ")
        cmd = f'{nc} spock repset-add-table default "*" {mdb["db_name"]}'
        message = f"Adding all tables to repset"
        run_cmd(cmd, new_node_data, message=message, verbose=verbose)

        cmd = f'{nc} spock repset-add-table default_insert_only "*" {mdb["db_name"]}'
        run_cmd(cmd, new_node_data, message=message, verbose=verbose)

    if v4:
        set_cluster_readonly(nodes, False, db[0]["db_name"], f"pg{pg}", v4, verbose)

    cmd = f'cd {new_node_data["path"]}/pgedge/; ./pgedge spock node-list {db[0]["db_name"]}'
    message = f"Listing spock nodes"
    result = run_cmd(
        cmd, node=new_node_data, message=message, verbose=verbose, capture_output=True
    )
    print(f"\n{result.stdout}")

    sql_cmd = "select node_id,node_name from spock.node"
    cmd = (
        f"{source_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {db[0]['db_name']}"
    )
    message = f"List nodes"
    result = run_cmd(
        cmd,
        node=source_node_data,
        message=message,
        verbose=verbose,
        capture_output=True,
    )
    print(f"\n{result.stdout}")

    for node in nodes:
        sql_cmd = (
            "select sub_id,sub_name,sub_enabled,sub_slot_name,"
            "sub_replication_sets from spock.subscription"
        )
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {db[0]['db_name']}"
        message = f"List subscriptions"
        result = run_cmd(
            cmd, node=node, message=message, verbose=verbose, capture_output=True
        )
        print(f"\n{result.stdout}")

    sql_cmd = (
        "select sub_id,sub_name,sub_enabled,sub_slot_name,"
        "sub_replication_sets from spock.subscription"
    )
    cmd = f"{new_node_data['path']}/pgedge/pgedge psql '{sql_cmd}' {db[0]['db_name']}"
    message = f"List subscriptions"
    result = run_cmd(
        cmd, node=new_node_data, message=message, verbose=verbose, capture_output=True
    )
    print(f"\n{result.stdout}")

    # Reload the complete target JSON file and fetch repo1_path and stanza from its pgbackrest settings.
    try:
        with open(target_node_file, "r") as f:
            complete_target_json = json.load(f)

        # Since pgbackrest settings are stored inside each node group, fetch from the first node group.
        if (
            "node_groups" in complete_target_json
            and complete_target_json["node_groups"]
        ):
            repo1_path_target_file = (
                complete_target_json["node_groups"][0]
                .get("backrest", {})
                .get("repo1_path")
            )
            target_stanza_target_file = (
                complete_target_json["node_groups"][0].get("backrest", {}).get("stanza")
            )

            pgedge_dir = f"{new_node_data['path']}/pgedge"
            restore_path = backrest_settings.get(
                "restore_path", f"/var/lib/pgbackrest_restore/{new_node_data['name']}"
            )
            target_repo1_host_user = backrest_settings.get(
                "repo1_host_user", new_node_data.get("os_user", "postgres")
            )
            target_pg1_path = backrest_settings.get(
                "pg1_path", f"{pgedge_dir}/data/pg{pg}"
            )
            target_pg1_user = backrest_settings.get(
                "pg1_user", new_node_data.get("os_user", "postgres")
            )
            target_pg1_port = backrest_settings.get(
                "pg1_port", new_node_data.get("port", "6435")
            )

            # ---------------------------------------------------------------
            # If the repo1_path or stanza is missing, remove backrest instead
            # ---------------------------------------------------------------
            if not repo1_path_target_file or not target_stanza_target_file:
                # No valid repo1_path or stanza -> remove backrest
                repo1_path_target_file = None
                target_stanza_target_file = None

                cmd_remove_backrest_target = (
                    f"cd {pgedge_dir} && ./pgedge remove backrest"
                )
                run_cmd(
                    cmd=cmd_remove_backrest_target,
                    node=new_node_data,
                    message="Removing backrest",
                    verbose=verbose,
                )
            else:
                # Both repo1_path_target_file and target_stanza_target_file exist
                target_repo1_path = repo1_path_target_file
                target_stanza = target_stanza_target_file

                # Combined target node BACKUP configuration commands
                combined_target_cmd = (
                    f"sudo mkdir -p {restore_path} && "
                    f"sudo chown -R {target_repo1_host_user}:{target_repo1_host_user} {restore_path} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP restore_path {restore_path} && "
                    f"sudo mkdir -p {target_repo1_path} && "
                    f"sudo chown -R {target_repo1_host_user}:{target_repo1_host_user} {target_repo1_path} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP repo1-path {target_repo1_path} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP repo1-host-user {target_repo1_host_user} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP pg1-path {target_pg1_path} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP pg1-user {target_pg1_user} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP pg1-port {target_pg1_port} && "
                    f"cd {pgedge_dir} && ./pgedge set BACKUP stanza {target_stanza}"
                )
                run_cmd(
                    cmd=combined_target_cmd,
                    node=new_node_data,
                    message="Setting all target node BACKUP configuration",
                    verbose=False,
                )

                # Append the BACKUP settings to the target's PostgreSQL configuration
                cmd_set_postgresqlconf_target = (
                    f"cd {pgedge_dir} && ./pgedge backrest set_postgresqlconf "
                    f"{target_stanza} {target_pg1_path} {target_repo1_path} {repo1_type}"
                )
                run_cmd(
                    cmd=cmd_set_postgresqlconf_target,
                    node=new_node_data,
                    message="Appending BACKUP settings to postgresql.conf for target node",
                    verbose=verbose,
                )

                # Restart PostgreSQL to apply the new configuration
                cmd_restart_postgres = f"cd {pgedge_dir} && ./pgedge restart"
                run_cmd(
                    cmd=cmd_restart_postgres,
                    node=new_node_data,
                    message="Restarting PostgreSQL service",
                    verbose=verbose,
                )

                # Now create the pgBackRest stanza on the target node
                cmd_create_stanza_target = (
                    f"cd {pgedge_dir} && "
                    f"./pgedge backrest command stanza-create "
                    f"--stanza '{target_stanza}' "
                    f"--pg1-path '{target_pg1_path}' "
                    f"--repo1-cipher-type {repo1_cipher_type} "
                    f"--pg1-port {target_pg1_port} "
                    f"--repo1-path {target_repo1_path}"
                )
                run_cmd(
                    cmd=cmd_create_stanza_target,
                    node=new_node_data,
                    message=f"Creating pgBackRest stanza '{target_stanza}'",
                    verbose=verbose,
                )

                # Create a full backup using pgBackRest
                backrest_backup_args_target = (
                    f"--repo1-path {target_repo1_path} "
                    f"--stanza {target_stanza} "
                    f"--pg1-path {target_pg1_path} "
                    f"--repo1-type {repo1_type} "
                    f"--log-level-console {log_level_console} "
                    f"--pg1-port {target_pg1_port} "
                    f"--db-socket-path /tmp "
                    f"--repo1-cipher-type {repo1_cipher_type} "
                    f"--repo1-retention-full {repo1_retention_full} "
                    f"--type=full"
                )
                cmd_create_backup_target = (
                    f"cd {pgedge_dir} && ./pgedge backrest command backup "
                    f"'{backrest_backup_args_target}'"
                )
                run_cmd(
                    cmd=cmd_create_backup_target,
                    node=new_node_data,
                    message="Creating full pgBackRest backup",
                    verbose=verbose,
                )
        else:
            # If no node_groups exist at all, remove pgbackrest
            repo1_path_target_file = None
            target_stanza_target_file = None

            pgedge_dir = f"{new_node_data['path']}/pgedge"
            cmd_remove_backrest_target = f"cd {pgedge_dir} && ./pgedge remove backrest"
            run_cmd(
                cmd=cmd_remove_backrest_target,
                node=new_node_data,
                message="Removing backrest",
                verbose=verbose,
            )

    except Exception as e:
        print(f"Error fetching values from target JSON file: {e}")

    # NEW: Check and display pgBackRest configuration status in the source node
    # Remove unnecessary keys before appending new node to the cluster data
    new_node_data.pop("ip_address", None)
    new_node_data.pop("os_user", None)
    new_node_data.pop("ssh_key", None)

    # Append new node data to the cluster JSON
    cluster_data["node_groups"].append(new_node_data)
    cluster_data["update_date"] = datetime.datetime.now().astimezone().isoformat()

    write_cluster_json(cluster_name, cluster_data)

    check_source_backrest_config(source_node_data)


def cleanup_backrest_from_cluster(cluster_json, target_json):
    """
    Compare the node groups in the target JSON with the cluster JSON.
    For each node in cluster_json["node_groups"], if the corresponding node (by name)
    is not present in target_json's node groups or does not contain a "backrest" key,
    then remove the "backrest" key from that node in cluster_json.
    
    Args:
        cluster_json (dict): The main cluster configuration.
        target_json (dict): The target node configuration JSON.
    """
    # Create a mapping of node names to their configuration from the target JSON.
    target_nodes = {group.get("name"): group for group in target_json.get("node_groups", [])}
    
    for node in cluster_json.get("node_groups", []):
        node_name = node.get("name")
        target_group = target_nodes.get(node_name)
        # If the target group does not exist or does not contain a backrest key, delete backrest in the main config.
        if not target_group or "backrest" not in target_group:
            if "backrest" in node:
                del node["backrest"]

def json_validate_add_node(data):
    """
    Validate the structure of a node‑definition JSON file that will be fed to
    the add‑node command.

    • The traditional checks (json_version, ssh, port, …) still apply.
    • A node_group is not required to have a “backrest” block.
    • If a “backrest” block is present, it must contain at least:
         • stanza        – unique stanza name
         • repo1_path    – absolute path to the repo directory
         • repo1_type    – 'posix' or 's3'
       and the values must be non‑empty and valid.
    """

    required_top = {"json_version", "node_groups"}
    if not required_top.issubset(data):
        util.exit_message("Invalid add‑node JSON: missing json_version or node_groups.")

    if str(data.get("json_version")) != "1.0":
        util.exit_message("Invalid or unsupported json_version (must be '1.0').")

    node_group_required = {
        "ssh",
        "name",
        "is_active",
        "public_ip",
        "private_ip",
        "port",
        "path",
    }
    ssh_required = {"os_user", "private_key"}

    backrest_required = {"stanza", "repo1_path", "repo1_type"}
    valid_repo1_types = {"posix", "s3"}

    for group in data["node_groups"]:
        gname = group.get("name", "?")

        # --- basic mandatory keys
        missing_basic = node_group_required - set(group.keys())
        if missing_basic:
            util.exit_message(
                f"Node‑group '{gname}' missing keys: {', '.join(missing_basic)}"
            )

        # ssh block
        ssh_info = group["ssh"]
        missing_ssh = ssh_required - set(ssh_info.keys())
        if missing_ssh:
            util.exit_message(
                f"SSH block in node‑group '{gname}' missing: {', '.join(missing_ssh)}"
            )

        # backrest (optional but validated if present)
        if "backrest" in group and group["backrest"] is not None:
            br = group["backrest"]

            # ensure required keys are present
            missing_br = backrest_required - set(br.keys())
            if missing_br:
                util.exit_message(
                    f"pgBackRest block in node‑group '{gname}' missing: {', '.join(missing_br)}"
                )

            # ensure values are non‑empty
            for k in backrest_required:
                if not str(br[k]).strip():
                    util.exit_message(
                        f"pgBackRest key '{k}' in node‑group '{gname}' cannot be empty."
                    )

            # verify repo1_type is valid
            if br["repo1_type"] not in valid_repo1_types:
                util.exit_message(
                    f"Invalid repo1_type '{br['repo1_type']}' in node‑group '{gname}'. "
                    f"Allowed: {', '.join(valid_repo1_types)}"
                )

    util.message("✔ add‑node JSON structure is valid.", "success")

def remove_node(cluster_name, node_name):
    """Remove a node from the cluster configuration.

       Now also checks for multiple databases on the node, and drops all
       subscriptions/Spock extension across each database before removal.
    """
    json_validate(cluster_name)
    db, db_settings, nodes = load_json(cluster_name)
    cluster_data = get_cluster_json(cluster_name)
    if cluster_data is None:
        util.exit_message("Cluster data is missing.")

    pg = db_settings["pg_version"]
    pgV = f"pg{pg}"

    # Keep the original single-db variable (do not remove/change)
    dbname = db[0]["db_name"]
    verbose = cluster_data.get("log_level", "info")

    #
    # 1. Verify SSH connectivity on all nodes
    #
    for node in nodes:
        os_user = node["os_user"]
        ssh_key = node["ssh_key"]
        message = f"Checking ssh on {node['public_ip']}"
        cmd = "hostname"
        run_cmd(cmd, node, message=message, verbose=verbose)

    #
    # 2. On OTHER nodes (not being removed), drop any subscriptions that point TO the node being removed
    #
    for node in nodes:
        if node.get("name") != node_name:
            for db_item in db:
                sub_db = db_item["db_name"]
                # Subscription name: sub_{thisNode}{removedNode}
                sub_name = f"sub_{node['name']}{node_name}"
                cmd = (
                    f"cd {node['path']}/pgedge/; "
                    f"./pgedge spock sub-drop {sub_name} {sub_db}"
                )
                message = f"Dropping subscription {sub_name} on database {sub_db}"
                run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)

    #
    # 3. Collect subscription names that *originate from* the node being removed:
    #    sub_{removedNode}{otherNode}
    #
    sub_names = []
    for n in nodes:
        if n.get("name") != node_name:
            sub_name = f"sub_{node_name}{n['name']}"
            sub_names.append(sub_name)

    #
    # 4. On the node being removed:
    #    - Drop all subscriptions that point *from* this node to the other nodes
    #    - Drop the node itself for each DB
    #    - Remove the Spock extension from every database (via DROP EXTENSION spock CASCADE)
    #
    for node in nodes:
        if node.get("name") == node_name:
            # a) Drop all subscriptions from the node being removed
            for db_item in db:
                sub_db = db_item["db_name"]
                for s_name in sub_names:
                    cmd = (
                        f"cd {node['path']}/pgedge/; "
                        f"./pgedge spock sub-drop {s_name} {sub_db}"
                    )
                    message = f"Dropping subscription {s_name} on database {sub_db}"
                    run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)

            # b) Drop the node itself in each database
            for db_item in db:
                sub_db = db_item["db_name"]
                cmd = (
                    f"cd {node['path']}/pgedge/; "
                    f"./pgedge spock node-drop {node['name']} {sub_db}"
                )
                message = f"Dropping node {node['name']} from database {sub_db}"
                run_cmd(cmd, node, message=message, verbose=verbose, ignore=True)

            # c) Remove the Spock extension from each database on the node being removed
            for db_item in db:
                sub_db = db_item["db_name"]
                # Use psql to directly DROP EXTENSION spock CASCADE
                ext_cmd = (
                    f"cd {node['path']}/pgedge/; "
                    f"./pgedge psql -d {sub_db} -c 'DROP EXTENSION spock CASCADE'"
                )
                ext_message = f"Dropping spock extension from database {sub_db}"
                run_cmd(ext_cmd, node, message=ext_message, verbose=verbose, ignore=True)

    #
    # 5. Stop the node being removed; on other nodes, list the spock nodes for each DB
    #
    for node in nodes:
        if node.get("name") == node_name:
            manage_node(node, "stop", pgV, verbose)
        else:
            for db_item in db:
                sub_db = db_item["db_name"]
                cmd = f'cd {node["path"]}/pgedge/; ./pgedge spock node-list {sub_db}'
                message = f"Listing spock nodes in database {sub_db}"
                result = run_cmd(
                    cmd, node=node, message=message, verbose=verbose, capture_output=True
                )
                print(f"\n{result.stdout}")

    #
    # 6. Remove node references from the cluster configuration
    #
    empty_groups = []
    for group in cluster_data["node_groups"]:
        # If the entire group name matches node_name, remove the group altogether
        if group["name"] == node_name:
            cluster_data["node_groups"].remove(group)
            continue
        # Otherwise, remove from sub_nodes if found
        for sub_node in group.get("sub_nodes", []):
            if sub_node["name"] == node_name:
                group["sub_nodes"].remove(sub_node)
        # Collect empty groups to remove them
        if not group.get("sub_nodes") and group["name"] == node_name:
            empty_groups.append(group)

    for group in empty_groups:
        cluster_data["node_groups"].remove(group)

    write_cluster_json(cluster_name, cluster_data)


def manage_node(node, action, pgV, verbose):
    """
    Starts or stops a cluster based on the provided action.
    """
    if action not in ["start", "stop"]:
        raise ValueError("Invalid action. Use 'start' or 'stop'.")

    action_message = "Starting" if action == "start" else "Stopping"

    if action == "start":
        cmd = (
            f"cd {node['path']}/pgedge/; "
            f"./pgedge config {pgV} --port={node['port']}; "
            f"./pgedge start;"
        )
    else:
        cmd = f"cd {node['path']}/pgedge/; " f"./pgedge stop"

    message = f"{action_message} new node"
    run_cmd(cmd, node, message=message, verbose=verbose)


def create_node(node, dbname, verbose):
    """
    Creates a new node in the database cluster.
    """
    ip = node["public_ip"] if "public_ip" in node else node["private_ip"]
    if not ip:
        util.exit_message(f"Node '{node['name']}' does not have a valid IP address.")

    cmd = (
        f"cd {node['path']}/pgedge/; "
        f"./pgedge spock node-create {node['name']} "
        f"'host={ip} user={node['os_user']} dbname={dbname} "
        f"port={node['port']}' {dbname}"
    )
    message = f"Creating new node {node['name']}"
    run_cmd(cmd, node, message=message, verbose=verbose)


def create_sub_new(nodes, n, dbname, verbose):
    """
    Creates subscriptions for each node to a new node in the cluster.
    """
    for node in nodes:
        sub_name = f"sub_{n['name']}{node['name']}"
        ip = node["public_ip"] if "public_ip" in node else node["private_ip"]
        if not ip:
            util.exit_message(
                f"Node '{node['name']}' does not have a valid IP address."
            )
        cmd = (
            f"cd {n['path']}/pgedge/; "
            f"./pgedge spock sub-create {sub_name} "
            f"'host={ip} user={node['os_user']} dbname={dbname} "
            f"port={node['port']}' {dbname}"
        )
        message = f"Creating new subscriptions {sub_name}"
        run_cmd(cmd=cmd, node=n, message=message, verbose=verbose)


def create_sub(nodes, new_node, dbname, verbose):
    """
    Creates subscriptions for each node to a new node in the cluster.
    """
    for n in nodes:
        sub_name = f"sub_{n['name']}{new_node['name']}"
        ip = (
            new_node["public_ip"] if "public_ip" in new_node else new_node["private_ip"]
        )
        if not ip:
            util.exit_message(
                f"Node '{new_node['name']}' does not have a valid IP address."
            )
        cmd = (
            f"cd {n['path']}/pgedge/; "
            f"./pgedge spock sub-create {sub_name} "
            f"'host={ip} user={new_node['os_user']} dbname={dbname} "
            f"port={new_node['port']}' {dbname}"
        )
        message = f"Creating subscriptions {sub_name}"
        run_cmd(cmd=cmd, node=n, message=message, verbose=verbose)


def terminate_cluster_transactions(nodes, dbname, stanza, verbose):
    sql_cmd = "SELECT spock.terminate_active_transactions()"
    for node in nodes:
        cmd = f"{node['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"Terminating·cluster·transactions"
        result = run_cmd(
            cmd=cmd, node=node, message=message, verbose=verbose, capture_output=True
        )


def extract_psql_value(psql_output: str, alias: str) -> str:
    lines = psql_output.split("\n")
    if len(lines) < 3:
        return ""
    header_line = lines[0]
    headers = [header.strip() for header in header_line.split("|")]

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
        columns = [column.strip() for column in line.split("|")]
        if len(columns) > alias_index:
            return columns[alias_index]

    return ""


def set_cluster_readonly(nodes, readonly, dbname, stanza, v4, verbose):
    """Set the cluster to readonly mode."""
    action = "Setting" if readonly else "Removing"

    if v4:
        sql_cmd = (
            'ALTER SYSTEM SET spock.readonly TO \\\\"all\\\\"'
            if readonly
            else 'ALTER SYSTEM SET spock.readonly TO \\\\"off\\\\"'
        )
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
        func_call = (
            "spock.set_cluster_readonly()"
            if readonly
            else "spock.unset_cluster_readonly()"
        )

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

        time.sleep(2)
        cmd = f"{n['path']}/pgedge/pgedge psql '{sql_cmd}' {dbname}"
        message = f"Checking lag time of new cluster"
        result = run_cmd(
            cmd=cmd, node=n, message=message, verbose=verbose, capture_output=True
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
        message = "Checking wal receiver"
        result = run_cmd(
            cmd=cmd, node=n, message=message, verbose=verbose, capture_output=True
        )
        time.sleep(interval)
        lag_bytes = int(extract_psql_value(result.stdout, "total_all_flushed"))


def replication_all_tables(cluster_name, database_name=None):
    """Add all tables in the database to replication on every node."""
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["db_name"]
    else:
        for i in db:
            if i["db_name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")

    if "auto_ddl" in db_settings:
        if db_settings["auto_ddl"] == "on":
            util.exit_message(f"Auto DDL enabled for db {database_name}")

    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["public_ip"]
        os_user = n["os_user"]
        ssh_key = n["ssh_key"]
        cmd = f"{nc} spock repset-add-table default '*' {db_name}"
        util.echo_cmd(cmd, host=ndip, usr=os_user, key=ssh_key)


def replication_check(cluster_name, show_spock_tables=False, database_name=None):
    """Print replication status on every node"""
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["db_name"]
    else:
        for i in db:
            if i["db_name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    for n in nodes:
        ndpath = n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = n["public_ip"]
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

    db, db_settings, nodes = load_json(cluster_name)
    rc = 0
    knt = 0
    for nd in nodes:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            rc = util.echo_cmd(
                nd["path"] + os.sep + "pgedge" + os.sep + "pgedge " + cmd,
                host=nd["public_ip"],
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
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["db_name"]
    else:
        for i in db:
            if i["db_name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    ctl = os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["public_ip"]
            util.echo_cmd(
                f"{ndpath}{ctl} app pgbench-install {db_name} {factor} default",
                host=ndip,
                usr=n["os_user"],
                key=n["ssh_key"],
            )
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["public_ip"]
            util.echo_cmd(
                f"{ndpath}{ctl} app northwind-install {db_name} default",
                host=ndip,
                usr=n["os_user"],
                key=n["ssh_key"],
            )
    else:
        util.exit_message(f"Invalid app_name '{app_name}'.")


def ssh_un_cross_wire(cluster_name, db, db_settings, db_user, db_passwd, nodes):
    """Create nodes and subs on every node in a cluster."""
    sub_array = []
    for prov_n in nodes:
        ndnm = prov_n["name"]
        ndpath = prov_n["path"]
        nc = ndpath + os.sep + "pgedge" + os.sep + "pgedge"
        ndip = prov_n["public_ip"]
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
        ndip = prov_n["public_ip"]
        os_user = prov_n["os_user"]
        ssh_key = prov_n["ssh_key"]
        cmd1 = f"{nc} spock node-drop {ndnm} {db}"
        util.echo_cmd(cmd1, host=ndip, usr=os_user, key=ssh_key)
    ## To Do: Check Nodes have been dropped


def app_remove(cluster_name, app_name, database_name=None):
    """Remove test application from cluster.

    Remove a test application from all of the nodes in a cluster.
    This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n
    Example: cluster app-remove pgbench
    :param cluster_name: The name of the cluster.
    :param node: The application name, pgbench or northwind.
    """
    db, db_settings, nodes = load_json(cluster_name)
    db_name = None
    if database_name is None:
        db_name = db[0]["db_name"]
    else:
        for i in db:
            if i["db_name"] == database_name:
                db_name = database_name
    if db_name is None:
        util.exit_message(f"Could not find information on db {database_name}")
    ctl = os.sep + "pgedge" + os.sep + "pgedge"
    if app_name == "pgbench":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["public_ip"]
            util.echo_cmd(
                f"{ndpath}{ctl} app pgbench-remove {db_name}",
                host=ndip,
                usr=n["os_user"],
                key=n["ssh_key"],
            )
    elif app_name == "northwind":
        for n in nodes:
            ndpath = n["path"]
            ndip = n["public_ip"]
            util.echo_cmd(
                f"{ndpath}{ctl} app northwind-remove {db_name}",
                host=ndip,
                usr=n["os_user"],
                key=n["ssh_key"],
            )
    else:
        util.exit_message("Invalid application name.")


def list_nodes(cluster_name):
    """List all nodes in the cluster."""
    db, db_settings, nodes = load_json(cluster_name)

    nodes_list = []
    for node in nodes:
        node_info = (
            f"Node: {node['name']}, IP: {node['public_ip']}, "
            f"Port: {node['port']}, Active: {'Yes' if node['is_active'] else 'No'}"
        )
        nodes_list.append(node_info)

    return nodes_list


def validate_json(json_data):
    required_keys = {
        "node_groups": {
            "dynamic_key": [
                {
                    "nodes": [
                        {
                            "name": str,
                            "is_active": bool,
                            "public_ip": str,
                            "port": int,
                            "repo1_type": str,
                            "path": str,
                        }
                    ]
                }
            ]
        }
    }

    valid_node_groups = {"aws", "localhost", "azure", "gcp", "remote"}
    valid_repo1_types = {"s3", "posix"}

    def validate_keys(data, template, path=""):
        if isinstance(template, dict):
            if not isinstance(data, dict):
                util.exit_message(
                    f"Expected a dictionary at {path}, but got {type(data).__name__}.",
                    1,
                )
            for key, sub_template in template.items():
                if key == "dynamic_key":
                    for dynamic_key in data.keys():
                        if dynamic_key not in valid_node_groups:
                            util.exit_message(
                                f"Invalid node group '{dynamic_key}' at {path}.", 1
                            )
                        validate_keys(
                            data[dynamic_key], sub_template, path + f".{dynamic_key}"
                        )
                else:
                    if key not in data:
                        util.exit_message(f"Missing key '{key}' at {path}.", 1)
                    validate_keys(data[key], sub_template, path + f".{key}")
        elif isinstance(template, list):
            if not isinstance(data, list):
                util.exit_message(
                    f"Expected a list at {path}, but got {type(data).__name__}.", 1
                )
            if len(template) > 0:
                for index, item in enumerate(data):
                    validate_keys(item, template[0], path + f"[{index}]")
        else:
            if not isinstance(data, template):
                util.exit_message(
                    f"Expected {template.__name__} at {path}, but got {type(data).__name__}.",
                    1,
                )
            if path.endswith(".repo1_type") and data not in valid_repo1_types:
                util.exit_message(f"Invalid repo1_type '{data}' at {path}.", 1)

    validate_keys(json_data, required_keys)


def print_install_hdr(
    cluster_name, db, db_user, total_nodes, name, path, ip, port, repo
):
    """
    Print the installation header with node and cluster information.

    Args:
        cluster_name (str): The name of the cluster.
        db (str): The database name.
        db_user (str): The database user.
        total_nodes (int): The total number of nodes in the cluster (including sub-nodes).
        name (str): The name of the current node.
        path (str): The installation path on the node.
        ip (str): The IP address of the node.
        port (str): The port number on the node.
        repo (str): The repository URL.
    """
    node_info = {
        "REPO": repo,
        "Cluster Name": cluster_name,
        "Node Name": name,
        "Host IP": ip,
        "Port": port,
        "Installation Path": path,
        "Database": db,
        "Database User": db_user,
        "Total Nodes": total_nodes,
    }
    util.echo_node(node_info)


def app_concurrent_index(cluster_name, db_name, index_name, table_name, col):
    """Helper function for a Creating concurrent index when auto_ddl is on."""
    db, db_settings, nodes = load_json(cluster_name)
    rc = 0
    found_db_name = None
    cmd = f"psql 'CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {table_name}({col})' "
    for d in db:
        if d["db_name"] == db_name:
            found_db_name = db_name

    if not found_db_name:
        util.exit_message(f"Could not find db {db_name} in cluster {cluster_name}", 1) 

    for nd in nodes:
        rc = util.echo_cmd(
            nd["path"]
            + os.sep
            + "pgedge"
            + os.sep
            + "pgedge "
            + cmd
            + found_db_name,
            host=nd["public_ip"],
            usr=nd["os_user"],
            key=nd["ssh_key"],
        )

    return rc


if __name__ == "__main__":
    fire.Fire(
        {
            "json-validate": json_validate,
            "json-create": json_create,
            "json-template": json_template,
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
            "app-remove": app_remove,
            "app-concurrent-index": app_concurrent_index,
        }
    )
