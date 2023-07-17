 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           #########
####################################################################

import sys, os

thisDir = os.path.dirname(os.path.realpath(__file__))
script = thisDir + os.sep + "config-nclibs.py"
cmd = sys.executable + " -u " + script
rc = os.system(cmd)

