import os, util_test, subprocess, pathlib
# Get environment variables

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

#Use the spock-diff command to compare the meta-data on two cluster nodes
cmd_node = f"ace spock-diff {cluster} all"
res=util_test.run_cmd("spock-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "Replication Rules are the same'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - spock-diff", 1) 


#Use the diff-schemas command to compare the schemas in a cluster 
cmd_node = f"ace schema-diff {cluster} all public"
res=util_test.run_cmd("schema-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "SCHEMAS ARE THE SAME'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - spock-diff", 1) 

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
