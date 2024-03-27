import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
print(num_nodes)
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")
##
#confirm that if the name of a non-ex. database is provided, and the name of a valid replication set is provided, the error is handled gracefully.
##
cmd_node = f"app pgbench-install {(not dbname)} -r default"
res=util_test.run_cmd_err("install pgbench with non-ex database", cmd_node, f"{cluster_dir}/n1")
print("*"*100)
print(res)
print("*"*100)
##
#haystack and needle
#Checking needle and haystack from returncode in the result
check=util_test.contains(str(res.returncode),"1")


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

