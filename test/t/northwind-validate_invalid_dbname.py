import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

nodbname="edokatinikenduku"

##Demonstrate that if northwind-validate is called with an invalid database name, the error is handed gracefully.
cmd_node = f"app northwind-validate {noddbname}"
res=util_test.run_cmd("validate northwind providing non-ex dbname", cmd_node, f"{cluster_dir}/n1")
print(res)
print("*"*100)

##
#haystack and needle
check=util_test.contains(str(res.returncode),"1")
print("*"*100)

##
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)





