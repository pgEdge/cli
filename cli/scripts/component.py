#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################
 
import os, sys, util, api, meta

def init_comp(p_comp, p_pidfile=''):
  print(" ")
  print("## initializing " + p_comp +  " ##################")

  MY_HOME = os.getenv('MY_HOME', '')

  datadir = os.path.join(MY_HOME, 'data', p_comp)
  if os.path.isdir(datadir):
    print("## " + p_comp + " already configured.")
    return(1)
  else:
    os.mkdir(datadir)
  util.set_column("datadir", p_comp, datadir)

  if p_pidfile != '':
    pidfilepath = os.path.join(datadir, p_pidfile)
    util.set_column("pidfile", p_comp, pidfilepath)

  logdir = os.path.join(MY_HOME, 'data', 'logs', p_comp)
  if not os.path.isdir(logdir):
    os.mkdir(logdir)
  util.set_column("logdir", p_comp, logdir)

  return(0)


def start_comp(p_comp, p_homedir, p_start_cmd):
  port = util.get_comp_port(p_comp)
  print(p_comp + " starting on port " + port)

  autostart = util.get_column("autostart", p_comp)
  if autostart == "on":
    os.system("sudo systemctl start " + p_comp)
    return(0)

  os.chdir(p_homedir)

  datadir = util.get_column("datadir", p_comp)
  if datadir == "" or not (os.path.isdir(datadir)):
    os.system(sys.executable + " -u init-" + p_comp + ".py")

  os.system(p_start_cmd)
  return(0)


def stop_comp(p_comp):

  autostart = util.get_column("autostart", p_comp)
  if autostart == "on":
    os.system("sudo systemctl stop " + p_comp)
    return(0)

  pidfile = util.get_column("pidfile", p_comp)
  if os.path.isfile(pidfile):
    print(p_comp + " stopping")
    try:
      with open(pidfile, 'r') as f:
        pid = f.readline().rstrip(os.linesep)
      util.kill_pid(int(pid))
      os.remove(pidfile)
    except Exception as e:
      print(str(e))
  else:
    print(p_comp + " stopped")

  return 0


def check_pid_status(p_comp, p_pidfile, p_kount=0, p_json=False):
  port = util.get_comp_port(p_comp)
  if os.path.isfile(p_pidfile):
    ver = meta.get_ver_plat(p_comp)
    rc = os.system("pgrep --pidfile " + p_pidfile + " > /dev/null 2>&1")
    if rc == 0:
      api.status(p_json, p_comp, ver, "Running", port, p_kount)
    else:
      api.status(p_json, p_comp, ver, "Stopped", port, p_kount)

  else:
    api.status(p_json, p_comp, "", "Stopped", port, p_kount)

