import sys, os, util_test, subprocess, shutil

nc=os.getenv("NC_DIR")

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
nc=os.getenv("NC_DIR")
home=os.getenv("HOME")


# Remove the nc directory (and its contents)
#
cwd=os.getcwd()
nc_path=(f"{cwd}/{nc}")
print(f"The complete path to the directory we want to delete is: {nc_path}")
res=util_test.remove_directory(f"{nc_path}")



# Remove the ~/.pgpass file
#
pgpass_path=(f"{home}/.pgpass")
res=util_test.remove_file(f"{pgpass_path}")



