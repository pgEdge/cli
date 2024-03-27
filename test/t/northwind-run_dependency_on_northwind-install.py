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
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

rate=2
time=1
offset=1

#Demonstrate that if you call northwind-run before northwind-install the error is handled gracefully.
def northwindrun():
	cmd_node = f"app northwind-run {dbname} {offset} {rate} {time}"
	res=util_test.run_cmd("northwind run", cmd_node, f"{cluster_dir}/n1")
	print(res)
	print("*"*100)
	check=util_test.contains(str(res.returncode),"1")
	print("*"*100)

northwindrun()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)



