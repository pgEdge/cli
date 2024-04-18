import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

# Get environment variables
num_nodes = int(os.getenv("EDGE_NODES", 2))
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
db=os.getenv("EDGE_DB","lcdb")

for n in range(1,num_nodes+1):
    ## Add Tables to Repset
    cmd_node = f"spock repset-add-table default '*' {db}"
    res=util_test.run_cmd("Repset Add Table", cmd_node, f"{cluster_dir}/n{n}")
    print(res)
    if res.returncode == 1 or "Adding table" not in res.stdout:
    	util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Repset Add Table", 1) 

## Repset List Tables Test
cmd_node = f"spock repset-list-tables public {db}"
res=util_test.run_cmd("Repset List Tables", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 1 or "pgbench_accounts" not in res.stdout or "default" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Repset List Tables", 1) 

## Sub Show Table Test
cmd_node = f"spock sub-show-table sub_n1n2 pgbench_accounts {db}"
res=util_test.run_cmd("Sub Show Table", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 1 or "pgbench_accounts" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Table", 1) 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 