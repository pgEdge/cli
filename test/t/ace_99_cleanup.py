import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

num_nodes=int(os.getenv("EDGE_NODES",2))
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")

for n in range(1,num_nodes+1):
    #DROP table matching
    row = util_test.write_psql("DROP TABLE foo CASCADE",host,dbname,port,pw,usr)

    #DROP table - data diff
    row = util_test.write_psql("DROP TABLE foo_diff_data CASCADE",host,dbname,port,pw,usr)

    #DROP table - row diff
    row = util_test.write_psql("DROP TABLE foo_diff_row CASCADE",host,dbname,port,pw,usr)

    #DROP table - no primarykey
    row = util_test.write_psql("DROP TABLE foo_nopk CASCADE",host,dbname,port,pw,usr)

    print(f"Drop tables on n{n}")
    port = port + 1

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)