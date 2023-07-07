#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import sys, os

VER="23.122"
REPO=os.getenv("REPO", "https://pgedge-download.s3.amazonaws.com/REPO")

if sys.version_info < (3, 6):
  print("ERROR: Requires Python 3.6 or greater")
  sys.exit(1)

if sys.version_info < (3, 9):
  print("WARNING: Advanced functionality requires Python 3.9+")

from urllib import request as urllib2

import tarfile, platform


def download_n_unpack(p_file, p_url, p_download_msg, p_del_download):
  if os.path.exists(p_file):
    os.system("rm -f " + p_file)

  print("Downloading " + str(p_download_msg))
  f = str(p_url) + "/" + p_file
  try:
    fu = urllib2.urlopen(f)
    local_file = open(p_file, "wb")
    local_file.write(fu.read())
    local_file.close()
  except Exception as e:
    print("ERROR: Unable to download " + f + "\n" + str(e))
    sys.exit(1)

  print("Unpacking ...")
  try:
    tar = tarfile.open(p_file)
    tar.extractall(path=".")
    tar.close()
    if p_del_download == True:
      os.remove(p_file)
  except Exception as e:
    print("ERROR: Unable to unpack \n" + str(e))
    sys.exit(1)


#######################
# MAINLINE
#######################

IS_64BITS = sys.maxsize > 2**32
if not IS_64BITS:
  print("ERROR: This is a 32-bit machine and our packages are 64-bit.")
  sys.exit(1)

if os.path.exists("pgedge"):
  dir = os.listdir("pgedge")
  if len(dir) != 0:
    print("ERROR: Cannot install over a non-empty 'pgedge' directory.")
    sys.exit(1)

my_file="pgedge-nodectl-" + VER + ".tar.bz2"

download_n_unpack(my_file, REPO, "CLI " + VER + " ...", True)
cmd = "pgedge" + os.sep + "nodectl "
os.system(cmd + "set GLOBAL REPO " + REPO)
os.system(cmd + "update --silent")
os.system(cmd + "info")

## figure out what python-libs file we need ##############
if platform.system() == "Linux":
  if platform.machine() == "aarch64":
    machine = "arm"
  else:
    machine = "amd"

  if os.path.isfile("/etc/redhat-release"):
    plat = "el9"
  else:
    plat = "ubu22"

  lib_file = f"linux-{plat}-{machine}"

elif platform.system() == "Darwin":
  lib_file = "osx-amd"

else:
  print("ERROR: platform.system() {platform.system()} not supported.")
  sys.exit(1)

lib_download = f"lib-{lib_file}.tar.bz2"
print(f"\nDownloading supporting libs '{lib_download}' ...")
##download_n_unpack(my_file, REPO, "CLI " + VER + " ...", False)

print("\npgedge/nodectl installed.\n")

sys.exit(0)

