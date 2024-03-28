import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

##Get Needle in Haystack
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

#pgbench-remove
##CONFIRM that pgbench-remove removes the pgbench tables that pgbench-install loads from the specified database.
cmd_node = f"app pgbench-remove {dbname}"
res=util_test.run_cmd("Removing pgbench", cmd_node, f"{cluster_dir}/n1")
print(res)
print("*"*100)

#haystack and needle
#confirm with SELECT * FROM information_schema.tables WHERE table_name='pgbench_accounts'
row = util_test.read_psql("SELECT * FROM information_schema.tables WHERE table_name='pgbench_accounts'",host,dbname,port,pw,usr)
check=util_test.contains(res.stdout,"Dropped pgBench tables from database")
print("*"*100)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

