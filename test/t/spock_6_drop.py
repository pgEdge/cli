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
            cmd_node = f"spock sub-drop sub_n{n}n{z} {db}"
            res=util_test.run_cmd("Sub Drop", cmd_node, f"{cluster_dir}/n{n}")
            print(res)
            if res.returncode == 1 or "sub_drop" not in res.stdout:
    	        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Drop", 1) 
            port = port + 1

port=int(os.getenv("EDGE_START_PORT",6432))
for n in range(1,num_nodes+1):
    ## Create Nodes
    cmd_node = f"spock node-drop n{n} {db}"
    res=util_test.run_cmd("Node Drop", cmd_node, f"{cluster_dir}/n{n}")
    print(res)
    if res.returncode == 1 or "node_drop" not in res.stdout:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Drop", 1) 
    port = port + 1

port=int(os.getenv("EDGE_START_PORT",6432))
for n in range(1,num_nodes+1):
    cmd_node = f"app pgbench-remove {db}"
    res=util_test.run_cmd("Remove pgbench", cmd_node, f"{cluster_dir}/n{n}")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 