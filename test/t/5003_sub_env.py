import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",3))
print("Number of node=",num_nodes)
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
#print(port)
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")


port1=port
#print(port1)
c=1
for i in range(c,num_nodes+1):
	for j in range(c,num_nodes+1):
		if(i==c and j==c):
			continue
		else:
			
			if(i==j):
				port+=1
				#print(port,"for same nodes")
			else:
				#print("b4 cmd",i,j,port)
				port+=1
				cmd = f"~/work/nodectl/test/pgedge/cluster/demo/n{i}/pgedge/nodectl spock sub-create sub_n{i}n{j} 'host={host} port={port} user={repuser} dbname={db}' {db}"
				#util_test.run_cmd("Create Subscriptions",cmd,f"{cluster_dir}/n{i}")
				#print("After cmd",i,j,port)
				print(cmd)
				#util_test.run_cmd("Create Subscriptions",cmd,f"{cluster_dir}/n{i}")
				#print("After cmd",i,j,port)
				
				result1 = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
# Check if there were any errors
				if result1.returncode != 0:
					print("Error occurred:",result1.stderr)
					sys.exit(1)	

# Print the output

				print("Result of stdout=",result1.stdout)
				haystack=result1.stdout
				needle=os.getenv("EDGE_SUB_CHECK")

# Check if the needle is present in the haystack
				result = util_test.contains(haystack, needle)
				print("Result:", result)

				
	port=port1-1
	#print(port)

         
     
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
