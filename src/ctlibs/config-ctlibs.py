 
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
    rc = os.system(f"grep 2023 {f} > /dev/null 2>&1")
    if rc == 0:
      platf = f"el9-{plat_os}"
    else:
      platf = f"el8-amd"
  else:
    f = "/etc/os-release"
    if os.path.exists(f):
      rc22 = os.system(f"grep '22.04' {f} > /dev/null 2>&1")
      rc24 = os.system(f"grep '24.04' {f} > /dev/null 2>&1")
      deb12 = os.system(f"grep 'bookworm' {f} > /dev/null 2>&1")
      rc_l15 = os.system(f"grep 'leap:15' {f} > /dev/null 2>&1")
      rc_s15 = os.system(f"grep 'sles:15' {f} > /dev/null 2>&1")

      if rc22 == 0:
        platf = f"ubu22-{plat_os}"
      elif rc24 == 0:
        platf = f"ubu24-{plat_os}"
      elif deb12 == 0:
        platf = f"deb12-{plat_os}"
      elif ((rc_l15 == 0) or (rc_s15 == 0)):
        platf = f"el8-{plat_os}"

elif platform.system() == "Darwin":
  platf = "osx"

if platf == "unsupported":
  util.message("ctlibs not available for platform")
  sys.exit(0)

url  = util.get_value("GLOBAL", "REPO")
file = f"ctlibs-{platf}.tgz"

if util.download_file(url, file):
  if util.unpack_file(file):
    dir = "../hub/scripts/lib/"
    util.message(f"moving {platf} to {dir}")
    os.system(f"rm -rf {dir}{platf}")
    os.system(f"mv {platf} {dir}")
    os.system(f"rm {file}")
    sys.exit(0)

sys.exit(1)

