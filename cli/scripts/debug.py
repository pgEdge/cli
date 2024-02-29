
import os, sys


os.environ["MY_HOME"] = os.getcwd()
os.environ["MY_LOGS"] = f"/tmp/cli_log.out"
os.environ["MY_LITE"] = f"{os.getenv('PGE')}/out/posix/conf/db_local.db"

import util, vm

#nds = vm.list_nodes("eqn", pretty=False)
#print(nds)
#apts = vm.list_airports(airport="iad", pretty=False)
#print(apts)
szs = vm.list_sizes(provider="akm", pretty=False)
print(szs)
#vm.create(provider="akm", airport="iad",  node_name="ewr-akm-n222")
#vm.list_keys("aws")
