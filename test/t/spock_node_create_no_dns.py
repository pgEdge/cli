# This test case tests what happens if a node name is not provided when creating a node.

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
# Check for "n1", and drop it if it exists; then we'll use spock node-create to create errors. This way we can play the tests out of order.
# 
check_value = util_test.read_psql("select * from spock.node;",host,dbname,port,pw,usr).strip("[]")
print(f"Check value is: {check_value}")

if "n1" in str(check_value):
    drop_node = f"spock node-drop n1 {dbname}"
    drop=util_test.run_cmd("Run spock node-drop.", drop_node, f"{cluster_dir}/n1")
    print(f"Print drop.stdout here: - {drop.stdout}")
print("*"*100)

# Invoke spock node-create, but don't specify a node name:

command = f"spock node-create n1 {dbname}"
res=util_test.run_cmd("Run spock node-create.", command, f"{cluster_dir}/n1")
print(f"Print res.stderr here: - {res.stderr}")

print("*"*100)

# Needle and Haystack
# Confirm the test works by looking for 'ERROR' in res:
if "ERROR" in str(res):
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS

print("*"*100)



