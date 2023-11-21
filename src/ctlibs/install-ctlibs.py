 
#          Copyright (c)  2022-2024 PGEDGE        #

import sys, os

thisDir = os.path.dirname(os.path.realpath(__file__))
script = thisDir + os.sep + "config-ctlibs.py"
cmd = sys.executable + " -u " + script
rc = os.system(cmd)

