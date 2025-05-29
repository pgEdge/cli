
#  Copyright 2022-2025 PGEDGE  All rights reserved. #

import os, sys
import fire, util, meta, api
import time, datetime, platform, tarfile, sqlite3, time

## Initialize Globals ##############################################
REPO = util.get_value("GLOBAL", "REPO")

os.chdir(util.MY_HOME)

db_local = util.MY_LITE

connL = sqlite3.connect(db_local)

isJSON = util.isJSON

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
                    check_pid_status(comp, pidfile, kount, isJSON)
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
            check_pid_status(p_comp, pidfile, 0, isJSON)
        else:
            port = util.get_comp_port(p_comp)
            util.check_comp(p_comp, port, 0)
    return


def run_cmd(p_cmd, p_comp):
    nc_cmd = "./pgedge " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def start(component=None):
    """Start server components."""
    util.message(f"service.start({component})", "debug")

    util.check_server(component, "start")

    if component and util.get_comp_state(component) == "Disabled":
        util.exit_message(f"{component} is disabled and will not be started")

    for svr in util.get_enabled_servers():
        if (component is None) or (component == svr):
            util.run_script(svr, f"start-{svr}", "start")


def stop(component=None):
    """Stop server components."""
    util.message(f"service.stop({component})", "debug")

    util.check_server(component, "stop")

    for svr in util.get_enabled_servers():
        if (component is None) or (component == svr):
            util.run_script(svr, f"stop-{svr}", "stop")


def status(component=None):
    """Display running status of server components."""
    util.message(f"service.status({component})", "debug")

    util.check_server(component, "status")

    for svr in util.get_enabled_servers():
        if (component is None) or (component == svr):
            check_status(svr, "status")


def restart(component=None):
    """Stop & then start server components."""
    util.message(f"service.restart({component})", "debug")

    util.check_server(component, "restart")

    for svr in util.get_enabled_servers():
        if (component is None) or (component == svr):
            util.run_script(svr, f"stop-{svr}", "stop")
            util.run_script(svr, f"start-{svr}", "start")


def reload(component):
    """Reload server configuration files (without a restart)"""
    util.message(f"service.reload({component})", "debug")

    util.check_server(component, "reload")

    run_cmd("reload", component)


def enable(component=None):
    """Enable a server component to start automatically."""
    util.message(f"service.enable({component})", "debug")

    if component is None: 
        util.exit_message("You must enable one component at a time")

    util.check_server(component, "enable")

    util.update_component_state(component, "enable")
    util.run_script(component, f"start-{component}", "start")


def disable(component=None):
    """Disable a server component from starting automatically."""
    util.message(f"service.disable({component})", "debug")

    if component is None: 
        util.exit_message("You must disable one component at a time")

    util.check_server(component, "disable")

    util.run_script(component, f"stop-{component}", "stop")
    util.update_component_state(component, "disable")
    util.run_script(component, f"disable-{component}", "disable")


def config(component):
    """Configure a component."""
    util.message(f"service.config({component})", "debug")

    util.check_server(component, "config")

    run_cmd("config", component)


def init(component):
    """Initialize a component."""
    util.message(f"service.init({component})", "debug")

    util.check_server(component, "init")

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
