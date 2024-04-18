import os, util_test, subprocess, pathlib
# Get environment variables

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("EDGE_HOME_DIR")
cluster = os.getenv("EDGE_CLUSTER")

#Use the spock-diff command to compare the meta-data on two cluster nodes
cmd_node = f"ace diff-spock {cluster} n1 n2"
res=util_test.run_home_cmd("spock-diff", cmd_node, f"{home_dir}")
print(res)

#Use the diff-schemas command to compare the schemas in a cluster 
cmd_node = f"ace diff-schema {cluster} n1 n2 public"
res=util_test.run_home_cmd("schema-diff", cmd_node, f"{home_dir}")
print(res)
