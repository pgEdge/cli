from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2022-2023 PGEDGE             ##########
####################################################################

import os, sys
import util, startup

pgver = "pgXX"

autostart = util.get_column('autostart', pgver)
if autostart == "on":
  startup.remove_linux("pg" + pgver[2:4], pgver)
