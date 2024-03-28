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
rate=os.getenv("EDGE_RATE","2")
time=os.getenv("EDGE_TIME",10)

#Demonstrate that you cannot invoke pgbench-run until after you've invoked pgbench-install.

def pgbenchrun():
	cmd_node = f"app pgbench-run {dbname} {rate} {time}"
	res=util_test.run_cmd("pgbench-run", cmd_node, f"{cluster_dir}/n1")
	print(res)
	print("*"*100)
	check=util_test.contains(str(res.returncode),"0")
	print("*"*100)


pgbenchrun()


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

