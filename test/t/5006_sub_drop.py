import sys, os, util_test,subprocess


## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",3))
print("Number of Nodes=",num_nodes)
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
				cmd = f"spock sub-drop sub_n{i}n{j} {db}"
				res=util_test.run_cmd("Create Subscriptions",cmd,f"{cluster_dir}/n{i}")
				haystack=res.stdout
				needle=os.getenv("EDGE_SUB_DROP","sub_drop")
				print("needle is",needle)
				##Get Needle in Haystack
				res=util_test.contains(haystack,needle)
			
	port=port1-1
	#print(port)
			
 
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
