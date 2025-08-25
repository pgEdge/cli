
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



# Match both "spock50" and "spock50-pg17" (and variants like spock5, spock5-pg16)
_SPOCK5_NAME_RE = re.compile(r"^spock5(?:0)?(?:-pg\d+)?$", re.IGNORECASE)
_SPOCK5_VER_RE  = re.compile(r"^5\.", re.IGNORECASE)
_SPOCK50_RE = re.compile(r"^spock50(?:-pg\d+)?$", re.IGNORECASE)

def install(component, active=True):
    """Install a component."""

    # Trigger pre-check ONLY for Spock 5.0 artifacts
    if _SPOCK50_RE.match(component):
        validate_spock_upgrade(component)   # should sys.exit(1) on failure; otherwise just returns

    # Common path (no duplication)
    if active not in (True, False):
        util.exit_message("'active' parm must be True or False")

    cmd = "install" if active else "install --no-preload"
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

def get_guc_value(pg_comp, guc_name):
    """
    Look up the value of a GUC from postgresql.auto.conf (preferred) or
    postgresql.conf
    Returns 'on' / 'off' / <string> if set, or None if not found.
    """

    # Prefer postgresql.auto.conf, fallback to postgresql.conf
    for conf_path in [util.get_pgconf_filename_auto(pg_comp), util.get_pgconf_filename(pg_comp)]:
        if not os.path.isfile(conf_path):
            continue

        try:
            with open(conf_path, "r", encoding="utf-8", errors="ignore") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower().startswith(guc_name.lower()):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip("'\"").lower()
                            return val
        except Exception:
            return None

    return None

def validate_spock_upgrade(spock_component):
    """
    Validate Spock↔PostgreSQL compatibility for an upcoming Spock 5 install.
    Enforces that Spock DDL-related settings are OFF before proceeding.
    """

    DB_PATH = "data/conf/db_local.db"


    SPOCK_SQL = """
    SELECT version AS spock_ver, component AS spock_comp
    FROM components
    WHERE component LIKE 'spock%'
    ORDER BY CASE
               WHEN version LIKE '5.%' THEN 5
               WHEN version LIKE '4.%' THEN 4
               ELSE 0
             END DESC,
             version DESC
    LIMIT 1;
    """
    PG_SQL = """
    SELECT component AS pg_comp, version AS pg_ver
    FROM components
    WHERE component LIKE 'pg__'
    ORDER BY CAST(substr(component, 3) AS INTEGER) DESC
    LIMIT 1;
    """

    # --- Read currently installed PG/Spock from local metadata ---------------
    try:
        with _sqlite3.connect(DB_PATH) as conn:
            sp_row = conn.execute(SPOCK_SQL).fetchone()
            pg_row = conn.execute(PG_SQL).fetchone()
    except _sqlite3.Error as err:
        sys.exit(f"ERROR: SQLite query failed: {err}")

    if not pg_row:
        sys.exit("ERROR: No PostgreSQL version row found.")

    existing_pg_comp, existing_pg_ver = pg_row[0], pg_row[1]
    existing_spock_ver, existing_spock_comp = (sp_row or (None, None))

    # If already on Spock 5, nothing to do (no gate, no compat check).
    if existing_spock_ver and (
        _SPOCK5_NAME_RE.match(existing_spock_comp or "")
        or _SPOCK5_VER_RE.match(existing_spock_ver or "")
    ):
        return 0


    # EARLY EXIT: Check postgresql.auto.conf (preferred) or postgresql.conf for DDL GUCs
    for guc in [
        "spock.enable_ddl_replication",
        "spock.include_ddl_repset",
        "spock.allow_ddl_from_functions",
    ]:
        val = get_guc_value(existing_pg_comp, guc)
        if val == "on":
            print(
                f"ERROR: {guc} must be set to off before upgrading to Spock 5.0."
            )
            sys.exit(1)

    # Continue with version compatibility checks
    requested_spock_ver = spock_component
    if requested_spock_ver and requested_spock_ver.lower().startswith("spock"):
        requested_spock_ver = requested_spock_ver[5:]

    # Friendly downtime banner if upgrading from existing Spock
    if existing_spock_ver:
        banner = "=" * 80
        print(f"\n{banner}")
        print("*** WARNING: This operation will cause downtime! ***")
        print(f"{banner}\n")
        print(
            f"Detected existing Spock version {existing_spock_ver} "
            f"on PostgreSQL {existing_pg_ver}"
        )

    try:
        util.validate_spock_pg_compat(requested_spock_ver, existing_pg_ver)
    except Exception as exc:
        sys.exit(f"ERROR: Compatibility check failed: {exc}")

    if existing_spock_ver:
        print("Compatibility check passed.")

    return 0

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
