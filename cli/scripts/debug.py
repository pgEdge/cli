
import os, sys


os.environ["MY_HOME"] = os.getcwd()
os.environ["MY_LOGS"] = f"/tmp/cli_log.out"
os.environ["MY_LITE"] = f"{os.getenv('PGE')}/out/posix/conf/db_local.db"

import util, vm

#vm.list_nodes("eqn")
#vm.list_zones("akm")
vm.list_airports(airport="iad")
#vm.list_sizes(provider="akm")
#vm.create(provider="akm", airport="iad",  node_name="ewr-akm-n222")
#vm.list_keys("aws")
