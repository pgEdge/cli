#!/usr/bin/env python3

#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os
import json
import util
import fire
import time
import warnings

from tabulate import tabulate

PATRONI = "/usr/local/patroni/patroni.py"
PATRONICTL = "/usr/local/patroni/patronictl.py"

base_dir = "cluster"

PATRONI_MEMBERES_LIST = f"{PATRONICTL} -c /etc/patroni/patroni.yaml list"
PATRONI_MEMBERES_REOME = f"{PATRONICTL} -c /etc/patroni/patroni.yaml remove postgres"

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

PATRONI_YAML = """
scope: postgres
namespace: /db/
name: NODE_NAME
replication_slot_name: NODE_NAME

restapi:
  listen: 0.0.0.0:8008
  connect_address: NODE_NAME:8008

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
        wal_keep_size: 64MB
        wal_keep_segments: 0
        track_commit_timestamp: true

  pg_hba:
    - host replication replicator 0.0.0.0/0 trust
    - host all all 0.0.0.0/0 trust
    - host all all 127.0.0.1/32 trust
    - host all all 172.31.0.0/16 trust
"""

PATRONI_YAML_POSTGRESQL = """
postgresql:
  listen: 0.0.0.0:PG_PORT
  connect_address: IP_NODE:PG_PORT
  data_dir: PGDATA
  bin_dir: PGBIN
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: REPLICATOR_USER
      password: REPLICATOR_PASSWORD
    superuser:
      username: SUPER_USER
      password: SUPER_PASSWORD
recovery_conf:
  standby_mode: "on"
  primary_conninfo: "host=IP_NODE port=PG_PORT user=REPLICATOR_USER password=REPLICATOR_PASSWORD"
  trigger_file: "/tmp/trigger"
"""


def init(cluster_name):
    db, db_settings, primary_nodes = util.load_json(cluster_name)
    for node in primary_nodes:
        configure_patroni(node, node["subnodes"], db, db_settings)

def patroni_command(cluster_name, node, cmd, args=None):
    if validate_config(cluster_name) == 'False':
        return

    cj = util.load_json(cluster_name)
    cluster = cj["cluster"]

    knt = 0
    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            knt += 1
            util.run_rcommand(
                f"{PATRONICTL} -c /etc/patroni/patroni.yaml {cmd}",
                message=f"Running patronictl {cmd} on {nd['name']}",
                host=nd['private_ip'], usr=nd['os_user'], key=nd['ssh_key']
            )
    if knt == 0:
        util.message("# nothing to do")

def update_node_yaml(node, db, db_settings):
    pg_ver = db_settings["pg_version"]
    
    replacements = {
        "IP_NODE": node['private_ip'],
        "PG_PORT": node['port'],
        "SUPER_USER": db['db_user'],
        "SUPER_PASSWORD": db['db_password'],
        "NODE_NAME": node['private_ip'],
        "REPLICATOR_USER": "replicator",
        "REPLICATOR_PASSWORD": "replicator",
        "PGDATA": os.path.join(
            node['path'], 'pgedge', 'data', f"pg{pg_ver}"
        ),
        "PGBIN": os.path.join(
            node['path'], 'pgedge', f"pg{pg_ver}", 'bin'
        ),
        "PGARCHIVE": os.path.join(
            node['path'], 'pgedge', f"pg{pg_ver}", 'archive'
        )
    }

    patroni_yaml = PATRONI_YAML + PATRONI_YAML_POSTGRESQL
    for placeholder, replacement in replacements.items():
        replacement = str(replacement)
        patroni_yaml = patroni_yaml.replace(placeholder, replacement)
   
    patroni_yaml_path = os.path.join('/etc/patroni', 'patroni.yaml')
    cmd = f"sudo sh -c 'echo \"{patroni_yaml}\" > {patroni_yaml_path}'"
    util.run_rcommand(
        cmd, 
        message="Updating Patroni YAML configuration",
        host=node["private_ip"], usr=node["os_user"], key=node["ssh_key"]
    )

def configure_node(node, db, db_settings, pg_ver, remove=False):
    util.run_rcommand(
        f"{node['path']}/pgedge/pgedge patroni stop",
        message=f"Stopping old Patroni on node {node['name']}",
        host=node["private_ip"], usr=node["os_user"], key=node["ssh_key"]
    )
    
    util.run_rcommand(
        f"{node['path']}/pgedge/pgedge install patroni",
        message=f"Installing Patroni on node {node['name']}",
        host=node["private_ip"], usr=node["os_user"], key=node["ssh_key"]
    )
    update_node_yaml(node, db, db_settings)
   
def configure_patroni(primary_node, nodes, db, db_settings):
    pg_ver = db_settings["pg_version"]

    pgdata = f"{primary_node['path']}/pgedge/data/pg{pg_ver}"
    util.run_rcommand(
        f"echo 'host replication replicator 0.0.0.0/0 trust' >> {pgdata}/pg_hba.conf",
        message=f"Adding replication entry to pg_hba.conf of {primary_node['name']}",
        host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    )
    util.run_rcommand(
        f"{primary_node['path']}/pgedge/pgedge restart",
        message=f"Restarting postgres on node {primary_node['name']}",
        host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    )
    #util.run_rcommand(
    #    PATRONI_MEMBERES_REOME,
    #    message=f"Removing old patroni cluster on {primary_node['name']}",
    #    host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    #) 
    configure_node(primary_node, db, db_settings, pg_ver, True)
    
    util.run_rcommand(
        f"sudo systemctl daemon-reload", 
        message="",
        host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    )
    util.run_rcommand(
        f"{primary_node['path']}/pgedge/pgedge patroni start",
        message=f"Starting Patroni on node {primary_node['name']}",
        host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    )

    for node in nodes:
        configure_node(node, db, db_settings, pg_ver)
        util.run_rcommand(
            f"sudo systemctl daemon-reload", 
            message="",
            host=node["private_ip"], usr=node["os_user"], key=node["ssh_key"]
        )
        util.run_rcommand(
            f"{node['path']}/pgedge/pgedge patroni start",
            message=f"Starting Patroni on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], key=node["ssh_key"]
        )
    
    util.wait_with_dots("Checking etcd health", 60) 
    util.echo_cmd(
        PATRONI_MEMBERES_LIST,
        host=primary_node["private_ip"], usr=primary_node["os_user"], key=primary_node["ssh_key"]
    )

if __name__ == "__main__":
    fire.Fire({
        "start": start,
        "stop": stop,
        "status": status,
    })

