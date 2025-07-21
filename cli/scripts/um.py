
#  Copyright 2022-2025 PGEDGE  All rights reserved. #

import os, sys, glob, sqlite3, time
import fire, meta, util
isJSON = util.isJSON
import re
import sqlite3 as _sqlite3

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
    """Install a component or trigger Spock upgrade for spock50-pg<major>."""
    # Only invoke upgrade_spock when installing spock50-pg*
    if component.startswith("spock50-pg"):
        print(f"Detected Spock upgrade target '{component}', invoking upgrade_spock()...\n")
        upgrade_spock()
        # After successful compatibility, proceed with install
        util.message(f"um.install(install {component})", "debug")
        run_cmd("install", component)
        return

    if active not in (True, False):
        util.exit_message("'active' parm must be True or False")
    cmd = "install"
    if not active:
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




# Regex that matches typical Spock‑5 version strings or component names
_SPOCK5_RE = re.compile(r"^(?:spock)?5[0-9\.]*$", re.IGNORECASE)


def upgrade_spock():
    """
    Validate Spock ↔ PostgreSQL compatibility **unless Spock 5 is already installed**.

    Behaviour
    ---------
    • If any installed Spock component matches `_SPOCK5_RE`, print a notice and EXIT 0.  
    • Otherwise, warn about downtime, read PG/Spock versions from SQLite,
      do util.validate_spock_pg_compat(), and exit(1) on any error.
    """
    DB_PATH = "data/conf/db_local.db"
    VERSION_SQL = """
        SELECT pg.version      AS pg_ver,
               sp.version      AS spock_ver,
               sp.component    AS spock_comp
          FROM components AS pg
          LEFT JOIN components AS sp
                 ON sp.component LIKE 'spock%' || pg.component
         WHERE pg.component IN ('pg11','pg12','pg13','pg14','pg15','pg16','pg17')
         LIMIT 1;
    """

    # ── fetch versions ────────────────────────────────────────────────────────────
    try:
        with _sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(VERSION_SQL).fetchone()
    except _sqlite3.Error as err:
        sys.exit(f"ERROR: SQLite query failed: {err}")

    if not row:
        sys.exit("ERROR: No PostgreSQL/Spock version row found.")

    pg_ver, spock_ver, spock_comp = row

    # ── early‑exit if Spock 5 already installed ──────────────────────────────────
    if any(_SPOCK5_RE.match(x or "") for x in (spock_ver, spock_comp)):
        print(f"Spock 5 already installed (component='{spock_comp}', version='{spock_ver}').")
        print("Nothing to do — skipping upgrade/installation.\n")
        sys.exit(0)          # treat as successful no‑op

    # ── standard downtime banner ─────────────────────────────────────────────────
    banner = "=" * 80
    print(f"\n{banner}\n*** WARNING: This operation will cause downtime! ***\n{banner}\n")
    print(f"Detected Spock version {spock_ver} on PostgreSQL {pg_ver}")

    # ── compatibility check ──────────────────────────────────────────────────────
    try:
        util.validate_spock_pg_compat(spock_ver, pg_ver)
    except Exception as exc:
        sys.exit(f"ERROR: Compatibility check failed: {exc}")

    print("Compatibility check passed. Proceed with upgrade.")

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
        }
    )
