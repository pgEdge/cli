from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE           ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column('autostart', pgver)
if autostart == "on":
  startup.remove_linux("pg" + pgver[2:4], pgver)

isRM_DATA = os.getenv('isRM_DATA', 'False')
if isRM_DATA == "True":
  util.message("Removing 'data/*' directories at your request")
  os.system("sudo rm -r data/*")

