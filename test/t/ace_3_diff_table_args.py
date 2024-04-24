import os, util_test, subprocess, pathlib
# Get environment variables

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Test Additional Arguements for table diff

cmd_node = f"ace table-diff {cluster} public.foo --block_rows=1001"
res=util_test.run_cmd("block_rows > 1000", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)

cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=1"
res=util_test.run_cmd("max_cpu_ratio is 1", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1)

cmd_node = f"ace table-diff {cluster} public.foo --output=json"
res=util_test.run_cmd("output in json form", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output JSON", 1)
## TO DO - check for diff file
#if not os.path.exists(f"{home_dir}/diffs"):
##	util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Failed to make JSON", 1)
##os.system(f"rm -rf {home_dir}/diffs")

## TO DO - ydiff error
#cmd_node = f"ace table-diff {cluster} public.foo --output=csv"
#res=util_test.run_cmd("output in csv form", cmd_node, f"{home_dir}")
#print(res)
#if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
#    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output CSV", 1)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 
