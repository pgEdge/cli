import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

# Get environment variables
num_nodes = int(os.getenv("EDGE_NODES", 2))
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
repuser=os.getenv("EDGE_REPUSER","pgedge")
pw=os.getenv("EDGE_PASSWORD","lcpasswd")
db=os.getenv("EDGE_DB","lcdb")
host=os.getenv("EDGE_HOST","localhost")

for n in range(1,num_nodes+1):
    ## Create Nodes
    cmd_node = f"spock node-create n{n} 'host=127.0.0.1 port={port} user={repuser} dbname={db}' {db}"
    res=util_test.run_cmd("Node Create", cmd_node, f"{cluster_dir}/n{n}")
    print(res)
    if res.returncode == 1 or "node_create" not in res.stdout:
    	util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Create", 1) 
    port = port + 1

## Metrics Check Test
cmd_node = f"spock metrics-check {db}"
res=util_test.run_cmd("Metrics Check", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 1 or "mount_point" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Metrics Check", 1) 

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 