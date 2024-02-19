
import os, sys


os.environ["MY_HOME"] = os.getcwd()
os.environ["MY_LOGS"] = f"{os.getenv('MY_HOME')}/tmp/cli_log.out"
os.environ["MY_LITE"] = f"/Users/denisl/dev/cli/out/posix/conf/db_local.db"

import util, multicloud, cluster, spock

#multicloud.list_nodes("akm")
#multicloud.list_zones("akm")
multicloud.list_airport_regions(airport="iad")

