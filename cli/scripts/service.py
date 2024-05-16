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
    """Start server components"""
    dep9 = util.get_depend()
    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        ## Iterate through components in primary list order.
        ## Components with a port of "1" are client components that
        ## are only launched when explicitely started
        for comp in dep9:
            if util.is_server(comp[0]):
                script_name = "start-" + comp[0]
                util.run_script(comp[0], script_name, "start")
    else:
        present_state = util.get_comp_state(p_comp)
        if present_state == "NotInstalled":
            msg = "Component '" + p_comp + "' is not installed."
            util.exit_message(msg, 0)
        if not util.is_server(p_comp):
            msg = "'" + p_comp + "' component cannot be started."
            util.exit_message(msg, 0)
            util.exit_cleanly(1,connL)
        if not present_state == "Enabled":
            util.update_component_state(p_comp, "enable")
        script_name = "start-" + p_comp
        util.run_script(p_comp, script_name, "start")


def stop(component=None):
    """Stop server components"""
    dep9 = util.get_depend()
    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        ## iterate through components in reverse list order
        for comp in reversed(dep9):
            script_name = "stop-" + comp[0]
            util.run_script(comp[0], script_name, "stop")
    else:
        script_name = "stop-" + p_comp
        util.run_script(p_comp, script_name, "stop")


def status(component=None):
    """Display running status of installed server components"""
    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    for c in p_comp_list:
        check_status(c, "status")
    util.exit_cleanly(0,connL)


def restart(component=None):
    """Stop & then start server components"""
    dep9 = util.get_depend()
    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        ## iterate through components in reverse list order
        for comp in reversed(dep9):
            script_name = "stop-" + comp[0]
            util.run_script(comp[0], script_name, "stop")
    else:
        script_name = "stop-" + p_comp
        util.run_script(p_comp, script_name, "stop")
    if p_comp == "all":
        ## Iterate through components in primary list order.
        ## Components with a port of "1" are client components that
        ## are only launched when explicitely started
        for comp in dep9:
            if util.is_server(comp[0]):
                script_name = "start-" + comp[0]
                util.run_script(comp[0], script_name, "start")
    else:
        present_state = util.get_comp_state(p_comp)
        if present_state == "NotInstalled":
            msg = "Component '" + p_comp + "' is not installed."
            util.exit_message(msg, 0)
        if not util.is_server(p_comp):
            msg = "'" + p_comp + "' component cannot be started."
            util.exit_message(msg, 0)
            util.exit_cleanly(1,connL)
        if not present_state == "Enabled":
            util.update_component_state(p_comp, "enable")
        script_name = "start-" + p_comp
        util.run_script(p_comp, script_name, "start")


def reload(component):
    """Reload server configuration files (without a restart)"""

    run_cmd("reload", component)


def enable(component=None):
    """Enable a component"""
    util.message(f"service.enable({component})", "debug")

    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        msg = "You must enable one component at a time"
        util.exit_message(msg, 1, isJSON)

    util.update_component_state(p_comp, "enable")
    script_name = "enable-" + p_comp
    sys.exit(util.run_script(p_comp, script_name, extra_args))


def disable(component=None):
    """Disable a server component from starting automatically"""
    util.message(f"service.disable({component})", "debug")

    init_comp_list=[]
    if component is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("status", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        msg = "You must disable one component at a time"
        util.exit_message(msg, 1, isJSON)
    util.update_component_state(p_comp, "disable")
    script_name = "disable-" + p_comp
    sys.exit(util.run_script(p_comp, script_name, extra_args))


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
