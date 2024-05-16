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
seconds=int(os.getenv("EDGE_SLEEP"))

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

# We're not going to create the table on n2; instead, we'll create the subscription with --synchronize-struct=True to pull the structure over.
command = (f"spock sub-create sub_n2n1 'host={host} port={port} user={repuser} dbname={dbname}' {dbname} --synchronize_structure=True")
sub_create=util_test.run_cmd("Run spock sub-create sub_n2n1.", command, f"{cluster_dir}/n2")
print(f"The spock sub-create command for sub_n2n1 returned: {sub_create.stdout}")
print("*"*100)

# Napping
time.sleep(seconds)

# Check for public.foo in pg_tables:
rep_check = util_test.read_psql("SELECT * FROM pg_tables WHERE schemaname = 'public';",host,dbname,n2_port,pw,usr)

# Needle and Haystack
# Confirm the test works by looking for 'foo' in rep_check:
if "foo" not in str(rep_check) or sub_create.returncode ==1:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS






