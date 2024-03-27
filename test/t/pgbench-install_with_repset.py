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
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

## pgbench-install
## CONFIRM that if a database name and repset name are provided, pgbench is installed as expected and the transactions are added to the repset
cmd_node = f"app pgbench-install {dbname} -r default"
res=util_test.run_cmd("running pgbench-install including repsetname", cmd_node, f"{cluster_dir}/n1")
##
## confirm with SELECT * FROM spock.replication_set_table.
cmd=f"SELECT * FROM spock.replication_set" 
con=util_test.get_pg_con(host,db,port,pw,usr)
val=util_test.run_psql(cmd, con)
#print(val)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

