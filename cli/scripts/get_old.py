
import os
from pathlib import Path
os.chdir(Path(__file__).parent)

import sys, sqlite3, platform

PROD_BUCKET="s3://pgedge-download/REPO"

conf_dir="../../data/conf"
meta_data_db=f"{conf_dir}/db_local.db"
cache_dir=f"{conf_dir}/cache"


try:
    con = sqlite3.connect("../../data/conf/db_local.db", check_same_thread=False)
except Exception as e:
    print(f"ERROR connecting to meta data: {e}")
    sys.exit(1)

arch="amd"
if platform.machine() == "aarch64":
    arch = "arm"


data = []
sql = '''
SELECT component, version, platform
  FROM v_versions 
 WHERE stage = 'prod' 
   AND is_current = 0;
'''

try:
    c = con.cursor()
    c.execute(sql)
    data = c.fetchall()
except Exception as e:
    print(f"ERROR retrieving old meta data: {e}")
    sys.exit(1)

err_knt = 0

for d in data:
    component = str(d[0])
    version = str(d[1])
    platform = str(d[2])

    file = f"{component}-{version}-{arch}.tgz"

    cmd= f"aws s3 cp {PROD_BUCKET}/{file}  {cache_dir}/."
    print(f"# {cmd}") 
    rc = os.system(cmd)
    if rc == 0:
        os.system(f"aws s3 cp {PROD_BUCKET}/{file}.sha512 {cache_dir}/.")
    else:
        err_knt = err_knt + 1
        print(f"#################### ERROR ({err_knt}) #########################")

    print("")

sys.exit(err_knt)


