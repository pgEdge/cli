#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, tempfile
import util


def user_exists(p_user):
  user_data = util.getoutput ("cat /etc/passwd | grep -E '^%s:' ; true" % p_user)

  if user_data:
    u = user_data.split(":")
    return dict(name=u[0],uid=u[2],gid=u[3],home=u[5],shell=u[6])
  else:
    return None

  return(0)


## Create a system user for running specific system services
def useradd_linux(p_user):
  util.message("Creating the user "+ p_user)
  if not util.get_platform() == "Linux":
    util.message("USERADD is a Linux only command", "error")
    return(1)

  if not util.is_admin():
    util.message("Must be ROOT to run USERADD", "error")
    return(1)

  ## make sure the user exists....
  util.run_sudo("useradd -m " + p_user)

  return(0)



def config_linux(p_comp, p_systemsvc, p_svc_user, p_start, p_start_log,
                   p_stop, p_reload, p_status="", is_pg=True, p_env=None):

  my_home = os.getenv("MY_HOME")

  pg_bin_dir = os.path.join(my_home, p_comp, 'bin')
  util.create_symlinks("/usr/bin", pg_bin_dir)

  sys_svc_file = os.path.join(util.get_systemd_dir(), p_systemsvc + ".service")

  util.message(p_comp + " config autostart " + sys_svc_file)

  ## systemD ################################
  unit_file = tempfile.mktemp(".service")
  fh = open(unit_file, "w")
  fh.write("[Unit]\n")
  fh.write("Description=PostgreSQL (" + p_comp + ")\n")
  if is_pg:
    fh.write("After=syslog.target\n")
  fh.write("After=network.target\n")
  fh.write("\n")
  fh.write("[Service]\n")
  if p_env:
    fh.write("Environment=" + p_env + "\n")
  if is_pg:
    fh.write("Type=forking\n")
  fh.write("User=" + p_svc_user + "\n")
  if is_pg:
    fh.write("\n")
    fh.write("OOMScoreAdjust=-1000\n")
  fh.write("ExecStart="  + p_start  + "\n")
  if p_stop!="":
    fh.write("ExecStop="   + p_stop   + "\n")
  fh.write("ExecReload=" + p_reload + "\n")
  if is_pg:
    fh.write("TimeoutSec=300\n")
  fh.write("\n")
  fh.write("[Install]\n")
  fh.write("WantedBy=multi-user.target\n")
  fh.close()

  util.run_sudo("mv " + unit_file + " " + sys_svc_file)
  return(util.echo_cmd("sudo systemctl enable " + p_systemsvc))


def start_linux(p_systemsvc):
  return (util.echo_cmd("sudo systemctl start " + p_systemsvc))


def stop_linux(p_systemsvc):
  return (util.echo_cmd("sudo systemctl stop  " + p_systemsvc))


def reload_linux(p_systemsvc):
  return (util.echo_cmd("sudo systemctl reload " + p_systemsvc))


def remove_linux(p_systemsvc, p_pgver):
  my_home = os.getenv("MY_HOME")
  pg_bin_dir = os.path.join(my_home, p_pgver, 'bin')
  #util.remove_symlinks("/usr/bin", pg_bin_dir)

  util.echo_cmd("sudo systemctl disable " + p_systemsvc)
  util.echo_cmd("sudo rm -f " + os.path.join(util.get_systemd_dir(), p_systemsvc + ".service"))
  return(0)

