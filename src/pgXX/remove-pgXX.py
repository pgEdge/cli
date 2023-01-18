from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE             ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column('autostart', pgver)
if autostart != "on":
  sys.exit(0)

startup.remove_linux("pgedge" + pgver[2:4], pgver)
