import sys, os, util_test, subprocess, json

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
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")


#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {cluster_name} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")


new_address_0 = '127.0.0.1'
new_address_1 = '127.0.0.1'
new_port_0 = '6435'
new_port_1 = '6437'
new_path_0 = 'one'
new_path_1 = 'two'


with open(f"{cluster_dir}/{cluster_name}.json", 'r') as file:
    data = json.load(file)
    #print(data)
    data["remote"]["os_user"] = repuser
    data["node_groups"]["remote"][0]["nodes"][0]["ip_address"] = new_address_0
    data["node_groups"]["remote"][1]["nodes"][0]["ip_address"] = new_address_1
    data["node_groups"]["remote"][0]["nodes"][0]["port"] = new_port_0
    data["node_groups"]["remote"][1]["nodes"][0]["port"] = new_port_1
    data["node_groups"]["remote"][0]["nodes"][0]["path"] = new_path_0
    data["node_groups"]["remote"][1]["nodes"][0]["path"] = new_path_1

newdata = json.dumps(data, indent=4)
with open(f"{cluster_dir}/{cluster_name}.json", 'w') as file:
    file.write(newdata)
    


command = (f"cluster init {cluster_name}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
print(f"init = {init.stdout}\n")
print("*"*100)


# Needle and Haystack
# Confirm the command worked by looking for:

if "\nSyntaxError" not in str(init.stdout) or init.returncode == 1:

    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS



