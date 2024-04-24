import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir = os.getenv("NC_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")
cluster=os.getenv("EDGE_CLUSTER","demo")
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
pg = os.getenv("EDGE_INST_VERSION")

cmd_node = f"cluster json-template {cluster} {dbname} {num_nodes} {usr} {pw} {pg} {port}"
res=util_test.run_cmd("Gen JSON", cmd_node, f"{home_dir}")
if res.returncode == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node Create", 1) 

n = 1
new_port = port
test_dir = os.getcwd()
with open(f"{cluster_dir}/{cluster}.json", "rt") as fin:
    with open(f"{cluster_dir}/{cluster}_1.json", "w") as fout:
        for line in fin:
            if "\"ip_address\": \"\"" in line:
                fout.write(line.replace("\"\"",f"\"{host}\""))
            elif "\"path\": \"" in line:
                fout.write(line.replace("\"\"",f"\"{test_dir}/{cluster_dir}/n{n}\""))
                n = n + 1
            elif "\"port\":" in line:
                if n != 1: 
                    fout.write(line.replace(f"{port}",f"{new_port}"))
                else:
                    fout.write(line)
                new_port = new_port + 1
            else:
                fout.write(line)

rc = os.system(f"mv {cluster_dir}/{cluster}_1.json {cluster_dir}/{cluster}.json")    
       
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
