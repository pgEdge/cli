import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Table diff

#compare the matching tables in a cluster and shows any differences
cmd_node = f"ace table-diff {cluster} public.foo"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1) 

#compare tables with mis matched data in a cluster and shows any differences
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Data", 1)

#compare tables with mis matched rows in a cluster and shows any differences
cmd_node = f"ace table-diff {cluster} public.foo_diff_row"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Rows", 1)

#compare tables with no pk in a cluster and shows any differences
cmd_node = f"ace table-diff {cluster} public.foo_nopk"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "No primary key found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - No pk", 1)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 
