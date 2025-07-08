
#  Copyright 2022-2025 PGEDGE  All rights reserved. #

import os, sys, glob, sqlite3, time
import fire, meta, util
from cluster import load_json, get_cluster_json   # helper functions for reading cluster JSON
import subprocess
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
    util.message(f"um.remove_comp({p_comp})", "debug")
    msg = p_comp + " removing"
    util.message(msg, "info", isJSON)
    script_name = "remove-" + p_comp
    if os.path.isdir(p_comp):
        util.run_script(p_comp, script_name, "")
        util.delete_dir(p_comp)
    if meta.is_extension(p_comp):
        util.run_script(meta.get_extension_parent(p_comp), script_name, "")
    return 0


def run_cmd(p_cmd, p_comp=None):
    nc_cmd = "./pgedge " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def list(components=False, aliases=False):
    """Display available/installed components."""

    util.message(f"um.list({components})", "debug")

    if components is True:
        list_components()
    elif aliases is True:
        list_aliases()
    else:
        meta.get_list(isJSON, "all")


def list_components():
    lc = meta.list_components()
    for c in lc:
        print(c)


def list_aliases():
    la = meta.list_aliases()
    for a in la:
        print(a)


def update():
    """Update with a new list of available components."""
    run_cmd("update")


def install(component, active=True):
    """Install a component."""

    if active not in (True, False):
        util.exit_message("'active' parm must be True or False")
    
    cmd = "install"
    if active is False:
        cmd = "install --no-preload"

    util.message(f"um.install({cmd} {component})", "debug")
    run_cmd(cmd, component)


def remove(component):
    """Uninstall a component."""
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
    """Perform an upgrade to a newer version of a component."""

    run_cmd("upgrade", component)


def download(component):
    """Download a component into local cache (without installing it)."""

    util.download_component(component)
    return


def download_all():
    """Download pg15 & pg16 components into local cache."""

    comp_l = [
        "pg16", "spock40-pg16", "spock33-pg16", "lolor-pg16",
        "snowflake-pg16", "postgis-pg16", "vector-pg16",
        "pg15", "spock40-pg15", "spock33-pg15", "lolor-pg15",
        "snowflake-pg15", "postgis-pg15", "vector-pg15",
        "pgcat", "etcd", "patroni", "backrest", "bouncer"
        ]

    os.environ["isSilent"] = "True"
    for c in comp_l:
        util.download_component(c)

    return


def make_bundle():
    """Make a tarball of pg15 & pg16 components."""

    bundle = f"pgedge-{util.MY_VERSION}-{util.get_ctlib_dir()}.tgz"
    print(f"make_bundle() - {bundle}")

    os.chdir("/tmp")

    os.system(f"rm -f {bundle}")
    os.system("rm -f install.py")
    os.system("rm -rf pgedge")
 
    repo = util.get_value('GLOBAL', 'REPO') 
    util.echo_cmd(f"wget {repo}/install.py")
    util.echo_cmd("python3 install.py")

    util.echo_cmd("pgedge/pgedge um download-all")

    util.echo_cmd(f"tar czf {bundle} pgedge")

    os.system("rm -f install.py")
    os.system("rm -rf pgedge")

    os.system(f"ls -lh /tmp/{bundle}")

    return


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


def verify_metadata(Project="", Stage="prod", IsCurrent=0):
    """Display component metadata from the local store"""
    sql = f"""
SELECT r.project, r.component, r.stage, v.version, v.platform, 
        v.is_current, v.release_date, p.port as default_port
  FROM projects p, releases r, versions v
 WHERE p.project = r.project
   AND r.component = v.component
   AND p.project like '{Project}%'
   AND r.stage like '{Stage}%'
   AND v.is_current >= {IsCurrent}
ORDER BY 1, 2, 3, 7"""

    util.message(f"{sql}", "debug")

    meta.pretty_sql(sql)



import os
import subprocess

def upgrade_spock(cluster_name: str, new_spock_ver: str):
    """
    Upgrade the Spock extension cluster-wide.

    ./pgedge um upgrade-spock <cluster_name> <new_spock_ver>
    """
    # 1. Warn that downgrades (or same‐version/minor upgrades) aren’t supported
    util.message(
        "WARNING: Downgrading to a previous Spock version—or upgrading within the same major version—is not supported; "
        "only upgrades to a newer major version are allowed.",
        "warn",
        isJSON,
    )

    # 2. Load cluster JSON
    util.message(f"## Loading cluster '{cluster_name}' JSON definition file", "info", isJSON)
    try:
        db, db_settings, nodes = load_json(cluster_name)
    except Exception as e:
        util.exit_message(f"Unable to load cluster JSON: {e}", 1, isJSON)

    if not nodes:
        parsed = get_cluster_json(cluster_name)
        if not parsed or not parsed.get("nodes"):
            util.exit_message("Unable to load cluster JSON", 1, isJSON)
        nodes = parsed["nodes"]

    # 3. Extract node directories
    node_dirs = []
    for n in nodes:
        dir_ = n.get("node_dir") or n.get("dir") or n.get("path")
        if dir_:
            node_dirs.append(dir_)
    if not node_dirs:
        util.exit_message("No node_dir entries found in cluster JSON.", 1, isJSON)
    util.message(f"Discovered node directories: {', '.join(node_dirs)}", "info", isJSON)

    # 4. Auto-detect current Spock version from JSON
    current_spock_ver = db_settings.get("spock_version")
    if not current_spock_ver:
        util.exit_message(
            "Current Spock version not found in cluster JSON (expected db_settings['spock_version']).",
            1,
            isJSON
        )
    util.message(
        f"Detected current Spock version from JSON: {current_spock_ver}",
        "info",
        isJSON
    )

    # 5. Refuse no-ops
    if new_spock_ver == current_spock_ver:
        util.exit_message(
            f"New Spock version {new_spock_ver} is the same as the current version.",
            1,
            isJSON
        )

    # 5.1 Compare major versions as strings
    try:
        current_major = current_spock_ver.split(".")[0]
        new_major = new_spock_ver.split(".")[0]
    except IndexError:
        util.exit_message(
            f"Invalid Spock version format. Got current='{current_spock_ver}', requested='{new_spock_ver}'.",
            1,
            isJSON
        )

    if new_major <= current_major:
        util.exit_message(
            f"Invalid upgrade: new Spock major version {new_major} must be greater than current major version {current_major}.",
            1,
            isJSON
        )

    # 6. If upgrading to Spock 5, install Spock5 on each node
    if new_major == "5":
        for dir_ in node_dirs:
            pgedge_dir = os.path.join(dir_, "pgedge")
            util.message(
                f"Installing Spock5 on node at '{pgedge_dir}'",
                "info",
                isJSON
            )
            try:
                subprocess.run(["./pgedge", "um", "install", "spock5"], cwd=pgedge_dir, check=True)
            except subprocess.CalledProcessError as e:
                util.exit_message(
                    f"Spock5 installation failed in '{pgedge_dir}': {e}",
                    1,
                    isJSON
                )

    # 7. Warn about downtime
    util.message(
        f"WARNING: Upgrading Spock on cluster '{cluster_name}' "
        f"from {current_spock_ver} to {new_spock_ver} will cause downtime; "
        "all nodes will be restarted.",
        "warn",
        isJSON,
    )

    # 8. Check for Backrest configuration and run pgBackRest backups
    for n in nodes:
        br = n.get("backrest")
        if br:
            stanza = br.get("stanza")
            node_name = n.get("name") or n.get("node_dir") or "unknown"
            node_dir = n.get("node_dir") or n.get("dir") or n.get("path")
            pgedge_dir = os.path.join(node_dir, "pgedge")

            util.message(
                f"Running pgBackRest backup for stanza '{stanza}' on node '{node_name}'",
                "info",
                isJSON
            )
            try:
                subprocess.run(["./pgedge", "backrest", "backup", stanza], cwd=pgedge_dir, check=True)
            except subprocess.CalledProcessError as e:
                util.exit_message(
                    f"pgBackRest backup failed on node '{node_name}': {e}",
                    1,
                    isJSON
                )

    # 9. Determine the running PostgreSQL version
    try:
        pg_version = db_settings.get("pg_version") or util.fetch_pg_version(node_dirs[0])
        util.message(f"Detected PostgreSQL version: {pg_version}", "info", isJSON)
    except Exception as e:
        util.exit_message(f"Unable to determine PostgreSQL version: {e}", 1, isJSON)

    # 10. Validate compatibility
    util.validate_spock_pg_compat(current_spock_ver, pg_version)

    # 11. Success
    util.exit_message(
        f"Successfully upgraded Spock to {new_spock_ver} on cluster '{cluster_name}'.",
        0,
        isJSON
    )



if __name__ == "__main__":
    fire.Fire(
        {
            "list": list,
            "update": update,
            "install": install,
            "remove": remove,
            "upgrade": upgrade,
            "clean": clean,
            "verify-metadata": verify_metadata,
            "download": download, 
            "upgrade-spock": upgrade_spock, 
        }
    )
