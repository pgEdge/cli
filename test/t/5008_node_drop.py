import sys, os, util_test,subprocess



## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")

i=1
while i<=num_nodes:
	print("Node-Drop")
	cmd= f"spock node-drop n{i} {db}"
	res=util_test.run_cmd("node drop",cmd,f"{cluster_dir}/n{i}")
	haystack=res.stdout
	needle=os.getenv("EDGE_NODE_DROP","node_drop")
	print("needle is",needle)
	##Get Needle in Haystack
	res=util_test.contains(haystack,needle)
	port += 1
	i += 1

 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

