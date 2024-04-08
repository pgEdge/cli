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
# Check for "my_interface", and drop it if it exists; then we'll use spock node-add-interface to drop it. This way we can play the tests out of order.
# 
check_value = util_test.read_psql("select * from spock.node_interface;",host,dbname,port,pw,usr).strip("[]")
if "my_interface" in str(check_value):
    drop_interface = "spock node-drop-interface n1 my_interface lcdb"
    drop=util_test.run_cmd("Run spock node-drop-interface.", add_interface, f"{cluster_dir}/n1")
    print(f"Print drop.stdout here: - {drop.stdout}")
print("*"*100)

command = "spock node-add-interface n1 my_interface 'host=127.0.0.1 user=lcusr dbname=lcdb' lcdb"
res=util_test.run_cmd("Run spock node-add-interface.", command, f"{cluster_dir}/n1")
print(f"Print res.stdout here: - {res.stdout}")
print("*"*100)

# Needle and Haystack
# Confirm the test works by looking for 'my_interface' with psql:
psql_value = util_test.read_psql("select * from spock.node_interface;",host,dbname,port,pw,usr).strip("[]")
if "my_interface" in str(psql_value):
    util_test.EXIT_PASS
else:
    util_test.EXIT_FAIL

print("*"*100)

