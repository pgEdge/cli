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
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")

for n in range(1,num_nodes+1):
    #CREATE table matching
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)


    #CREATE table - data diff
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_diff_data (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    if n==1:
        row = util_test.write_psql("INSERT INTO foo_diff_data (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)
    else:
        row = util_test.write_psql("INSERT INTO foo_diff_data (employeeID,employeeName,employeeMail) VALUES(1,'Alice','alice@pgedge.com'),(2,'Carol','carol@pgedge.com')",host,dbname,port,pw,usr)

    #CREATE table - row diff
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_diff_row (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo_diff_row (employeeID,employeeName,employeeMail) VALUES(1,'Bob','bob@pgedge.com'),(2,'Carol','carol@pgedge.com')",host,dbname,port,pw,usr)
    if n==2:
        row = util_test.write_psql("INSERT INTO foo_diff_row (employeeID,employeeName,employeeMail) VALUES(3,'Alice','alice@pgedge.com')",host,dbname,port,pw,usr)


    #CREATE table - no primarykey
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_nopk (employeeID INT ,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo_nopk (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)

    print(f"Created tables on n{n}")


    cmd_node = f"spock repset-add-table default 'public.foo' {db}"
    res=util_test.run_home_cmd("add tables to repset", cmd_node, f"{cluster_dir}/n{n}/pgedge")
    print(f"Added tables to repset on n{n}")

    port = port + 1

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)