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
offset=os.getenv("EDGE_OFFSET",1)
##
## The command invokes the northwind-run app and iterates through a list of orders.
##specifying ratevalue and timevalue
cmd_node = f"app northwind-run {dbname} {offset} {rate} {time}"
res=util_test.run_cmd("northwind install", cmd_node, f"{cluster_dir}/n1")
print(res)
print("*"*100)

##
#haystack and needle
#Checking needle and haystack from returncode in the result
check=util_test.contains(res.stdout,"Finished running Northwind App")
print("*"*100)


	
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

