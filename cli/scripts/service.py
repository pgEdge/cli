import os, sys
import fire, util, component, meta
import time, datetime, platform, tarfile, sqlite3, time

## Initialize Globals ##############################################
REPO = util.get_value("GLOBAL", "REPO")

os.chdir(util.MY_HOME)

db_local = util.MY_LITE

connL = sqlite3.connect(db_local)

isJSON = util.isJSON

def exit_cleanly(p_rc):
    try:
        connL.close()
    except Exception:
        pass
    sys.exit(p_rc)


## Check component state #################################################
def check_status(p_comp, p_mode):
    if p_comp in ["all", "*"]:
        try:
            c = connL.cursor()
            sql = "SELECT component, port, autostart, pidfile FROM components"
            c.execute(sql)
            data = c.fetchall()
            kount = 0
            if isJSON:
                print("[")
            for row in data:
                comp = row[0]
                port = row[1]
                autostart = row[2]
                pidfile = row[3]
                if str(pidfile) != "None" and str(pidfile) > "":
                    kount = kount + 1
                    component.check_pid_status(comp, pidfile, kount, isJSON)
                    continue
                if (port > 1) or (p_mode == "list") or (autostart == "on"):
                    kount = kount + 1
                    util.check_comp(comp, str(port), kount)
            if isJSON:
                print("]")
        except Exception as e:
            util.fatal_sql_error(e, sql, "check_status()")
    else:
        pidfile = util.get_comp_pidfile(p_comp)
        if pidfile != "None" and pidfile > "":
            component.check_pid_status(p_comp, pidfile, 0, isJSON)
        else:
            port = util.get_comp_port(p_comp)
            util.check_comp(p_comp, port, 0)
    return



def run_cmd(p_cmd, p_comp):
    nc_cmd = "./ctl " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def start(component=None):
    """Start server components"""

    run_cmd("start", component)


def stop(component=None):
    """Stop server components"""

    run_cmd("stop", component)


def status(component=None):
    """Display running status of installed server components"""
    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, requested_p_version, extra_args = util.get_comp_lists("status", 0, init_comp_list, [], "", connL)
    for c in p_comp_list:
        check_status(c, "status")
    exit_cleanly(0)


def restart(component):
    """Stop & then start server components"""

    run_cmd("restart", component)


def reload(component):
    """Reload server configuration files (without a restart)"""

    run_cmd("reload", component)


def enable(component):
    """Enable a component"""

    run_cmd("enable", component)


def disable(component):
    """Disable a server component from starting automatically"""

    run_cmd("disable", component)


def config(component):
    """Config a component"""

    run_cmd("config", component)


def init(component):
    """Initialize a component"""

    run_cmd("init", component)


if __name__ == "__main__":
    fire.Fire(
        {
            "start": start,
            "stop": stop,
            "status": status,
            "restart": restart,
            "reload": reload,
            "enable": enable,
            "disable": disable,
            "config": config,
            "init": init,
        }
    )
