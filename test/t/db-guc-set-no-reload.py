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
# Confirm that a parameter value remains unchanged if db guc-set changes a variable that requires a reset.
# 

# Check the value before the command:
value_before = util_test.read_psql("SHOW max_connections;",host,dbname,port,pw,usr).strip("[]")

# Use db guc-set to change the value of max_connections (a parameter that requires a reset to take effect)
command = "db guc-set max_connections 259"
res=util_test.run_cmd("Using db guc-set to set max_connections to 259.", command, f"{cluster_dir}/n1")

print("*"*100)
#
# Check the value after the command:
value_after = util_test.read_psql("SHOW max_connections;",host,dbname,port,pw,usr).strip("[]")

# Needle and Haystack
# Confirm the command works by taking a count from pg_settings and comparing it to the count of rows returned by db guc-show:

# Compare the value of max_connections before and after:
if value_before == value_after:
    print(f"result code returned by db guc-set = {res}")
    print(f"max_connections value_before = {value_before}")
    print(f"max_connections value_after = {value_after}")

    util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
else:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)}", 1)



