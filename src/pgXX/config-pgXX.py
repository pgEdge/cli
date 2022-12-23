from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2020-2022 OSCG             ##########
####################################################################

import argparse, sys, os, tempfile, json, subprocess, getpass
import util, startup

pgver = "pgXX"

MY_HOME = os.getenv('MY_HOME', '')
MY_LOGS = os.getenv('MY_LOGS', '')

pg_home = os.path.join(MY_HOME, pgver)
homedir = os.path.join(MY_HOME, pgver)
logdir = os.path.join(homedir, pgver)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=0)
parser.add_argument("--autostart", choices=["on", "off"])
parser.add_argument("--datadir", type=str, default="")
parser.add_argument("--logdir", type=str, default="")
parser.add_argument("--svcname", type=str, default="")

parser.add_argument("--setpwd", type=str, default="")
parser.add_argument("--getpwd", type=str, default="")

parser.usage = parser.format_usage().replace("--autostart {on,off}","--autostart={on,off}")
args = parser.parse_args()

autostart = util.get_column('autostart', pgver)
app_datadir = util.get_comp_datadir(pgver)
port = util.get_comp_port(pgver)

## SECURE SECRETS MANAGMENT ###################################
if args.setpwd > "":
  pwdargs = args.setpwd.split()
  if len(pwdargs) != 2:
     util.message("invalid --setpwd args", "error")
     sys.exit(1)

  user = pwdargs[0]
  pwd = pwdargs[1]

  util.change_pgpassword(pwd, p_user=user, p_port=port, p_ver=pgver)
  
  sys.exit(0)


if args.getpwd > "":
  pwdargs = args.getpwd.split()
  if len(pwdargs) != 1:
     util.message("invalid --getpwd args", "error")
     sys.exit(1)

  user = pwdargs[0]

  pwd = util.retrieve_pgpassword(p_user=user, p_port=port)
  if pwd == None:
    util.message("not found", "error")
  else:
    util.message(pwd, "pwd")

  sys.exit(0)


## IS_RUNNING ###############################################
is_running = False
if app_datadir != "" and util.is_socket_busy(int(port), pgver):
  is_running = True
  msg = "You cannot change the configuration when the server is running."
  util.message(msg, "error")

  sys.exit(0)


## DATADIR, PORT , LOGDIR & SVCNAME ###########################
if args.datadir > '':
  util.set_column("datadir", pgver, args.datadir)

## PORT ################################################
if args.port > 0:
  util.update_postgresql_conf(pgver, args.port, False)

if args.logdir > '':
  util.set_column("logdir", pgver, args.logdir)
else:
  ## DATA ###############################################
  data_root = os.path.join(MY_HOME, "data")
  if not os.path.isdir(data_root):
    os.mkdir(data_root)

  ## LOGS ###############################################
  data_root_logs = os.path.join(data_root, "logs")
  if not os.path.isdir(data_root_logs):
    os.mkdir(data_root_logs)
  pg_log = os.path.join(data_root_logs, pgver)
  if not os.path.isdir(pg_log):
    os.mkdir(pg_log)
  util.set_column("logdir", pgver, pg_log)

if args.svcname > '':
  util.set_column("svcname", pgver, args.svcname)


## AUTOSTART ###########################################
if ((args.autostart is None) or (autostart == args.autostart)):
  sys.exit(0)

systemsvc = 'postgresql' + pgver[2:4]
if args.autostart == "off":
  startup.remove_linux(systemsvc, pgver)
else:
  pg_ctl = os.path.join(MY_HOME, pgver, 'bin', 'pg_ctl') 
  pgdata = util.get_column('datadir', pgver)
  cmd_start  = pg_ctl + ' start  -D ' + pgdata + ' -s -w -t 300'
  cmd_stop   = pg_ctl + ' stop   -D ' + pgdata + ' -s -m fast'
  cmd_reload = pg_ctl + ' reload -D ' + pgdata + ' -s'
  cmd_status = pg_ctl + ' status -D ' + pgdata
  cmd_log = '-l ' + pgdata + '/pgstartup.log'
  svcuser = util.get_column('svcuser', pgver)
  startup.config_linux(pgver, systemsvc, svcuser, cmd_start, cmd_log, 
    cmd_stop, cmd_reload, cmd_status)
  util.set_column('svcname', pgver, systemsvc)

util.set_column('autostart', pgver, args.autostart)
sys.exit(0)
