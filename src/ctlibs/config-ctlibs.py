 
#         Copyright (c)  2022-2024 PGEDGE          #

import os, sys
import util

thisDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(thisDir)

platf = util.get_ctlib_dir()
if platf == "unsupported":
    util.message("ctlibs not available for platform")
    sys.exit(0)

url  = util.get_value("GLOBAL", "REPO")
file = f"ctlibs-{platf}.tgz"
cache_dir = f"{os.getenv('MY_HOME')}/data/conf/cache"

if os.path.exists(f"{cache_dir}/{file}"):
    util.message("File already downloaded")
    os.system(f"cp {cache_dir}/{file} .")
else:
    util.download_file(url, file)

if util.unpack_file(file):
    dir = "../hub/scripts/lib/"
    util.message(f"moving {platf} to {dir}")
    os.system(f"rm -rf {dir}{platf}")
    os.system(f"mv {platf} {dir}")
    os.system(f"rm {file}")
    sys.exit(0)

sys.exit(1)

