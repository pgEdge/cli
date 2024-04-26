import sys, os, util_test,subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()

cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
dbname=os.getenv("EDGE_DB","lcdb")

## Check for n1, and drop it if it exists.
#
check_node = util_test.read_psql("select * from spock.node;",host,dbname,port,pw,usr).strip("[]")
print(f"Check for existence of n1: {check_node}")

if "n1" in str(check_node):
    drop_node = f"spock node-drop n1 {dbname}"
    drop=util_test.run_cmd("Run spock node-drop.", drop_node, f"{cluster_dir}/n1")
    print(f"Print drop.stdout here: - {drop.stdout}")
print("*"*100)

# Create a new n1:
command = f"spock node-create n1 'host={host} user={repuser} dbname={dbname}' {dbname}"
res=util_test.run_cmd("Run spock node-create.", command, f"{cluster_dir}/n1")
print(f"Print res here: - {res}")
print("*"*100)

# Define a table named foo on n1 - this should echo back 'CREATE TABLE'
create_table = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo (empid INT PRIMARY KEY, empname varchar(40))",host,dbname,port,pw,usr)
print("*"*100)

# Add some data to the table:
add_data = util_test.write_psql("INSERT INTO public.foo (empid, empname) VALUES(1,'Alice'), (2, 'Bob'), (3, 'Carol'), (4, 'Duane'), (5, 'Edward'), (6, 'Francis');",host,dbname,port,pw,usr)
print("*"*100)



# Add the table to the 'default' repset.
command = (f"spock repset-add-table default 'public.foo' {dbname}")
repset_add=util_test.run_cmd("Run spock repset-add-table.", command, f"{cluster_dir}/n1")
print(f"Print repset_add here: - {repset_add}")
print("*"*100)





# Needle and Haystack
# Confirm the test works by looking for 'Adding' in res.stdout:
if "Adding" in str(repset_add.stdout):
    util_test.EXIT_PASS
else:
    util_test.EXIT_FAIL






