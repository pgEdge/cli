import sys, os, util_test

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()


## Get Test Settings
#util_test.get_pg_con()

##Get Needle in Haystack
#util_test.needle_in_haystack(haystack,needle)
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",3))
print(num_nodes)
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
#usr=os.getenv("EDGE_USERNAME","admin")
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
needle_node=os.getenv("EDGE_NODE_CHECK","node_create")
needle_repset=os.getenv("EDGE_REPSET_CHECK","demo-repset")
i=1

## Build Cluster
print("Creating node directories")
while i<=num_nodes:
	cmd=f"SELECT * FROM spock.replication_set WHERE set_name='demo-repset'" 
	print(cmd) 
	con=util_test.get_pg_con(host,db,port,pw,usr)
	val=util_test.run_psql(cmd, con)
	print(val)
	port+=1
	i+=1

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)




