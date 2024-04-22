import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

# Get environment variables
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
repuser=os.getenv("EDGE_REPUSER","pgedge")

## Repset List Tables Test
cmd_node = f"spock repset-list-tables"
res=util_test.run_cmd("Repset List Tables", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr :
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Repset List Tables", 1) 

## Sub Show Table Test
cmd_node = f"spock sub-show-table"
res=util_test.run_cmd("Sub Show Table", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Table", 1) 

## Sub Show Status Test
cmd_node = f"spock sub-show-status"
res=util_test.run_cmd("Sub Show Status", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Status", 1) 

## Node List Test
cmd_node = f"spock node-list"
res=util_test.run_cmd("Node List", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node List", 1) 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)