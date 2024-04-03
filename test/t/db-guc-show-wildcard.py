import sys, os, util_test,subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")
#
# Confirm that db guc-show returns a list of parameters that meet a wildcard criteria.
# 
command = "db guc-show share* | grep name | wc -l"

db_show_count=util_test.run_cmd("Querying db guc-show for information about any parameter that meets a wildcard criteria.", command, f"{cluster_dir}/n1")
print(f"stdout = {db_show_count.stdout}")
print("*"*100)

# Needle and Haystack
# Confirm the command works by taking a count from pg_settings and comparing it to the count of rows returned by db guc-show:
psql_count = util_test.read_psql("SELECT COUNT(*) FROM pg_settings WHERE name like 'share%';",host,dbname,port,pw,usr).strip("[]")

# The two values aren't of the same type, so cast them to int() before testing:
if int(db_show_count.stdout) == int(psql_count):
    print(f"db_show_count = {db_show_count}")
    print(f"psql_count = {psql_count}")

    util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
else:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)}", 1)


