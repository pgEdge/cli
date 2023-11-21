 
#         Copyright (c)  2022-2024 PGEDGE          #

import platform, os, sys, subprocess, shutil
import util

thisDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(thisDir)

arch = platform.machine()
if arch == "aarch64":
  plat_os = "arm"
else:
  plat_os = "amd"

platf = "unsupported"
if platform.system() == "Linux":
  if os.path.exists("/etc/redhat-release"):
    if util.get_el_os() == "EL9":
      platf = f"el9-{plat_os}"
    else:
      platf = f"el8-amd"
  elif os.path.exists("/etc/amazon-linux-release"):
    f = "/etc/amazon-linux-release"
    rc = os.system(f"grep 2023 {f}")
    if rc == 0:
      platf = f"el9-{plat_os}"
    else:
      platf = f"el8-amd"
  else:
    f = "/etc/os-release"
    if os.path.exists(f):
      rc = os.system(f"grep '22.04' {f}")
      if rc == 0:
        platf = f"ubu22-{plat_os}"
elif platform.system() == "Darwin":
  platf = "osx"

if platf == "unsupported":
  util.message("nclibs not available for platform")
  sys.exit(0)

url  = util.get_value("GLOBAL", "REPO")
file = f"ctlibs-{platf}.tar.bz2"

if util.download_file(url, file):
  if util.unpack_file(file):
    dir = "../hub/scripts/lib/"
    util.message(f"moving {platf} to {dir}")
    os.system(f"rm -rf {dir}{platf}")
    os.system(f"mv {platf} {dir}")
    os.system(f"rm {file}")
    sys.exit(0)

sys.exit(1)

