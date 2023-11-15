import sys
import os
import util_test
import subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()

repo = os.getenv("EDGE_REPO")
num_nodes = int(os.getenv("EDGE_NODES", 2))
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
port = int(os.getenv("EDGE_START_PORT", 6432))
usr = os.getenv("EDGE_USERNAME", "admin")
pw = os.getenv("EDGE_PASSWORD", "password1")
db = os.getenv("EDGE_DB", "demo")
host = os.getenv("EDGE_HOST", "localhost")
repuser = os.getenv("EDGE_REPUSER", "pgedge")
repset = os.getenv("EDGE_REPSET", "demo-repset")

for i in range(1, num_nodes + 1):
    # Drop Node
    print("Repset-Drop")
    cmd_spock = f"~/work/nodectl/test/pgedge/cluster/demo/n{i}/pgedge/nodectl spock repset-drop {repset} {db}"

    # Execute the command and capture the output
    result = subprocess.run(cmd_spock, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print the output
    print("Output of cmd_spock:")
    print("Result of stdout=", result.stdout)
    

# Check if there were any errors
    if result.returncode != 0:
        print("Error occurred:")
        print(result.stderr)
        sys.exit(1)

    # Needle and Haystack check
    haystack = result.stdout
    needle = os.getenv("EDGE_REP_DROP")

    # Check if the needle is present in the haystack
    result = util_test.contains(haystack, needle)
    print("Result:", result)

    print(i)
    port += 1
    i += 1
    print(i)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


