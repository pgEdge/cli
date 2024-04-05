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
# Confirm that db guc-set throws an ERROR if the user tries to set a GUC to an invalid value of the correct type.
# 
command = "db guc-set authentication_timeout 601"
res=util_test.run_cmd("Setting authentication_timeout to 601 (the high threshold is 600).", command, f"{cluster_dir}/n1")
print(res)
print("*"*100)
#
# Needle and Haystack
# Confirm the command works by looking for the word ERROR in stderr:
value = util_test.read_psql("SHOW client_min_messages;",host,dbname,port,pw,usr).strip("[]")
check=util_test.contains((res.stderr),"ERROR")
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

