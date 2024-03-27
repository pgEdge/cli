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

## northwind-validate
## northwind-validate is called with a valid database name, a result that includes the sum of units on order and in stock is returned. 
cmd_node = f"app northwind-validate {dbname}"
res=util_test.run_cmd("validate northwind", cmd_node, f"{cluster_dir}/n1")
print(res)
print("*"*100)
#
#haystack and needle
#confirm with SELECT count(*) FROM northwind.products
row = util_test.read_psql("select sum(units_on_order) From northwind.products;",host,dbname,port,pw,usr).strip("[]")
check=util_test.contains(res.stdout,row)
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)





