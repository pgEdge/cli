import sys, os, util_test

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")

## Build Cluster
print("Creating node directories")
for i in range(1,num_nodes+1):
  cmd = f"mkdir -p {cluster_dir}/n{i}"
  rc = os.system(str(cmd))

print("Download pgEdge")
for i in range(1,num_nodes+1):
  cmd = f"cd {cluster_dir}/n{i}; python3 -c \"$(curl -fsSL {repo})\""
  rc = os.system(str(cmd))

print("Install Nodes")
for i in range(1,num_nodes+1):
  cmd=f"install pgedge -U {usr} -P {pw} -d {db} -p {port}"
  util_test.run_cmd("Install Nodes", cmd, f"{cluster_dir}/n{i}")
  cmd_spock=f"spock node-create n{i} 'host={host} port={port} user={repuser} dbname={db}' {db}"
  util_test.run_cmd("Register Nodes",cmd_spock,f"{cluster_dir}/n{i}")
  port=port+1

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)