import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

# Get environment variables
num_nodes = int(os.getenv("EDGE_NODES", 2))
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","lcpasswd")
db=os.getenv("EDGE_DB","lcdb")
host=os.getenv("EDGE_HOST","localhost")

## Modify Tables on n1
cmd_psql = ("INSERT INTO pgbench_tellers VALUES (11,1,0,'INSERT statement')")
res=util_test.write_psql(cmd_psql,host,db,port,pw,usr)

cmd_psql = ("UPDATE pgbench_tellers SET filler='UPDATE statement' WHERE tid = 1")
res=util_test.write_psql(cmd_psql,host,db,port,pw,usr)

cmd_psql = ("DELETE FROM pgbench_tellers WHERE tid = 2")
res=util_test.write_psql(cmd_psql,host,db,port,pw,usr)

cmd_psql = ("TRUNCATE pgbench_accounts")
res=util_test.write_psql(cmd_psql,host,db,port,pw,usr)

## Check Results on n2
port = port + 1

cmd_psql = ("SELECT * FROM pgbench_tellers WHERE tid = 11")
res=util_test.read_psql(cmd_psql,host,db,port,pw,usr)
print("Expecting - 11, 1, 0, INSERT statement -" + res)
if "INSERT" not in res:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Replicate Insert", 1) 

cmd_psql = ("SELECT * FROM pgbench_tellers WHERE tid = 1")
res=util_test.read_psql(cmd_psql,host,db,port,pw,usr)
print("Expecting - 1, 1, 0, UPDATE statement -" + res)
if "UPDATE" not in res:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Replicate Update", 1)

cmd_psql = ("SELECT * FROM pgbench_tellers WHERE tid = 2")
res=util_test.read_psql(cmd_psql,host,db,port,pw,usr)
print("Expecting no results - " + res)
if "[]" not in res:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Replicate Delete", 1)

cmd_psql = ("SELECT * FROM pgbench_accounts LIMIT 5")
res=util_test.read_psql(cmd_psql,host,db,port,pw,usr)
print("Expecting no results - " + res)
if "[]" not in res:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Replicate Truncate", 1)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 