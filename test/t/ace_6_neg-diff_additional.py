import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")


#Negative, call with non-existant node name
cmd_node = f"ace spock-diff demo n1"
res=util_test.run_cmd("Invalid Node Name", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "spock-diff needs at least two nodes to compare" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Similar Node Names", 1) 
print("*" * 100)

## use a schema-unqualified schema name
cmd_node = f"ace schema-diff demo all puble"
res=util_test.run_cmd("unqualified-schema", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Schema puble does not exist" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Schema Name", 1) 
print("*" * 100)

#call with the same node name in the command twice.
cmd_node = f"ace schema-diff demo n1 public"
res=util_test.run_cmd("schema-diff", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "schema-diff needs at least two nodes to compare" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Similar Node Names", 1) 

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
