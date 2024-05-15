#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime
import util, utilx, fire, meta, time, sys

def create_node(node, dbname):
    """
    Creates a new node in the database cluster.
    """
    utilx.echo_action(f"Creating new node {node['name']}")

    cmd = (f"cd {node['path']}/pgedge/; "
           f"./pgedge spock node-create {node['name']} "
           f"'host={node['ip_address']} user=pgedge dbname={dbname} "
           f"port={node['port']}' {dbname}")
    utilx.echo_cmd(cmd, host=node["ip_address"],
                   usr=node["os_user"], key=node["ssh_key"])
    utilx.echo_action(f"Creating new node {node['name']}", "ok")

def create_sub(nodes, new_node, dbname):
    """
    Creates subscriptions for each node to a new node in the cluster.
    """
    for node in nodes:
        sub_name = f"sub_{node['name']}{new_node['name']}"
        utilx.echo_action(f"Creating subscription {sub_name}")

        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge spock sub-create {sub_name} "
               f"'host={new_node['ip_address']} user=pgedge dbname={dbname} "
               f"port={new_node['port']}' {dbname}")
        utilx.echo_cmd(cmd, host=node["ip_address"],
                       usr=node["os_user"], key=node["ssh_key"])
        utilx.echo_action(f"Subscription {sub_name} created successfully", "ok")

def terminate_cluster_transactions(nodes, dbname, stanza):
    """
    Terminates active transactions across the cluster.
    """
    utilx.echo_action("Terminating cluster transactions")

    cmd = "SELECT spock.terminate_active_transactions();"
    for node in nodes:
        util.psql_cmd_output(cmd, f"{node['path']}/pgedge/pgedge", dbname,
                              stanza, host=node["ip_address"],
                              usr=node["os_user"], key=node["ssh_key"])
    utilx.echo_action("Cluster transactions terminated successfully", "ok")

def set_cluster_readonly(nodes, readonly, dbname, stanza):
    """
    Sets or unsets readonly mode on a PostgreSQL cluster across multiple nodes.
    """
    action = "Setting" if readonly else "Removing"
    func_call = ("spock.set_cluster_readonly()" if readonly
                 else "spock.unset_cluster_readonly()")

    utilx.echo_action(f"{action} readonly mode from cluster")

    cmd = f"SELECT {func_call};"

    for node in nodes:
        util.psql_cmd_output(cmd, f"{node['path']}/pgedge/pgedge", dbname,
                              stanza, host=node["ip_address"],
                              usr=node["os_user"], key=node["ssh_key"])
    utilx.echo_action(f"{action} readonly mode from cluster", "ok")

def check_cluster_lag(n, dbname, stanza):
    """
    Monitors the replication lag of a new cluster node until it catches up.
    """
    utilx.echo_action("Checking lag time of new cluster")

    cmd = """
    SELECT
        pg_last_wal_receive_lsn() AS last_receive_lsn,
        pg_last_wal_replay_lsn() AS last_replay_lsn,
        pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) 
            AS lag_bytes
    """

    lag_bytes = 1
    while lag_bytes > 0:
        time.sleep(1)
        op = util.psql_cmd_output(
            cmd, f"{n['path']}/pgedge/pgedge", dbname, stanza,
            host=n["ip_address"], usr=n["os_user"], key=n["ssh_key"]
        )
        last_receive_lsn, last_replay_lsn, lag_bytes = parse_query_output(op)
    utilx.echo_action("Checking lag time of new cluster", "ok")

def manage_node(node, action):
    """
    Starts or stops a cluster based on the provided action.
    """
    if action not in ['start', 'stop']:
        raise ValueError("Invalid action. Use 'start' or 'stop'.")

    action_message = "Starting" if action == 'start' else "Stopping"
    utilx.echo_action(f"{action_message} new node")

    # Construct the command based on the action
    if action == 'start':
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge config pg16 --port={node['port']}; "
               f"./pgedge start")
    else:
        cmd = (f"cd {node['path']}/pgedge/; "
               f"./pgedge stop")

    # Execute the command
    utilx.echo_cmd(cmd, host=node["ip_address"], usr=node["os_user"], 
                   key=node["ssh_key"])
    utilx.echo_action(f"{action_message} new node", "ok")


def parse_query_output(output):
    # Split the output into lines
    lines = output.split('\n')
    
    # Find the line with the data (usually the third line if formatted as shown)
    data_line = lines[2].strip()
    
    # Split the data line into parts
    parts = data_line.split('|')
    
    # Trim whitespace and assign to variables
    last_receive_lsn = parts[0].strip()
    last_replay_lsn = parts[1].strip()
    lag_bytes = int(parts[2].strip())  # Convert lag_bytes to an integer
    
    # Return the parsed values
    return last_receive_lsn, last_replay_lsn, lag_bytes

