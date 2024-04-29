import os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")


## use a misspelled table name.
cmd_node = f"ace table-diff demo public.fo"
res=util_test.run_cmd("misspelled table name", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Invalid table name 'public.fo'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Invalid Table", 1) 
print("*" * 100) 
   
## use a non-existant cluster name.
cmd_node = f"ace table-diff dem public.foo"
res=util_test.run_cmd("non-existent cluster name", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - cluster not found", 1) 
print("*" * 100) 
     
## set --block_rows to a value less than 1000
cmd_node = f"ace table-diff demo public.foo --block_rows=999"
res=util_test.run_cmd("block_rows < 1000", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "block_rows param '999' must be integer >= 1000" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1) 
print("*" * 100)  
    
## set --max_cpu_ratio to 2
cmd_node = f"ace table-diff demo public.foo --max_cpu_ratio=2"
res=util_test.run_cmd("cpu ratio > 1", cmd_node, f"{home_dir}")
print(res)
'''
if res.returncode == 0 or "block_rows param '999' must be integer >= 1000" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)
'''
print("*" * 100)  

## set --max_cpu_ratio to ONE
cmd_node = f"ace table-diff demo public.foo --max_cpu_ratio=ONE"
res=util_test.run_cmd("invalid_cpu_ratio", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Invalid values for ACE_MAX_CPU_RATIO" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1) 
print("*" * 100)  
    
##  Negative, set --output to html; confirm that an error is thrown
cmd_node = f"ace table-diff demo public.foo --output=html"
res=util_test.run_cmd("output in html format", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "table-diff currently supports only csv and json output formats" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output HTML", 1) 
 
util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)    
