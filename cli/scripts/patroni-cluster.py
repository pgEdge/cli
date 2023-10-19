#!/usr/bin/env python3

#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, json
import util, fire
import time, warnings
from tabulate import tabulate

base_dir = "patroni-cluster"
patroni_dir = "/usr/local/patroni/"

# These commands are used to refresh the etcd database and set the proper permissions.
ETCD_DATA     = f"/var/lib/etcd"
ETCD_CLEANUP  = f"rm -rf {ETCD_DATA}/*; mkdir -p {ETCD_DATA}; chown -R etcd:etcd {ETCD_DATA}; "
ETCD_CLEANUP += f"rm -rf {ETCD_DATA}/postgresql/*; mkdir -p {ETCD_DATA}/postgresql; chown -R etcd:etcd {ETCD_DATA}/postgresql; "
ETCD_CLEANUP += f"chmod 700 {ETCD_DATA}/postgresql;"

HAPROXY_YAML = """
global
  log /dev/log local0
  log /dev/log local1 notice
  maxconn 2000
  user haproxy
  group haproxy

defaults
  log global
  mode tcp
  option tcplog
  option dontlognull
  timeout connect 5000
  timeout client 50000
  timeout server 50000

listen pg-cluster
  bind *:5432
  mode tcp
  option tcplog
  balance roundrobin  # Adjust the load balancing algorithm as needed
"""

ETCD_YAML = """
name: NODE_NAME
advertise-client-urls: http://IP_NODE:2379
data-dir: /var/lib/etcd/postgresql
initial-advertise-peer-urls: http://IP_NODE:2380
initial-cluster: INITIAL_CLUSTER
initial-cluster-state: STATE
initial-cluster-token: devops_token
listen-client-urls: http://IP_NODE:2379,http://localhost:2379
listen-peer-urls: http://IP_NODE:2380
"""

PATRONI_YAML = """
scope: postgres
namespace: /db/
name: NODE_NAME
replication_slot_name: NODE_NAME

restapi:
  listen: 0.0.0.0:8008
  connect_address: IP_NODE:8008

etcd3:
  host: IP_NODE:2379
  ttl: 30
  protocol: http

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
  initdb:
    - encoding: UTF8
    - data-checksums
  postgresql:
    use_pg_rewind: true
    use_slots: true
"""

PATRONI_YAML_POSTGRESQL = """
postgresql:
  listen: 0.0.0.0:5432
  connect_address: IP_NODE:5432
  data_dir: PGDATA
  bin_dir: PGBIN
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: REPLICATOR_USER
      password: REPLICATOR_PASSWORD
    superuser:
      username: SUPER_USER
      password: SUPER_PASSORD
"""

PATRONI_REPLICA_YAML = """
recovery_conf:
  standby_mode: "on"
  primary_conninfo: "host=IP_NODE port=PG_PORT user=REPLICATOR_USER password=REPLICATOR_PASSWORD"
  trigger_file: "/tmp/trigger"
"""

def etcd_conf(cluster, nodes):
    for i, node in enumerate(nodes):
        etcd_yaml = ETCD_YAML.replace("IP_NODE", node['local_ip'])
        etcd_yaml = etcd_yaml.replace("NODE_NAME", node['name'])
        
        if i == 0:
            # Node 1 configuration
            initial_cluster = f"{node['name']}=http://{node['local_ip']}:2380"
            initial_cluster_state = "new"
        else:
            # Nodes 2 and 3 configuration
            initial_cluster = ",".join([f"{n['name']}=http://{n['local_ip']}:2380" for n in nodes[:i+1]])
            initial_cluster_state = "existing"
        
        etcd_yaml = etcd_yaml.replace("INITIAL_CLUSTER", initial_cluster)
        etcd_yaml = etcd_yaml.replace("STATE", initial_cluster_state)
        
        echo_cmd(f"sudo sh -c \"echo '{etcd_yaml}' > /etc/etcd/etcd.yaml\"", node['public_ip'], cluster)
        print(etcd_yaml)


def echo_cmd(command, host, cluster, fail=1, max_retries=1):
    for _ in range(max_retries):
        rc = util.echo_cmd(f"{command}", host=host, usr=cluster["os_user"], key=cluster["ssh_key"])
        if rc == 0:
            return "OK"
        max_retries -= 1
        if max_retries > 0:
            time.sleep(1)
            util.message("Retrying command...")
        else:
            if fail == 1:
                util.exit_message("Command failed...", 1)
                return 1
    return 0
 
def create_local_json(config):
    cluster_name = config["cluster"]["cluster"]
    num_nodes = config["cluster"]["count"]
    port1 = 5432  # Replace with the actual port

    cluster_dir = base_dir + os.sep + cluster_name
    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    cluster_json = {
        "HAProxy": config["HAProxy"],
        "cluster": config["cluster"],
        "nodes": [],
    }

    for n in range(1, num_nodes + 1):
        node_json = {
            "nodename": config["nodes"][n - 1]["name"],
            "ip": config["nodes"][n - 1]["ip"],
            "local_ip": config["nodes"][n - 1]["local_ip"],
            "port": port1,
            "path": os.getcwd()
            + os.sep
            + "cluster"
            + os.sep
            + cluster_name
            + os.sep
            + "n"
            + str(n),
            "primary": config["nodes"][n - 1]["primary"],
            "bootstrap": config["nodes"][n - 1]["bootstrap"],
        }
        cluster_json["nodes"].append(node_json)
        port1 = port1 + 1

    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
        print(f"JSON file '{cluster_name}.json' has been created.")
    except Exception as e:
        util.exit_message("Unable to create JSON file: " + str(e), 1)

def load_json(cluster_name):
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
        util.exit_message(f"Unable to load cluster def file '{cluster_file}'\n{e}")

    return parsed_json


def reset_remote(cluster_name):
    """Reset a patroni-cluster from json definition file of existing nodes."""
    validate_config(cluster_name)
 
    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    util.message("\n## Ensure that PG is stopped.")
    for nd in cj["nodes"]:
        ndpath = cluster["path"] + nd['name'] + "/"
        cmd = ndpath + "/nodectl stop 2> /dev/null"
        echo_cmd(f"{cmd}", nd["ip"], cluster)

def check_cluster(cluster_name):
    
    if validate_config(cluster_name) == 'False':
        return

    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    for nd in cj["nodes"]:
        is_primary = nd["primary"]
        if is_primary == True:
            util.message("\n## checking primary node has all module installed")
            bin_path = f"{cluster['path']}/{nd['name']}/pgedge/pg16/bin"
            data_path = f"{cluster['path']}/{nd['name']}/pgedge/data/pg16"

            # Check if PostgreSQL is installed in bin_path
            rc = echo_cmd(f"{bin_path}/postgres --version", nd['public_ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No PostgreSQL installation found in {bin_path}")

            # Check for ETCD installation
            rc = echo_cmd(f"etcdctl version", nd['public_ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No ETCD installation found in $PATH")

            # Check for Patroni installation
            rc = echo_cmd(f"{patroni_dir}/patronictl.py version", nd['public_ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No Patroni installation found in {patroni_dir}")

            cmd_check_data_dir = f"[ -d {data_path} ] || echo '' exit 1"
            rc = echo_cmd(cmd_check_data_dir, nd['public_ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"Data directory not found at {data_path} for the primary node")
        else:
            util.message(f"\nchecking ssh'ing to replica {nd['name']} - {nd['public_ip']}")
            cmd = f"ssh -o StrictHostKeyChecking=no -q -t {cj['cluster']['os_user']}@{nd['public_ip']} -i {cj['cluster']['ssh_key']} 'hostname'"
            result = util.echo_cmd(cmd)
            status = "OK" if result == 0 else "FAILED"
            util.message(f"{status}")


def init_remote(cluster_name, app=None):
    """Initialize a patroni-cluster from json definition file of existing nodes."""
    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    if validate_config(cluster_name) == 'False':
        return

    cj = load_json(cluster_name)
    cluster= cj["cluster"]
    nodes = cj["nodes"]
    haproxy = cj["HAProxy"]
  
    print_information(cj)

    #check_cluster(cluster_name)
    #configure_etcd(cluster, nodes)
    #configure_patroni(cluster, nodes)
    configure_haproxy(haproxy, cluster, nodes)

def print_config(cluster_name):
    """Print patroni-cluster json definition file information."""
    if validate_config(cluster_name) == 'False':
        return

    config = load_json(cluster_name)
    print_information(config)

def print_information(config):
    # HAProxy Info
    print("#" * 70)
    print("#       haproxy: ver 1.1.0")
    print("#     public ip: " + config["HAProxy"]["public_ip"])
    print("#      local iP: " + config["HAProxy"]["local_ip"])
    print("#      username: " + config["HAProxy"]["username"])
    print("#  ssh key path: " + config["HAProxy"]["ssh_key_path"])
    print("# ")
    print("*" * 70)

    # Cluster Info
    cluster = config["cluster"]
    print("#        cluster Name: " + cluster["cluster"])
    print("#         create Date: " + cluster["create_dt"])
    print("#       database name: " + cluster["db_name"])
    print("#       database user: " + cluster["db_user"])
    print("#   database password: " + cluster["db_init_passwd"])
    print("#     replicator user: " + cluster["replicator_user"])
    print("# replicator password: " + cluster["replicator_password"])
    print("#             os user: " + cluster["os_user"])
    print("#             ssh_key: " + cluster["ssh_key"])
    print("#    postgres version: " + cluster["pg_ver"])
    print("#     number of nodes: " + cluster["count"])
    print("# ")
    print(("*" * 70))

    print((" "))

    # PostgreSQL Config
    postgresql_conf = config["cluster"]["cluster_init"]["postgresql_conf"]
    print("#     postgres configuration:")
    for key, value in postgresql_conf.items():
        print(f"#     {key}: {value}")
    print(("#" * 70))
    
    print((" "))

    # Nodes Info
    nodes = config.get("nodes", [])
    nodes_data = []
    for node in nodes:
        node_data = {
            "node name": node.get("name", ""),
            "public ip": node.get("public_ip", ""),
            "local ip": node.get("local_ip", ""),
            "is_primary": node.get("primary", ""),
            "bootstrap": node.get("bootstrap", ""),
        }
        nodes_data.append(node_data)

    print(tabulate(nodes_data, headers="keys", tablefmt="pipe"))
    print(("#" * 70))
 
def install_pgedge(cluster_name):
    """Install pgedge on cluster from json definition file nodes."""
    if validate_config(cluster_name) == 'False':
        return

    cj = load_json(cluster_name)
    print_information(cj)
    nodes = cj["nodes"]
    cluster = cj["cluster"]

    for n in nodes:
        ndip = n["public_ip"]
        path = f"{cluster['path']}/{n['name']}/"
        cmd = f"rm -rf {path}"
        echo_cmd(cmd, ndip, cluster)

    for n in nodes:
        is_primary = node["primary"]
        if is_primary == 'False':
            continue
        ndnm = n["name"]
        ndip = n["public_ip"]
        ndport = cluster["port"]
        ndpath = cluster["path"] + ndnm + "/"

        if cluster["is_local"] == "False":
            REPO = util.get_value("GLOBAL", "REPO")
            os.environ["REPO"] = REPO
        else:
            os.environ["REPO"] = ""
            REPO = "https://pgedge-upstream.s3.amazonaws.com/REPO"

        cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; "
        cmd2 = f"python3 -c '$(curl -fsSL {REPO}/install24.py)'"
        echo_cmd(f"{cmd1}{cmd2}",ndip, cluster);
 
        nc = f"{ndpath}/pgedge/nodectl"  # Fixed path here
        parms = (
            f" -U {cluster['db_user']} "
            f"-P '{cluster['db_init_passwd']}' "
            f"-d {cluster['db_name']} "
            f"-p {ndport} "
            f"--pg {cluster['pg_ver']}"
        )
        echo_cmd(f"{nc} install pgedge{parms}",ndip, cluster);
        util.message("#")


def nodectl_command(cluster_name, node, cmd, args=None):
    """Run 'nodectl' commands on one or 'all' nodes."""
    if validate_config(cluster_name) == 'False':
        return

    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(nd["path"] + "/pgedge/nodectl" + cmd, nd['public_ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

def etcd_command(cluster_name, node, cmd, args=None):
    """Run 'etcdctl' command on a node."""
    if validate_config(cluster_name) == 'False':
        return

    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(f"etcdctl " + cmd, nd['public_ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

def patroni_command(cluster_name, node, cmd, args=None):
    """Run 'patronictl' command on a node"""
    if validate_config(cluster_name) == 'False':
        return


    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(f"{patroni_dir}/patronictl.py -c /etc/patroni/patroni.yaml " + cmd, nd['public_ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

def configure_haproxy(haproxy, cluster, nodes):
    print("#" * 70)
    print("#       Configuring HAProxy")
    print("*" * 70)
   
    stop_cmd = "sudo systemctl stop haproxy"
    start_cmd = "sudo systemctl start haproxy"
    reload_cmd = "sudo systemctl daemon-reload"

    # Reload HAProxy configuration
    echo_cmd(f"{reload_cmd}; {stop_cmd}", haproxy['public_ip'], cluster)

    haproxy_yaml = []
    haproxy_yaml.append(HAPROXY_YAML)
    for node in nodes:
        # Determine whether the node is primary or replica
        is_primary = node.get("primary", False)
        if is_primary:
            haproxy_line = f"  server {node['name']} {node['public_ip']}:{cluster['port']} check"
            haproxy_yaml.append(haproxy_line)
    
    haproxy_yaml_content = "\n".join(haproxy_yaml)
    haproxy_yaml_path = os.path.join('/etc/haproxy', 'haproxy.cfg')
    cmd = f"sudo sh -c 'echo \"{haproxy_yaml_content}\" > {haproxy_yaml_path}'"
   
    # Configure HAProxy and start it
    echo_cmd(cmd, haproxy['public_ip'], cluster)
    echo_cmd(start_cmd, haproxy['public_ip'], cluster)

def configure_etcd(cluster, nodes):
    node_ips = [node['local_ip'] for node in nodes]
    node_names = [node['name'] for node in nodes]

    print(("#" * 70))
    print("#       Configuring etcd on all nodes")
    print(("*" * 70))

    util.message("\n# generating etcd.yaml files\n")
    etcd_conf(cluster, nodes)
    
    util.message("# reset etcd on all nodes\n")
    for nd in nodes:
        cmd_reload = "sudo systemctl daemon-reload"
        cmd_stop_etcd = "sudo systemctl stop etcd"
        cmd_cleanup_etcd = f"{cmd_stop_etcd}; sudo sh -c '{ETCD_CLEANUP}'"
        echo_cmd(f"{cmd_reload}; {cmd_cleanup_etcd}", nd['public_ip'], cluster)

    util.message("# setting up etcd on all nodes\n")

    for i, node in enumerate(nodes):
        if i > 0:
            cmd_start_etcd = "sudo systemctl start etcd"
            cmd_etcd_member = f"etcdctl member add {node_names[i]} --peer-urls=http://{node_ips[i]}:2380"
            echo_cmd(cmd_etcd_member, nodes[0]['public_ip'], cluster)
            echo_cmd(cmd_start_etcd, nodes[i]['public_ip'], cluster)
            time.sleep(3)  # Sleep for a few seconds for the first node
        
        if i == 0:
            cmd_start_etcd = "sudo systemctl start etcd"
            echo_cmd(cmd_start_etcd, nodes[0]['public_ip'], cluster)

        cmd_member_list = "etcdctl endpoint status --write-out=table"
        echo_cmd(cmd_member_list, node['public_ip'], cluster)

    cmd_member_list = "etcdctl member list"
    echo_cmd(cmd_member_list, nodes[0]['public_ip'], cluster)

def configure_patroni(cluster, nodes):
    print("#" * 70)
    print("#       Configuring Patroni on all nodes")
    print("*" * 70)

    stop_cmd = "sudo systemctl stop patroni"
    start_cmd = "sudo systemctl start patroni"
    reload_cmd = "sudo systemctl daemon-reload"
    restart_cmd = "sudo systemctl restart patroni"
 
    for node in nodes:
        echo_cmd(f"{reload_cmd}; {stop_cmd}", node['public_ip'], cluster)

    cluster_init = cluster["cluster_init"]

    for node in nodes:
        # Determine whether the node is primary or replica
        is_primary = node["primary"]

        replacements = {
            "IP_NODE": node['local_ip'],
            "PG_PORT": cluster['port'],
            "REPLICATOR_USER": cluster['replicator_user'],
            "REPLICATOR_PASSWORD": cluster['replicator_password'],
            "SUPER_USER": cluster['db_user'],
            "SUPER_PASSWORD": cluster['db_init_passwd'],
            "NODE_NAME": node['name'],
            "PGDATA": os.path.join(cluster['path'], node['name'], 'pgedge', 'data', 'pg16'),
            "PGBIN": os.path.join(cluster['path'], node['name'], 'pgedge', 'pg16', 'bin'),
            "PGARCHIVE": os.path.join(cluster['path'], node['name'], 'pgedge', 'pg16', 'archive')
        }

        patroni_yaml = PATRONI_YAML

        patroni_yaml += "    parameters:\n"
        for key, value in cluster_init.items():
            if not isinstance(value, dict):
                patroni_yaml += f"      {key}: \"{value}\"\n"

        patroni_yaml += PATRONI_YAML_POSTGRESQL

        patroni_yaml += "parameters:\n"
        for key, value in cluster["cluster_init"]["postgresql_conf"].items():
            patroni_yaml += f"  {key}: \"{value}\"\n"

        patroni_yaml += "pg_hba:\n"
        for key, value in cluster["cluster_init"]["pg_hba_conf"].items():
            patroni_yaml += f"  - {key} {value}\n"

        # Create Patroni YAML
        patroni_yaml += PATRONI_REPLICA_YAML if not is_primary else ""

        # Replace placeholders in Patroni YAML
        for placeholder, replacement in replacements.items():
            patroni_yaml = patroni_yaml.replace(placeholder, replacement)

        # Write Patroni YAML to file
        patroni_yaml_path = os.path.join('/etc/patroni', 'patroni.yaml')
        cmd = f"sudo sh -c 'echo \"{patroni_yaml}\" > {patroni_yaml_path}'"
        echo_cmd(cmd, node['public_ip'], cluster)

        # If not primary, remove PGDATA directory
        if not is_primary:
            pgdata_path = os.path.join(cluster['path'], node['name'], 'pgedge', 'data', 'pg16')
            cmd = f"rm -rf {pgdata_path}"
            echo_cmd(cmd, node['public_ip'], cluster)

        # Reload and start PostgreSQL
        echo_cmd(start_cmd, node['public_ip'], cluster)

        print(patroni_yaml)
    cmd = os.path.join(patroni_dir, 'patronictl.py') + " -c /etc/patroni/patroni.yaml list"
    echo_cmd(cmd, nodes[0]['public_ip'], cluster)
    
    # for node in nodes:
    #    echo_cmd(f"{restart_cmd}", node['public_ip'], cluster)
    # echo_cmd(cmd, nodes[0]['public_ip'], cluster)

def validate_config(cluster_name):
    """ Validate the JSON configuration file."""
    cj = load_json(cluster_name)

    # Check if required keys are present
    required_keys = ["HAProxy", "cluster", "nodes"]
    for key in required_keys:
        if key not in cj:
            print(f"Error: '{key}' is missing in the JSON configuration.")
            return False

    haproxy = cj["HAProxy"]
    cluster = cj["cluster"]

    # Check if keys have the expected structure
    if "HAProxy" in cj:
        haproxy_keys = ["public_ip", "local_ip", "username", "ssh_key_path"]
        for key in haproxy_keys:
            if key not in haproxy:
                print(f"Error: '{key}' is missing in the 'HAProxy' section of the JSON configuration.")
                return False

    if "cluster" in cj:
        cluster_keys = ["cluster", "is_local", "create_dt", "db_name", "db_user", "db_init_passwd",
                        "replicator_user", "replicator_password", "os_user", "ssh_key",
                        "pg_ver", "port", "path", "cluster_init", "count"]
        for key in cluster_keys:
            if key not in cluster:
                print(f"Error: '{key}' is missing in the 'cluster' section of the JSON configuration.")
                return False

    if "nodes" in cj:
        primary_count = 0
        for node in cj["nodes"]:
            node_keys = ["name", "public_ip", "local_ip", "primary", "bootstrap"]
            for key in node_keys:
                if key not in node:
                    print(f"Error: '{key}' is missing in one of the 'nodes' entries in the JSON configuration.")
                    return False

            # Check if only one node is marked as "primary"
            if "primary" in node and node["primary"]:
                primary_count += 1

        if primary_count != 1:
            print("Error: Only one node should be marked as 'primary' in the JSON configuration.")
            return False

    print(f"JSON configuration is correct and validated")
 
if __name__ == "__main__":
    fire.Fire(
        {
            "init-remote": init_remote,
            "reset-remote": reset_remote,
            "install-pgedge": install_pgedge,
            "nodectl-command": nodectl_command,
            "patroni-command": patroni_command,
            "etcd-command": etcd_command,
            "print_config": print_config,
            "validate-config": validate_config,
        }
    )
