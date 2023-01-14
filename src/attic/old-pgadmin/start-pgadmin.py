from __future__ import print_function, division

####################################################################
######          Copyright (c)  2015-2020 BigSQL           ##########
####################################################################

import os, sys, subprocess, json
import util, startup, time

MY_HOME = os.getenv('MY_HOME', '')
homedir = os.path.join(MY_HOME, "pgadmin")
pgadmin_datadir = os.path.join(MY_HOME, "data", "pgadmin")

docker_start_cmd = os.path.join(MY_HOME, "docker", "start-docker")
os.system(docker_start_cmd)

if not os.path.isdir(pgadmin_datadir):
  rc=os.system(sys.executable + ' -u ' + homedir + os.sep + 'init-pgadmin.py')

cmd="sudo docker start pgadmin"
print(cmd)
os.system(cmd)
