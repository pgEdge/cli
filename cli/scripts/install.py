#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import sys, os

VER="23.03-3"
REPO=os.getenv("REPO", "https://pgedge-download.s3.amazonaws.com/REPO")
  
if sys.version_info < (3, 6):
  print("ERROR: Requires Python 3.6 or greater")
  sys.exit(1)

from urllib import request as urllib2

import tarfile

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
f = REPO + "/" + my_file

if not os.path.exists(my_file):
  print("Downloading CLI " + VER + " ...")
  try:
    fu = urllib2.urlopen(f)
    local_file = open(my_file, "wb")
    local_file.write(fu.read())
    local_file.close()
  except Exception as e:
    print("ERROR: Unable to download " + f + "\n" + str(e))
    sys.exit(1)

print("Unpacking ...")
try:
  tar = tarfile.open(my_file)
  tar.extractall(path=".")
  tar.close()
  os.remove(my_file)
except Exception as e:
  print("ERROR: Unable to unpack \n" + str(e))
  sys.exit(1)

cmd = "pgedge" + os.sep + "nodectl"
os.system(cmd + " set GLOBAL REPO " + REPO)

print("pgedge/nodectl installed.\n")

sys.exit(0)

