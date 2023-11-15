import sys, os, util_test

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

##Get Needle in Haystack
#util_test.needle_in_haystack(haystack,needle)
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",3))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
needle_node=os.getenv("EDGE_NODE_CHECK","node_create")
needle_repset=os.getenv("EDGE_REPSET_CHECK","demo-repset")

#print(node-list)

i=1
cmd_spock=f"spock node-list  {db}"
val=util_test.run_cmd("Node-list",cmd_spock,f"{cluster_dir}/n{i}")
print(val)
	
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)



