import sys, os, util_test,subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")
#
# First, we clean up the environment to remove the subscription if it exists.
# Then, we attempt to create the subscription, but pass a non-repset user in the connection string.

check_value = util_test.read_psql("select sub_replication_sets from spock.subscription;",host,dbname,port,pw,usr).strip("[]")

if "my_test_sub" in str(check_value):
    drop_sub = f"spock sub-drop my_test_sub {dbname}"
    drop=util_test.run_cmd("Run spock sub-drop.", drop_sub, f"{cluster_dir}/n1")
    print(f"Print drop.stdout here: - {drop.stdout}")
print("*"*100)

command = f"spock sub-create my_test_sub 'host={host} port={port} user={usr} dbname={dbname}' {dbname} -r 'this_repset,that_repset,the_other_repset'"
res=util_test.run_cmd("Run spock sub-create -r.", command, f"{cluster_dir}/n1")
print(f"Print our command here: {command}")
print(f"Print res.stdout here: - {res.stdout}")
print("*"*100)

# Needle and Haystack
#Check needle and haystack with res.stdout:
check=util_test.contains(res.stdout,"replication user")
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

