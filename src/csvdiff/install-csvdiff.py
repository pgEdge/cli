
import util
import os

thisDir = os.path.dirname(os.path.realpath(__file__))
ub = "/usr/bin/csvdiff"

util.message("\n## creating " + ub + " link #################")

os.system("sudo rm -f " + ub)
os.system("sudo ln -s " + thisDir + "/csvdiff " + ub)
os.system("sudo chmod 755 " + ub)

