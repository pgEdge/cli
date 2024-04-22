import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

# Get environment variables
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
db=os.getenv("EDGE_DB","lcdb")

## Create Node - Missing args
cmd_node = f"spock node-create"
res=util_test.run_cmd("Node Create", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr :
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Create - Missing Args", 1) 

## Create Node - Wrong User
cmd_node = f"spock node-create n1 'host=127.0.0.1 port={port} user={usr} dbname={db}' {db}"
res=util_test.run_cmd("Node Create", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "is not a replication user" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Create - Wrong User", 1) 
    
## Node Drop - Missing args
cmd_node = f"spock node-drop"
res=util_test.run_cmd("Node Drop", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr :
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Drop - Missing Args", 1) 

## Sub Create - Missing args
cmd_node = f"spock sub-create"
res=util_test.run_cmd("Sub Create", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr :
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Create - Missing Args", 1) 

## Sub Create - Wrong User
cmd_node = f"spock sub-create sub_n1n2 'host=127.0.0.1 port={port + 1} user={usr} dbname={db}' {db}"
res=util_test.run_cmd("Sub Create", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "is not a replication user" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Create", 1) 
            
## Sub Drop - Missing args
cmd_node = f"spock sub-drop"
res=util_test.run_cmd("Sub Drop", cmd_node, f"{cluster_dir}/n1")
print(res)
if res.returncode == 0 or "ERROR" not in res.stderr :
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Drop - Missing Args", 1) 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 
