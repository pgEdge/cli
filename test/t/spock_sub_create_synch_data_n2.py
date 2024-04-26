import sys, os, util_test, subprocess, time

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

n2_port = port + 1

print(f"port (n1) is set to {port}")
print(f"n2_port is set to {n2_port}")

# Check for n2, and drop it if it exists.
check_node = util_test.read_psql("select * from spock.node;",host,dbname,n2_port,pw,usr).strip("[]")

if "n2" in str(check_node):
    drop_node = f"spock node-drop n2 {dbname}"
    drop=util_test.run_cmd("Run spock node-drop.", drop_node, f"{cluster_dir}/n2")
    print(f"Print drop.stdout here: - {drop.stdout}")
print("*"*100)

# Create a new n2:
command = (f"spock node-create n2 'host={host} user={repuser} dbname={dbname} port={n2_port}' {dbname}")
res=util_test.run_cmd("Run spock node-create.", command, f"{cluster_dir}/n2")
print(f"spock node-create n2 returned: {res.stdout}")
print("*"*100)

# Define a table named foo - this should echo back 'CREATE TABLE'
create_table = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo (empid INT PRIMARY KEY, empname varchar(40))",host,dbname,n2_port,pw,usr)
print(f"We just CREATED the table on n2: {create_table}")
print("*"*100)

# We've created the table, but we're not going to add the data on n2; instead, we'll create the subscription with --synchronize-data=True to pull the data over.
command = (f"spock sub-create sub_n2n1 'host={host} port={port} user={repuser} dbname={dbname}' {dbname} --synchronize_data=True")
sub_create=util_test.run_cmd("Run spock sub-create sub_n2n1.", command, f"{cluster_dir}/n2")
print(f"The spock sub-create command for sub_n2n1 returned: {sub_create.stdout}")
print("*"*100)

# Napping
time.sleep(3)

# Check for a user that was added to n1 in n2's public.foo:
read_foo = util_test.read_psql("SELECT * FROM public.foo;",host,dbname,n2_port,pw,usr)
print(f"The foo table contains: {read_foo}")

if "Alice" in str(read_foo):
    util_test.EXIT_PASS
else:
    util_test.EXIT_FAIL



