import sys, os, util_test,subprocess



## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")

for i in range(1,num_nodes+1):

##Drop Node
  
  print("Node Drop")
  cmd_spock=f"~/work/nodectl/test/pgedge/cluster/demo/n{i}/pgedge/nodectl spock node-drop n{i} {db}"
  #util_test.run_cmd("Node Drop",cmd_spock,f"{cluster_dir}/n{i}")
  result = subprocess.run(cmd_spock, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Print the output
  print("Output of cmd_spock:")
  print("Result of stdout=",result.stdout)

 # Check if there were any errors
  if result.returncode != 0:
   print("Error occurred:")
   print(result.stderr)
   sys.exit(1)
   
  ## Needle and Haystack check 
   ##Get Needle in Haystack
   
  haystack=result.stdout
  needle = os.getenv("EDGE_NODE_DROP")
  result = util_test.contains(haystack, needle)
  print("Result:", result)	

   

  port=port+1
 


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

