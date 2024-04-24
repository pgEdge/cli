
import os, sys, glob, sqlite3, time
import fire, meta, util

isJSON = util.isJSON

MY_HOME = util.MY_HOME

db_local = util.MY_LITE

connL = sqlite3.connect(db_local)

# is there a dependency violation if component where removed ####
def is_depend_violation(p_comp, p_remove_list):
    data = meta.get_dependent_components(p_comp)

    kount = 0
    vv = []
    for i in data:
        if str(i[0]) in p_remove_list:
            continue
        kount = kount + 1
        vv.append(str(i[0]))

    if kount == 0:
        return False

    errMsg = "Failed to remove " + p_comp + "(" + str(vv) + " is depending on this)."
    util.exit_message(errMsg, 1, isJSON)

    return True

def remove_comp(p_comp):
    msg = p_comp + " removing"
    util.message(msg, "info", isJSON)
    script_name = "remove-" + p_comp
    if os.path.isdir(p_comp):
        util.run_script(p_comp, script_name, "")
        util.delete_dir(p_comp)
    if meta.is_extension(p_comp):
        util.run_script(meta.get_extension_parent(p_comp), script_name, "")
        manifest_file_name = p_comp + ".manifest"
        manifest_file_path = os.path.join(MY_HOME, "data", "conf", manifest_file_name)
        util.delete_extension_files(manifest_file_path)
        util.message("deleted manifest file : " + manifest_file_name, "info", isJSON)
        os.remove(manifest_file_path)
    return 0


def run_cmd(p_cmd, p_comp=None):
    nc_cmd = "./pgedge " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def list():
    """Display available/installed components"""
    meta.get_list(isJSON, "all")


def update():
    """Update with a new list of available components"""
    run_cmd("update")


def install(component, active=True):
    """Install a component"""

    if active not in (True, False):
        util.exit_message("'active' parm must be True or False")
    
    cmd = "install"
    if active is False:
        cmd = "install --no-preload"

    util.message(f"um.install({cmd} {component})", "debug")
    run_cmd(cmd, component)


def remove(component):
    """Uninstall a component"""
    installed_comp_list = meta.get_component_list()
    init_comp_list=[]
    p_comp=component
    if p_comp is not None:
        init_comp_list=component.split()
    info_arg, p_comp_list, p_comp, p_version, extra_args = util.get_comp_lists("remove", -1, init_comp_list, [], "", connL)
    if p_comp == "all":
        msg = "You must specify component to remove."
        util.exit_message(msg, 1, isJSON)
    for c in p_comp_list:
        if c not in installed_comp_list:
            msg = c + " is not installed."
            print(msg)
            continue

        if is_depend_violation(c, p_comp_list):
            util.exit_cleanly(1,connL)

        server_port = util.get_comp_port(c)

        server_running = False
        if server_port > "1":
            server_running = util.is_socket_busy(int(server_port), c)

        if server_running:
            cmd = "stop c"
            util.run_script(p_comp, "stop-" + p_comp, "stop")
            time.sleep(5)
        
        remove_comp(c)

        extensions_list = meta.get_installed_extensions_list(c)
        for ext in extensions_list:
            util.update_component_state(ext, "remove")

        util.update_component_state(c, "remove")
        comment = f"Successfully removed the component {component}"
        util.message(comment, "info", isJSON)

    util.exit_cleanly(0,connL)


def upgrade(component):
    """Perform an upgrade  to a newer version of a component"""

    run_cmd("upgrade", component)


def downgrade(component):
    """Perform a downgrade to an older version of a component"""

    run_cmd("downgrade", component)


def clean():
    """Delete downloaded component files from local cache"""
    conf_cache = util.MY_HOME + os.sep + "data" + os.sep + "conf" + os.sep + "cache" + os.sep + "*"
    files = glob.glob(conf_cache)
    kount = 0
    for f in files:
        kount = kount + 1
        util.message(f"deleting {f}")
        os.remove(f)

    msg = ""
    if kount == 0:
       msg = "local cache is already empty"

    util.exit_message(msg, 0)


if __name__ == "__main__":
    fire.Fire(
        {
            "list": list,
            "update": update,
            "install": install,
            "remove": remove,
            "upgrade": upgrade,
            "clean": clean,
        }
    )
