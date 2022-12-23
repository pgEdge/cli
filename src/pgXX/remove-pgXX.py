from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2020-2022 OSCG             ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column('autostart', pgver)
if autostart != "on":
  sys.exit(0)

startup.remove_linux("postgresql" + pgver[2:4], pgver)
