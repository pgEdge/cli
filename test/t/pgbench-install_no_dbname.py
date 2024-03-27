
'''
# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(message)s')
'''

import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
##
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
#
#
# CONFIRM that if a database name is omitted, the error is handled gracefully.
cmd_node = f"app pgbench-install"
res=util_test.run_cmd_err("pgbench install without dbname", cmd_node, f"{cluster_dir}/n1")
print("*"*100)
print(res)
print("*"*100)
##
#haystack and needle
#Checking needle and haystack from returncode in the result
check=util_test.contains(str(res.returncode),"1")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)




'''
#confirm that if you do not specify a database name, the northwind-install command fails gracefully.
cmd_node = f"app northwind-install { not dbname}"
res=util_test.run_cmd("local-create", cmd_node, f"{cluster_dir}/n1")

# Check if the database creation failed
if "DB DOES NOT EXIST" in res.stderr:
    print("Error: Database creation failed. 'DB DOES NOT EXIST' message captured.")
    # Handle the error here, you can raise an exception, log the error, or take appropriate action.
    
print(res.returncode)
##
#Haystack and Needle
check=util_test.contains(str(res.returncode),"1")
print(check)
    
'''
    
    
    
    
    
    
    
