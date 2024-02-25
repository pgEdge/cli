
import os, sys


os.environ["MY_HOME"] = os.getcwd()
os.environ["MY_LOGS"] = f"/tmp/cli_log.out"
os.environ["MY_LITE"] = f"{os.getenv('PGE')}/out/posix/conf/db_local.db"

import util, multicloud

#multicloud.list_nodes("akm")
#multicloud.list_zones("akm")
#multicloud.list_airport_regions(airport="iad")
#multicloud.list_sizes(provider="akm")
#multicloud.create_node(provider="akm", region="us-east", name="ewr-akm-n222", ssh_key="eqn-test-key")
multicloud.list_keys("eqn", project="2b293326-e54c-45a9-a248-c2e018a4429e")
