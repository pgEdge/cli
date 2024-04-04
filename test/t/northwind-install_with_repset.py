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

## northwind-install
#CONFIRM that if you run northwind-install with valid database and repset names, the command is successful.
cmd_node = f"app northwind-install {dbname} default"
res=util_test.run_cmd("install northwind with valid db and repset name", cmd_node, f"{cluster_dir}/n1")
print(res)
print("*"*100)
#
#haystack and needle
#confirm with SELECT * FROM information_schema.tables WHERE table_name='categories'
row = util_test.read_psql("SELECT * FROM spock.tables;",host,dbname,port,pw,usr).strip("[]")
check=util_test.contains((row),"default")
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

