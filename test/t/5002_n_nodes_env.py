import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()


##Get Needle in Haystack

#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",3))
print(num_nodes)
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")



## Build Cluster
print("Creating node directories")
i=1
while i<=num_nodes:
	cmd = f"mkdir -p {cluster_dir}/n{i}"
	rc = os.system(str(cmd))
	print("Download pgEdge")
	cmd = f"cd {cluster_dir}/n{i}; python3 -c \"$(curl -fsSL {repo})\""
	rc = os.system(str(cmd))
	print("Install Nodes")
	cmd=f"install pgedge -U {usr} -P {pw} -d {db} -p {port}"
	util_test.run_cmd("Install Nodes", cmd, f"{cluster_dir}/n{i}")
	print("node-create")
	cmd_spock=f"~/work/nodectl/test/pgedge/cluster/demo/n{i}/pgedge/nodectl spock node-create n{i} 'host={host} port={port} user={repuser} dbname={db}' {db}"
	print (cmd_spock)
	result = subprocess.run(cmd_spock, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
# Print the output
	print("Output of cmd_spock:")
	print("Result of stdout=",result.stdout)
    
# Check if there were any errors
	if result.returncode != 0:
		print("Error occurred:")
		print(result.stderr)
		sys.exit(1)
	
	haystack=result.stdout
	needle=os.getenv("EDGE_NODE_CHECK","node_create")
	print("needle is",needle)

##Get Needle in Haystack
	res=util_test.contains(haystack,needle)
	print(res)
	
## Repset Creation
	
	print("Repset-create")
	cmd_repset=f"~/work/nodectl/test/pgedge/cluster/demo/n{i}/pgedge/nodectl spock repset-create {repset} {db}"
	print(cmd_repset)
	result2 = subprocess.run(cmd_repset, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)	
	
# Print the output
	print("Output of cmd_repset:")
	print("Result of stdout=",result2.stdout)
    	
# Check if there were any errors
	if result2.returncode != 0:
		print("Error occurred:",result2.stderr)
		sys.exit(1)
	
	haystack=result2.stdout
	needle = os.getenv("EDGE_REP_CHECK","repset_create")
	result = util_test.contains(haystack, needle)
	print("Result:", result)
    		
	port+=1
	i+=1
	
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

