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
