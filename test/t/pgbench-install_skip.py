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

# confirm that if the pgbench tables already exist, pgbench-install does not overwrite the tables.

#checks whether pgbench istalled or not
row = util_test.read_psql("SELECT * FROM information_schema.tables WHERE table_name='pgbench_accounts'",host,dbname,port,pw,usr).strip("[]")
check=util_test.contains((row),"pgbench_accounts")
print(check)
print("*"*100)

#pgbenchinstall
def pgbenchinstall():
	cmd_node = f"app pgbench-install {dbname}"
	res=util_test.run_cmd("running pgbench-install", cmd_node, f"{cluster_dir}/n1")
	print(res)
	print("*"*100)


if(check==0):
	print("installs pgbench")	
	pgbenchinstall()
	
elif(check==1):
	print("skip installing pgbench")
	


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


