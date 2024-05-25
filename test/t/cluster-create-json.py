import sys, os, util_test,subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
pgv=os.getenv("EDGE_INST_VERSION")
num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER","demo")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

file_name = (f"{cluster_name}.json")

#
# Confirm that cluster json-template creates a template file:
# 
print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {cluster_name} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")
print("*"*100)
#
# Needle and Haystack
# Confirm the command works by looking for the file:
path=(f"{cluster_dir}/{file_name}")
file_info = os.stat(f"{path}")
print(f"The file info contains = {file_info}")

if "os.stat_result" not in str(file_info) or res.returncode == 1:

    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS



