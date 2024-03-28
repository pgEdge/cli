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
usr=os.getenv("EDGE_USERNAME","lahari")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

#pgbench-remove should not effect the table pgbench_foo

#creates table pgbench_foo
row = util_test.write_psql("CREATE TABLE pgbench_foo (did integer PRIMARY KEY, name varchar(40));",host,dbname,port,pw,usr)
print(row)
print("*"*100)

#Removes pgbench and confirms only table pgbench_foo remains
if (row==0):
	cmd_node = f"app pgbench-remove {dbname}"
	res=util_test.run_cmd("Removing pgbench", cmd_node, f"{cluster_dir}/n1")
	print(res)
	print("*"*100)
	row = util_test.read_psql("SELECT * FROM information_schema.tables WHERE table_name='pgbench_foo'",host,dbname,port,pw,usr).strip("[]")
	check=util_test.contains((row),"pgbench_foo")
	


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


