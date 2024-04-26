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

n2_port=port+1

# Connect to each node and drop the foo table:
drop_n1_table = util_test.write_psql("DROP TABLE IF EXISTS foo CASCADE",host,dbname,port,pw,usr)
print("*"*100)

# Connect to n1 and confirm the foo table is gone:
confirm_n1_table_gone = util_test.read_psql("SELECT * FROM pg_tables WHERE tablename = 'foo';",host,dbname,port,pw,usr)
print("*"*100)

# Connect to each node and drop the foo table:
drop_n2_table = util_test.write_psql("DROP TABLE IF EXISTS foo CASCADE",host,dbname,n2_port,pw,usr)
print("*"*100)

# Connect to n2 and confirm the foo table is gone:
confirm_n2_table_gone = util_test.read_psql("SELECT * FROM pg_tables WHERE tablename = 'foo';",host,dbname,n2_port,pw,usr)
print("*"*100)

# Needle and Haystack
# Confirm the test works by looking for 'foo' in pg_tables:
if "foo" in str(confirm_n2_table_gone) or "foo" in str(confirm_n1_table_gone):
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS



