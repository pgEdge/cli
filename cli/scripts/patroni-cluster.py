#!/usr/bin/env python3

#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, json
import util, fire
import time
from tabulate import tabulate

base_dir = "patroni-cluster"
patroni_dir = "/usr/local/patroni/"

# These commands are used to refresh the etcd database and set the proper permissions.
ETCD_DATA     = f"/var/lib/etcd"
ETCD_CLEANUP  = f"rm -rf {ETCD_DATA}/*; mkdir -p {ETCD_DATA}; chown -R etcd:etcd {ETCD_DATA}; "
ETCD_CLEANUP += f"rm -rf {ETCD_DATA}/postgresql/*; mkdir -p {ETCD_DATA}/postgresql; chown -R etcd:etcd {ETCD_DATA}/postgresql; "
ETCD_CLEANUP += f"chmod 700 {ETCD_DATA}/postgresql;"

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
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        archive_mode: "on"
        archive_command: "cp -f %p PGARCHIVE/%f"
  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: IP_NODE:5432
  data_dir: PGDATA
  bin_dir: PGBIN
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: replicatorpassword
    superuser:
      username: postgres
      password: mysupersecretpassword
  parameters:
  
  pg_hba:
    - local all all trust
    - host all all 0.0.0.0/0 trust
    - host replication replicator IP_NODE1/32 trust
    - host replication replicator IP_NODE2/32 trust
    - host replication replicator IP_NODE3/32 trust
    - host replication all 0.0.0.0/0 trust
    - host all all 0.0.0.0/0 trust
    """

PATRONI_REPLICA_YAML = """
recovery_conf:
    standby_mode: "on"
    primary_conninfo: "host=IP_NODE port=5432 user=replicator password=replicatorpassword
    trigger_file: /tmp/trigger
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
        
        echo_cmd(f"sudo sh -c \"echo '{etcd_yaml}' > /etc/etcd/etcd.yaml\"", node['ip'], cluster)
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
    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    util.message("\n## Ensure that PG is stopped.")
    for nd in cj["nodes"]:
        ndpath = cluster["path"] + nd['name'] + "/"
        cmd = ndpath + "/nodectl stop 2> /dev/null"
        echo_cmd(f"{cmd}", nd["ip"], cluster)

def check_cluster(cluster_name):

    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    for nd in cj["nodes"]:
        is_primary = nd["primary"]
        if is_primary == True:
            util.message("\n## checking primary node has all module installed")
            bin_path = f"{cluster['path']}/{nd['name']}/pgedge/pg16/bin"
            data_path = f"{cluster['path']}/{nd['name']}/pgedge/data/pg16"

            # Check if PostgreSQL is installed in bin_path
            rc = echo_cmd(f"{bin_path}/postgres --version", nd['ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No PostgreSQL installation found in {bin_path}")

            # Check for ETCD installation
            rc = echo_cmd(f"etcdctl version", nd['ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No ETCD installation found in $PATH")

            # Check for Patroni installation
            rc = echo_cmd(f"{patroni_dir}/patronictl.py version", nd['ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"No Patroni installation found in {patroni_dir}")

            cmd_check_data_dir = f"[ -d {data_path} ] || echo '' exit 1"
            rc = echo_cmd(cmd_check_data_dir, nd['ip'], cluster, 0)
            if rc == 1:
                util.exit_message(f"Data directory not found at {data_path} for the primary node")
        else:
            util.message(f"\nchecking ssh'ing to replica {nd['name']} - {nd['ip']}")
            cmd = f"ssh -o StrictHostKeyChecking=no -q -t {cj['cluster']['os_user']}@{nd['ip']} -i {cj['cluster']['ssh_key']} 'hostname'"
            result = util.echo_cmd(cmd)
            status = "OK" if result == 0 else "FAILED"
            util.message(f"{status}")


def init_remote(cluster_name, app=None):
    """Initialize a patroni-cluster from json definition file of existing nodes."""
    util.message(f"## Loading cluster '{cluster_name}' json definition file")
    cj = load_json(cluster_name)
    cluster= cj["cluster"]
    nodes = cj["nodes"]

    print_information(cj)

    check_cluster(cluster_name)

    configure_etcd(cluster, nodes)
    configure_patroni(cluster, nodes)

def print_config(cluster_name):
    """Print patroni-cluster json definition file information."""
    config = load_json(cluster_name)
    print_information(config)


def print_information(config):
    # HAProxy Info
    print(("#" * 70))
    print("#       HAProxy: ver 1.1.0" )
    print("#            IP: "  + config["HAProxy"]["ip"])
    print("#      Local IP: "  + config["HAProxy"]["local_ip"])
    print("#      Username: "  + config["HAProxy"]["username"])
    print("#  SSH Key Path: "  + config["HAProxy"]["ssh_key_path"])
    print("# ")
    print(("*" * 70))
    
    # Cluster Info
    print("#        Cluster Name: " + config["cluster"]["cluster"])
    print("#         Create Date: " + config["cluster"]["create_dt"])
    print("#             DB Name: " + config["cluster"]["db_name"])
    print("#             DB User: " + config["cluster"]["db_user"])
    print("# DB Initial Password: " + config["cluster"]["db_init_passwd"])
    print("#             OS User: " + config["cluster"]["os_user"])
    print("#             SSH Key: " + config["cluster"]["ssh_key"])
    print("#  PostgreSQL Version: " + config["cluster"]["pg_ver"])
    print("#          Node Count: " + config["cluster"]["count"])
    print("# ")
    print(("#" * 70))
    
    # Nodes Info
    nodes = config.get("nodes", [])
    nodes_data = []
    for node in nodes:
        node_data = {
            "Node Name": node.get("name", ""),
            "IP": node.get("ip", ""),
            "Local IP": node.get("local_ip", ""),
            "Primary": node.get("primary", ""),
            "Bootstrap": node.get("bootstrap", ""),
        }
        nodes_data.append(node_data)

    print(tabulate(nodes_data, headers="keys", tablefmt="pipe"))
    print(("#" * 70))
   
def install_pgedge(cluster_name):
    """Install pgedge on cluster from json definition file nodes."""
    cj = load_json(cluster_name)
    print_information(cj)
    nodes = cj["nodes"]
    cluster = cj["cluster"]

    for n in nodes:
        ndip = n["ip"]
        path = f"{cluster['path']}/{n['name']}/"
        cmd = f"rm -rf {path}"
        echo_cmd(cmd, ndip, cluster)

    for n in nodes:
        ndnm = n["name"]
        ndip = n["ip"]
        ndport = cluster["port"]
        ndpath = cluster["path"] + ndnm + "/"  # Fixed the path calculation

        if cluster["il"] == "True":  # Use cluster instead of cj["cluster"]
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
    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(nd["path"] + "/pgedge/nodectl" + cmd, nd['ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

def etcd_command(cluster_name, node, cmd, args=None):
    """Run 'etcdctl' command on a node."""
    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(f"etcdctl " + cmd, nd['ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

def patroni_command(cluster_name, node, cmd, args=None):
    """Run 'patronictl' command on a node"""

    cj = load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt = knt + 1
            echo_cmd(f"patronictl " + cmd, nd['ip'], cluster);
    if knt == 0:
        util.message(f"# nothing to do")

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
        cmd_stop_etcd = "sudo systemctl stop etcd"
        cmd_cleanup_etcd = f"{cmd_stop_etcd}; sudo sh -c '{ETCD_CLEANUP}'"
        echo_cmd(cmd_cleanup_etcd, nd['ip'], cluster)

    util.message("# setting up etcd on all nodes\n")

    for i, node in enumerate(nodes):
        if i > 0:
            cmd_start_etcd = "sudo systemctl start etcd"
            cmd_etcd_member = f"etcdctl member add {node_names[i]} --peer-urls=http://{node_ips[i]}:2380"
            echo_cmd(cmd_etcd_member, nodes[0]['ip'], cluster)
            echo_cmd(cmd_start_etcd, nodes[i]['ip'], cluster)
            time.sleep(3)  # Sleep for a few seconds for the first node
        
        if i == 0:
            cmd_start_etcd = "sudo systemctl start etcd"
            echo_cmd(cmd_start_etcd, nodes[0]['ip'], cluster)

        cmd_member_list = "etcdctl endpoint status --write-out=table"
        echo_cmd(cmd_member_list, node['ip'], cluster)

    cmd_member_list = "etcdctl member list"
    echo_cmd(cmd_member_list, nodes[0]['ip'], cluster)


def configure_patroni(cluster, nodes):
    print("#" * 70)
    print("#       Configuring Patroni on all nodes")
    print("*" * 70)

    stop_cmd = "sudo systemctl stop patroni"
    start_cmd = "sudo systemctl start patroni"
    reload_cmd = "sudo systemctl daemon-reload"

    for i, node in enumerate(nodes):
        echo_cmd(stop_cmd, node['ip'], cluster)

    for node in nodes:
        # Determine whether the node is primary or replica
        is_primary = node["primary"]

        # Define placeholders and replacements
        replacements = {
            "IP_NODE": node['local_ip'],
            "NODE_NAME": node['name'],
            "PGDATA": f"{cluster['path']}/{node['name']}/pgedge/data/pg16",
            "PGBIN": f"{cluster['path']}/{node['name']}/pgedge/pg16/bin/",
            "PGARCHIVE": f"{cluster['path']}/{node['name']}/pgedge/pg16/archive/"
        }

        # Create Patroni YAML
        patroni_yaml = PATRONI_YAML + (PATRONI_REPLICA_YAML if not is_primary else "")

        # Replace placeholders in Patroni YAML
        for placeholder, replacement in replacements.items():
            patroni_yaml = patroni_yaml.replace(placeholder, replacement)

        # Write Patroni YAML to file
        cmd = f"sudo sh -c 'echo \"{patroni_yaml}\" >> /etc/patroni/patroni.yaml'"
        echo_cmd(cmd, node['ip'], cluster)
        print(patroni_yaml)

        # If not primary, remove PGDATA directory
        if not is_primary:
            cmd = f"rm -rf {cluster['path']}/{node['name']}/pgedge/data/pg16"
            echo_cmd(cmd, node['ip'], cluster)

        # Reload and start PostgreSQL
        echo_cmd(reload_cmd, node['ip'], cluster)
        echo_cmd(start_cmd, node['ip'], cluster)

if __name__ == "__main__":
    fire.Fire(
        {
            "init-remote": init_remote,
            "reset-remote": reset_remote,
            "install-pgedge": install_pgedge,
            "nodectl-command": nodectl_command,
            "patroni-command": patroni_command,
            "etcd-command": etcd_command,
            "print_config": print_config
        }
    )
