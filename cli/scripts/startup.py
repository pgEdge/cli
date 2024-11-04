
#  Copyright 2022-2024 PGEDGE  All rights reserved. #


import os, tempfile
import util

PROC_MGR = util.get_value("GLOBAL", "PROC_MGR", "systemd")
if PROC_MGR == "supervisord":
    PROC_CTL = "supervisorctl"
else:
    PROC_CTL = "systemctl"


def user_exists(p_user):
    user_data = util.getoutput("cat /etc/passwd | grep -E '^%s:' ; true" % p_user)

    if user_data:
        u = user_data.split(":")
        return dict(name=u[0], uid=u[2], gid=u[3], home=u[5], shell=u[6])
    else:
        return None

    return 0


## Create a system user for running specific system services
def useradd_linux(p_user):
    util.message("Creating the user " + p_user)
    if not util.get_platform() == "Linux":
        util.message("USERADD is a Linux only command", "error")
        return 1

    if not util.is_admin():
        util.message("Must be ROOT to run USERADD", "error")
        return 1

    ## make sure the user exists....
    util.run_sudo("useradd -m " + p_user)

    return 0


def config_proc_mgr(
    p_comp, p_svc, p_user, p_start, p_stop="", p_reload="", is_pg=True):

    if PROC_MGR == "supervisord":
        config_supervisord(p_comp, p_user, p_start)
    else:
        config_systemd(p_comp, p_svc, p_user, p_start, p_stop, p_reload, is_pg)

    return


def config_supervisord(
    p_comp,
    p_svc_user,
    p_start
):

    supv_dir = f"{util.MY_DATA}/supevisord"
    os.system = f"mkdir -p {supv_dir}"

    f = f"{p_comp}.conf"
    sys_svc_file = os.path.join(supv_dir, f)
    unit_file = tempfile.mktemp(f)
    fh = open(unit_file, "w")

    fh.write(f"[program:{p_comp}]\n")
    fh.write(f"command={p_start}")
    fh.write("autostart=true\nautorestart=true\nstopsignal=INT\n")

    fh.close()
    os.system(f"sudo mv {unit_file} {sys_svc_file}")

    if os.getenv("pgeDebug") == "1":
        util.message("##### sys_svc_file = {sys_svc_file} #####", "debug")
        os.system(f"cat {sys_svc_file}")
        util.message("##############################", "debug")

    return(0)


def config_systemd(p_comp, p_systemsvc, p_svc_user, p_start, p_stop="", p_reload="", is_pg=True):

    ##pg_bin_dir = os.path.join(util.MY_HOME, p_comp, "bin")
    ##util.create_symlinks("/usr/bin", pg_bin_dir)

    f = f"{p_systemsvc}.service"
    sys_svc_file = os.path.join(util.get_systemd_dir(), f)
    unit_file = tempfile.mktemp(f)
    fh = open(unit_file, "w")

    fh.write("[Unit]\n")
    fh.write(f"Description=pgEdge {p_comp}\n")
    if is_pg:
        fh.write("After=syslog.target\n")
    fh.write("After=network.target\n")
    fh.write("\n")
    fh.write("[Service]\n")
    if is_pg:
        fh.write("Type=forking\n")
    fh.write(f"User={p_svc_user}\n")
    if is_pg:
        fh.write("\n")
        fh.write("OOMScoreAdjust=-1000\n")
    fh.write(f"ExecStart={p_start}\n")
    if p_stop != "":
        fh.write(f"ExecStop={p_stop}\n")
    if p_reload != "":
        fh.write(f"ExecReload={p_reload}\n")
    if is_pg:
        fh.write("TimeoutSec=300\n")
    fh.write("\n")
    fh.write("[Install]\n")
    fh.write("WantedBy=multi-user.target\n")

    fh.close()
    os.system(f"sudo mv {unit_file} {sys_svc_file}")

    if os.getenv("pgeDebug") == "1":
        util.message("##### sys_svc_file = {sys_svc_file} #####", "debug")
        os.system(f"cat {sys_svc_file}")
        util.message("##############################", "debug")

    return util.echo_cmd(f"sudo systemctl enable {p_systemsvc}")


def start_proc(p_systemsvc):
    return util.echo_cmd(f"sudo {PROC_CTL} start {p_systemsvc}")


def stop_proc(p_systemsvc):
    return util.echo_cmd(f"sudo {PROC_CTL} stop {p_systemsvc}")


def reload_proc(p_systemsvc):
    return util.echo_cmd(f"sudo {PROC_CTL} reload {p_systemsvc}")


def remove_proc(p_systemsvc):
    if PROC_MGR == "systemd":
        util.echo_cmd(f"sudo {PROC_CTL}  disable {p_systemsvc}")
        util.echo_cmd(
            "sudo rm -f " + os.path.join(util.get_systemd_dir(), p_systemsvc + ".service"))
    else:
        util.message("TODO")

    return 0


def config_pg_proc(pgver):
    systemsvc = "pg" + pgver[2:4]
    svcuser = util.get_user()
    cmd_log=None
    cmd_stop=None
    cmd_reload=None
    cmd_status=None

    pgdata = util.get_column("datadir", pgver)
    pg_ctl = os.path.join(MY_HOME, pgver, "bin", "pg_ctl")
    cmd_start = pg_ctl + " start  -D " + pgdata + " -w -t 300"

    if PROC_MGR == "systemd":
        cmd_stop = pg_ctl + " stop   -D " + pgdata + " -m fast"
        cmd_reload = pg_ctl + " reload -D " + pgdata
        cmd_status = pg_ctl + " status -D " + pgdata
        cmd_log = "-l " + pgdata + "/pgstartup.log"

    startup.config_proc_mgr(
        pgver, systemsvc, svcuser, cmd_start, cmd_log, cmd_stop, cmd_reload, cmd_status)

    util.set_column("svcname", pgver, systemsvc)


##############################################################################
## below _linux() systemd wrapper functions are left for compat with older 
##   versions of pgXX
##############################################################################

def config_linux(p_comp, p_systemsvc, p_svc_user, p_start, p_start_log,
        p_stop, p_reload, is_pg=True, p_env=None):

    config_systemd(p_comp, p_systemsvc, p_svc_user, p_start,
        p_stop, p_reload, is_pg=True)

    return

def start_linux(svc):
    return(start_proc(svc))

def stop_linux(svc):
    return(stop_proc(svc))

def reload_linux(svc):
    return(reload_proc(svc))

def remove_linux(svc, pg_ver):
    return(remove_proc(svc))
