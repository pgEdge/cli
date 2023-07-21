 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           #########
####################################################################

import platform, os, sys, subprocess, shutil
import util

thisDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(thisDir)

arch = platform.machine()

platf = "unsupported"
if platform.system() == "Linux":
  if os.path.exists("/etc/redhat-release"):
    if arch == "aarch64":
      platf = "el9-arm"
    else:
      platf = "el9-amd"
  else:
    f = "/etc/os-release"
    if os.path.exists(f):
      with open(f,'r') as text_file:
        text_data = text_file.read()
        if text_data.find("22.04"):
          if arch == "aarch64":
            platf = "ubu22-arm"
          else:
            platf = "ubu22-amd"
elif platform.system() == "Darwin":
  platf = "osx"

if platf == "unsupported":
  util.message("nclibs not available for platform")
  sys.exit(0)

url  = util.get_value("GLOBAL", "REPO")
file = f"nclibs-{platf}.tar.bz2"

if util.download_file(url, file):
  if util.unpack_file(file):
    dir = "../hub/scripts/lib/"
    util.message(f"moving {platf} to {dir}")
    os.system(f"rm -rf {dir}{platf}")
    os.system(f"mv {platf} {dir}")
    os.system(f"rm {file}")
    sys.exit(0)

sys.exit(1)

