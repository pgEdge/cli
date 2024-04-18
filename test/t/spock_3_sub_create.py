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

port_array = []
for n in range(1,num_nodes+1):
    port_array.append(port)
    port = port + 1

for n in range(1,num_nodes+1):
    for z in range(1,num_nodes+1):
        if n!=z:
            ## Create Subs
            cmd_node = f"spock sub-create sub_n{n}n{z} 'host=127.0.0.1 port={port_array[z-1]} user={repuser} dbname={db}' {db}"
            res=util_test.run_cmd("Sub Create", cmd_node, f"{cluster_dir}/n{n}")
            print(res)
            if res.returncode == 1 or "sub_create" not in res.stdout:
    	        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Create", 1) 
            port = port + 1

## Sub Show Status Test
cmd_node = f"spock sub-show-status sub_n1n2 {db}"
res=util_test.run_cmd("Sub Show Status", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 1 or "replicating" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Status", 1) 

## Node List Test
cmd_node = f"spock node-list {db}"
res=util_test.run_cmd("Node List", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 1 or "n2" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node List", 1) 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 