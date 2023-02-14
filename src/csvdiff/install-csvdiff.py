
import util
import os

thisDir = os.path.dirname(os.path.realpath(__file__))
ub = "/usr/bin/csvdiff"

util.message("\n## creating " + ub + " link #################")

os.system("sudo rm -f " + ub)
cmd = "sudo ln -s " + thisDir + "/csvdiff " + ub
print(f"DEBUG: {cmd}")
os.system(cmd)
os.system("sudo chmod 755 " + ub)

