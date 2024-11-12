#!/usr/bin/env python3

#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os
import json
import util
import fire
import time

base_dir = "cluster"

ETCD = "/usr/local/etcd/etcd"
ETCDCTL = "/usr/local/etcd/etcdctl"

ETCD_DATA = "/var/lib/etcd"
ETCD_CLEANUP = (
    f"rm -rf {ETCD_DATA}/*; mkdir -p {ETCD_DATA}; "
    f"chown -R etcd:etcd {ETCD_DATA}; "
    f"rm -rf {ETCD_DATA}/postgresql/*; "
    f"mkdir -p {ETCD_DATA}/postgresql; "
    f"chown -R etcd:etcd {ETCD_DATA}/postgresql; "
    f"chmod 700 {ETCD_DATA}/postgresql;"
)
ETCD_MEMBERS_STATUS = (
    f"{ETCDCTL} endpoint status --write-out=table"
)
ETCD_MEMBERS_LIST = f"{ETCDCTL} member list"

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
dial-timeout: 20s
read-timeout: 20s
write-timeout: 20s
"""

def etcd_conf(primary_node, nodes):
    primary_etcd_yaml = (
        ETCD_YAML.replace("NODE_NAME", primary_node['name'])
        .replace("IP_NODE", primary_node['private_ip'])
        .replace("INITIAL_CLUSTER", 
                 f"{primary_node['name']}=http://{primary_node['private_ip']}:2380")
        .replace("STATE", "new")
    )
    primary_cmd = (
        f"sudo sh -c \"echo '{primary_etcd_yaml}' > /etc/etcd/etcd.yaml\""
    )
    util.run_rcommand(
        primary_cmd, 
        message="Creating ETCD configuration on primary server",
        host=primary_node["private_ip"], usr=primary_node["os_user"], 
        key=primary_node["ssh_key"]
    )

    initial_cluster_configs = (
        f"{primary_node['name']}=http://{primary_node['private_ip']}:2380"
    )

    for node in nodes:
        initial_cluster_configs += (
            f",{node['name']}=http://{node['private_ip']}:2380"
        )
        etcd_yaml = (
            ETCD_YAML.replace("NODE_NAME", node['name'])
            .replace("IP_NODE", node['private_ip'])
            .replace("INITIAL_CLUSTER", initial_cluster_configs)
            .replace("STATE", "existing")
        )
        cmd = (
            f"sudo sh -c \"echo '{etcd_yaml}' > /etc/etcd/etcd.yaml\""
        )
        util.run_rcommand(
            cmd, 
            message=f"Creating ETCD configuration on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], 
            key=node["ssh_key"]
        )

def init(cluster_name):
    db, db_settings, primary_nodes = util.load_json(cluster_name)
    for node in primary_nodes:
        configure_etcd(node, node["subnodes"])

def etcd_command(cluster_name, node, cmd, args=None):
    if validate_config(cluster_name) == 'False':
        return

    cj = util.load_json(cluster_name)
    cluster = cj["cluster"]

    for nd in cj["nodes"]:
        if node == "all" or node == nd["name"]:
            util.run_rcommand(
                f"etcdctl {cmd}", 
                message=f"Running etcdctl {cmd} on {nd['name']}",
                host=nd['public_ip'], cluster=cluster
            )

def configure_etcd(primary_node, nodes):
    node_ips = [node['private_ip'] for node in nodes]
    node_names = [node['name'] for node in nodes]

    util.run_rcommand(
        f"{primary_node['path']}/pgedge/pgedge remove etcd",
        message="Removing old ETCD installation on primary server",
        host=primary_node["private_ip"], usr=primary_node["os_user"],
        key=primary_node["ssh_key"]
    )

    clean_cmd = f"sudo sh -c '{ETCD_CLEANUP}';"
    util.run_rcommand(
        clean_cmd,
        message="Cleaning ETCD data on primary server",
        host=primary_node["private_ip"], usr=primary_node["os_user"], 
        key=primary_node["ssh_key"]
    )

    util.run_rcommand(
        f"{primary_node['path']}/pgedge/pgedge install etcd",
        message="Installing ETCD on primary server",
        host=primary_node["private_ip"], usr=primary_node["os_user"],
        key=primary_node["ssh_key"]
    )

    for node in nodes:
        util.run_rcommand(
            f"{node['path']}/pgedge/pgedge remove etcd",
            message=f"Removing old ETCD installation on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], 
            key=node["ssh_key"]
        )
        util.run_rcommand(
            clean_cmd,
            message=f"Cleaning ETCD data on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], 
            key=node["ssh_key"]
        )
        util.run_rcommand(
            f"{node['path']}/pgedge/pgedge install etcd",
            message=f"Installing ETCD on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], 
            key=node["ssh_key"]
        )

    etcd_conf(primary_node, nodes)

    util.run_rcommand(
        f"{primary_node['path']}/pgedge/pgedge etcd start",
        message="Starting ETCD on primary server",
        host=primary_node["private_ip"], usr=primary_node["os_user"],
        key=primary_node["ssh_key"]
    )
    util.wait_with_dots("Wait to start etcd", 15) 

    util.run_rcommand(
        f"{ETCDCTL} --endpoints=http://{primary_node['private_ip']}:2379 endpoint health",
        message="Healthcheck ETCD's primary node",
        host=primary_node["private_ip"], usr=primary_node["os_user"],
        key=primary_node["ssh_key"],
        max_attempts=3
    )

    util.wait_with_dots("Wait to start etcd", 15) 
    for i, node in enumerate(nodes):
        util.run_rcommand(
            f"{ETCDCTL} member add {node_names[i]} "
            f"--peer-urls=http://{node_ips[i]}:2380",
            message=f"Adding member {node_names[i]}",
            host=primary_node["private_ip"], usr=primary_node["os_user"],
            key=primary_node["ssh_key"]
            )
        util.wait_with_dots("Wait to add node to etcd", 10) 
        util.run_rcommand(
            f"{node['path']}/pgedge/pgedge etcd start",
            message=f"Starting ETCD on node {node['name']}",
            host=node["private_ip"], usr=node["os_user"], 
            key=node["ssh_key"]
        )
        util.wait_with_dots("Wait to start etcd", 10) 

    util.echo_message(f"List of ETCD nodes", bold=True)
    util.echo_cmd(
        ETCD_MEMBERS_LIST,
        host=primary_node["private_ip"],
        usr=primary_node["os_user"],
        key=primary_node["ssh_key"]
    )
    
    cmd = f"{ETCDCTL} --endpoints=http://{primary_node['private_ip']}:2379"
    for i, node in enumerate(nodes):
        cmd = cmd + ","
        cmd = cmd + f"http://{node['private_ip']}:2379"
    cmd = cmd + " endpoint health"
    
    util.echo_message(f"Healthcheck of complete ETCD cluster", bold=True)
    util.echo_cmd(
        cmd,
        host=primary_node["private_ip"],
        usr=primary_node["os_user"],
        key=primary_node["ssh_key"]
    )


if __name__ == "__main__":
    fire.Fire({
        "start": start,
        "stop": stop,
        "status": status,
    })

