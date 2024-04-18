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

for n in range(1,num_nodes+1):

    cmd_node = f"app pgbench-install {db}"
    res=util_test.run_cmd("Install pgbench", cmd_node, f"{cluster_dir}/n{n}")
    cmd_psql = ("ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true);"
                + "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true);"
                + "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)" )
    res=util_test.write_psql(cmd_psql,host,db,port,pw,usr)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 