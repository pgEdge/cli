
import util
import os

thisDir = os.path.dirname(os.path.realpath(__file__))
if util.get_os() == "Linux":
  ub = "/usr/bin"
else:
  ub = "/usr/local/bin"

cmd = "sudo cp -f " + thisDir + "/csvdiff " + ub + "/."
util.message("\n# " + cmd)
os.system(cmd)
os.system("sudo chmod 755 " + ub + "/csvdiff")

