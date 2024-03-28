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
rate=os.getenv("EDGE_RATE","2")
time=os.getenv("EDGE_TIME",10)

#confirm that pgbench-validate errors gracefully if the command is invoked before pgbench-install is run.


## pgbench-validate
## CONFIRM that the command performs as expected if you provide a valid db name. 
def pgbenchvalidate():
	cmd_node = f"app pgbench-validate {dbname}"
	res=util_test.run_cmd("validating pgbench", cmd_node, f"{cluster_dir}/n1")
	print(res)
	print("*"*100)
	

pgbenchvalidate()


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)




