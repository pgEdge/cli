#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import sys, os

VER="24.008"
REPO=os.getenv("REPO", "https://pgedge-upstream.s3.amazonaws.com/REPO")

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


#############################################
# MAINLINE
#############################################

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
os.system(cmd + "install nclibs")

print("\npgedge/nodectl installed.\n")

sys.exit(0)

