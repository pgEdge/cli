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
util_test.remove_directory(f"{nc_path}")

# Confirm the nc directory is removed
dir_list=os.listdir(f"{cwd}")
print(f"The current working directory contains: {dir_list}")


# Remove the ~/.pgpass file
#
pgpass_path=(f"{home}/.pgpass")
util_test.remove_file(f"{pgpass_path}")

# Confirm the .pgpass file is removed
pgpass_list=os.listdir(f"{home}")
print(f"The home directory of the user invoking the tests contains: {pgpass_list}")


if "'nc'" in dir_list or '.pgpass' in pgpass_list:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS

