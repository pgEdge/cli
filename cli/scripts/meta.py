#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import sys, os, sqlite3, json
from semantic_version import Version

import api, util
import datetime


def get_extension_meta(component):
    data = []
    sql = "SELECT extension_name, is_preload, preload_name, default_conf\n" + \
         f"  FROM extensions WHERE component = '{component}'"
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchone()
        if data:
            return str(data[0]), data[1], str(data[2]), str(data[3])
        else:
            return None, None, None, None
    except Exception as e:
        fatal_error(e, sql, "get_extension_meta")


def get_installed_count():
    data = []
    sql = "SELECT count(*) FROM components WHERE component <> 'hub'"
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchone()
        return data[0]
    except Exception as e:
        fatal_error(e, sql, "get_installed_count")


def get_installed_pg():
    data = []
    sql = "SELECT component FROM components WHERE component like 'pg1%'"
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()
    except Exception as e:
        fatal_error(e, sql, "get_installed_pg")

    return data

'''
Accepts a connection object and returns the version of spock installed

@param: conn - connection object
@return: float - version of spock installed

'''
def get_spock_version(conn):
    data = []
    sql = "SELECT spock.spock_version();"
    try:
        c = conn.cursor()
        c.execute(sql)
        data = c.fetchone()
        if data:
            return float(data[0])
    except Exception as e:
        fatal_error(e, sql, "get_spock_version()")

    return 0.0


def get_stage(p_comp):
    try:
        c = con.cursor()
        sql = "SELECT stage FROM releases WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data:
            return str(data[0])
    except Exception as e:
        fatal_error(e, sql, "meta.get_stage()")

    return ""


def check_pre_reqs(p_comp, p_ver):
    # scrub the platform off the end of the version
    scrub_ver = p_ver.replace("-amd", "")
    scrub_ver = scrub_ver.replace("-arm", "")

    try:
        c = con.cursor()
        sql = "SELECT pre_reqs FROM versions WHERE component = ? and version = ?"
        c.execute(sql, [p_comp, scrub_ver])
        data = c.fetchone()
        if data:
            pre_req = str(data[0])
            if pre_req > "":
                MY_HOME = os.getenv("MY_HOME")
                req_sh = os.path.join(MY_HOME, "hub", "scripts", "check_pre_reqs.sh")
                rc = os.system(req_sh + " " + pre_req)
                if rc == 0:
                    return True
                else:
                    return False
    except Exception as e:
        fatal_error(e, sql, "meta.check_pre_reqs()")

    return True


def exec_sql_list(sql):
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()
        c.close()
    except Exception as e:
        fatal_error(e, sql, "meta.exec_sql_list()")

    return data


def exec_sql(sql, in_vars, commit=True):
    try:
        c = con.cursor()
        sql_type_list = sql.split()
        sql_type = sql_type_list[0].upper()
        c.execute(sql, in_vars)
        if sql_type == "SELECT":
            data = c.fetchone()
        else:
            data = None
            if commit:
                con.commit()
        c.close()
    except Exception as e:
        util.message(str(e), "error")
        return None

    return data


def put_components(
    p_comp,
    p_proj,
    p_ver,
    p_plat,
    p_port,
    p_stat,
    p_autos,
    p_datadir,
    p_logdir,
    p_svcname,
    p_svcuser,
):
    try:
        c = con.cursor()
        sql = "DELETE FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        sql = (
            "INSERT INTO components \n"
            + "  (component, project, version, platform, port, status, \n"
            + "   autostart, datadir, logdir, svcname, svcuser) \n"
            + "VALUES \n"
            + "  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        c.execute(
            sql,
            [
                p_comp,
                p_proj,
                p_ver,
                p_plat,
                p_port,
                p_stat,
                p_autos,
                p_datadir,
                p_logdir,
                p_svcname,
                p_svcuser,
            ],
        )
        con.commit()
        c.close()
    except Exception as e:
        fatal_error(e, sql, "meta.put_components()")
    return


def get_extension_parent(ext_comp):
    ndx = ext_comp.index("-pg")
    return ext_comp[(ndx + 1) :]


def check_release(p_wild):
    data = []
    sql = (
        "SELECT r.component FROM releases r, versions v \n"
        + " WHERE r.component = v.component \n"
        + "   AND r.component LIKE '"
        + p_wild
        + "' AND v.is_current >= 1"
    )
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()
    except Exception as e:
        fatal_error(e, sql, "check_release")
    ret = ""
    if len(data) == 1:
        for comp in data:
            ret = str(comp[0])
    return ret


#############################################################################
# If the prefix for a component uniquely matches only one component, then
#  expand the prefix into the full component name
#############################################################################
def wildcard_component(p_component):
    # Trim slashes for dweeb convenience
    p_comp = p_component.replace("/", "")
    if p_comp == "spock":
        p_comp = util.DEFAULT_SPOCK

    comp = check_release(p_comp)
    if comp > "":
        return comp

    comp = check_release("%" + p_comp + "%")
    if comp > "":
        return comp

    # check if only a single version of PG is installed ###
    pg_ver = ""
    data = []
    sql = (
        "SELECT component FROM components"
        + " WHERE component in ('pg11', 'pg12', 'pg13', 'pg14', 'pg15', 'pg16', 'pg17')"
    )
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()
    except Exception as e:
        fatal_error(e, sql, "wildcard_component")
    if len(data) == 1:
        for comp in data:
            pg_ver = str(comp[0])
    else:
        return p_comp

    # if only single version of PG installed, see if we match with that suffix
    comp = check_release("%" + p_comp + "%-" + pg_ver)
    if comp > "":
        return comp

    return p_comp


#############################################################################
# expand the prefix for a component's version number into the full version
#  number for the most recent version that matches
#############################################################################
def wildcard_version(p_comp, p_ver):
    try:
        # for an exact match then don't try the wildcard
        sql = "SELECT count(*) FROM versions WHERE component = ? AND version = ?"
        c = con.cursor()
        c.execute(sql, [p_comp, p_ver])
        data = c.fetchone()
        if data[0] == 1:
            # return the parm that was passed into this function
            return p_ver

        sql = (
            "SELECT release_date, version FROM versions \n"
            + " WHERE component = ? AND version LIKE ? \n"
            + "ORDER BY 1 DESC"
        )
        c = con.cursor()
        c.execute(sql, [p_comp, p_ver + "%"])
        data = c.fetchone()
        if data is None:
            # return the parm that was passed into this function
            return p_ver

    except Exception as e:
        fatal_error(e, sql, "wildcard_version")

    # return the full version number from the sql statement
    return str(data[1])


def is_present(p_table, p_key, p_value, p_any="one"):
    sql = (
        "SELECT count(*) "
        + "  FROM "
        + str(p_table)
        + " WHERE "
        + str(p_key)
        + " = '"
        + str(p_value)
        + "'"
    )
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchone()

        if p_any == "one":
            if data[0] == 1:
                return True
        elif p_any == "any":
            if data[0] >= 1:
                return True

    except Exception as e:
        fatal_error(e, sql, "meta.is_present()")

    return False


def is_node(p_node):
    return is_present("nodes", "node", p_node)


def is_component(p_comp):
    return is_present("releases", "component", p_comp)


def is_any_autostart():
    return is_present("components", "autostart", "on", "any")


def is_extension(ext_comp):
    ## util.message(f"meta.is_extension({ext_comp})", "debug")
    try:
        c = con.cursor()
        sql = f"SELECT count(*) FROM versions WHERE component = '{ext_comp}' AND parent > ''"
        c.execute(sql)
        data = c.fetchone()
        if data[0] == 0:
            ## util.message("  - FALSE", "debug")
            return False
    except Exception as e:
        fatal_error(e, sql, "meta.is_extension()")

    ## util.message("  - TRUE", "debug")
    return True


def list_components():
    try:
        c = con.cursor()
        cols = "component, project, version, platform, port, status, install_dt, autostart"
        sql = f"SELECT {cols} FROM components"
        c.execute(sql)
        t_comp = c.fetchall()
        r_comp = []
        for c in t_comp:
            r_comp.append([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]])
    except Exception as e:
        fatal_error(e, sql, "meta.list_components()")

    return r_comp


def get_available_component_list():
    try:
        c = con.cursor()
        sql = (
            "SELECT v.component FROM versions v WHERE v.is_current = 1 \n"
            + "   AND "
            + util.like_pf("v.platform")
        )
        c.execute(sql)
        t_comp = c.fetchall()
        r_comp = []
        for comp in t_comp:
            r_comp.append(str(comp[0]))
    except Exception as e:
        fatal_error(e, sql, "meta.get_available_component_list()")
    return r_comp


def get_all_components_list(p_component=None, p_version=None, p_platform=None):
    try:
        c = con.cursor()
        sql = "SELECT v.component, v.version, v.platform" + "  FROM versions v "
        if p_version is None:
            sql = sql + " WHERE v.is_current = 1 "
        elif p_version == "all":
            sql = sql + " WHERE v.is_current >= 0 "

        if p_platform is None:
            sql = sql + " AND " + util.like_pf("v.platform") + " "
        if p_component:
            sql = sql + " AND v.component = '" + p_component + "'"
        if p_version and p_version != "all":
            sql = sql + " AND v.version = '" + p_version + "'"

        c.execute(sql)
        t_comp = c.fetchall()
        r_comp = []
        for comp in t_comp:
            if p_platform == "all":
                if comp[2]:
                    platforms = comp[2].split(",")
                    for p in platforms:
                        comp_dict = {}
                        comp_dict["component"] = str(comp[0])
                        version = str(comp[1]) + "-" + p.strip()
                        comp_dict["version"] = version
                        r_comp.append(comp_dict)
                else:
                    comp_dict = {}
                    comp_dict["component"] = str(comp[0])
                    version = str(comp[1])
                    if comp[2]:
                        if p_platform is None:
                            version = str(comp[1]) + "-" + util.get_pf()
                        else:
                            version = str(comp[1]) + "-" + p_platform
                    comp_dict["version"] = version
                    r_comp.append(comp_dict)
            else:
                comp_dict = {}
                comp_dict["component"] = str(comp[0])
                version = str(comp[1])
                if comp[2]:
                    if p_platform is None:
                        version = str(comp[1]) + "-" + util.get_pf()
                    else:
                        version = str(comp[1]) + "-" + p_platform
                comp_dict["version"] = version
                r_comp.append(comp_dict)
    except Exception as e:
        fatal_error(e, sql, "meta.get_all_components_list()")
    return r_comp


def update_component_version(p_app, p_version):
    try:
        c = con.cursor()
        update_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE components SET version = ?,install_dt = ? WHERE component = ?"
        c.execute(sql, [p_version, update_date, p_app])
        con.commit()
        c.close()
    except Exception as e:
        fatal_error(e, sql, "meta.update_component_version()")

    return


# Get Component Version & Platform ########################################
def get_ver_plat(p_comp):
    try:
        c = con.cursor()
        sql = "SELECT version, platform FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "-1"
    except Exception as e:
        fatal_error(e, sql, "meta.get_ver_plat()")
    version = str(data[0])
    platform = str(data[1])
    if platform == "":
        return version
    return version + "-" + platform


# Get latest current version & platform ###################################
def get_latest_ver_plat(p_comp, p_new_ver=""):
    try:
        c = con.cursor()
        sql = (
            "SELECT version, platform, is_current, release_date \n"
            + "  FROM versions \n"
            + " WHERE component = ? \n"
            + "   AND "
            + util.like_pf("platform")
            + "\n"
            + "ORDER BY 3 DESC, 4 DESC"
        )
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "-1"
    except Exception as e:
        fatal_error(e, sql, "meta.get_latest_ver_plat()")
    if p_new_ver == "":
        version = str(data[0])
    else:
        version = p_new_ver
    platform = str(data[1])
    pf = util.get_pf()
    if platform == "":
        ver_plat = version
    else:
        if pf in platform:
            ver_plat = version + "-" + pf
        else:
            ver_plat = version + "-amd"
    return ver_plat


# Get platform specific version for component ###############################
def get_platform_specific_version(p_comp, p_ver):
    try:
        c = con.cursor()
        sql = (
            "SELECT version, platform FROM versions "
            + " WHERE component = ? "
            + "   AND "
            + util.like_pf("platform")
            + "   AND version = ?"
        )
        c.execute(sql, [p_comp, p_ver])
        data = c.fetchone()
        if data is None:
            return "-1"
    except Exception as e:
        fatal_error(e, sql, "meta.get_platform_specific_version()")
    version = str(data[0])
    platform = str(data[1])
    if platform == "":
        return version
    return version + "-" + util.get_pf()


# get list of installed & available components ###############################
def get_list(p_isJSON, p_comp=None, p_return=False):
    r_sup_plat = "1 = 1"

    if util.isSHOWDUPS:
        exclude_comp = ""
    else:
        exclude_comp = " AND v.component NOT IN (SELECT component FROM components)"

    my_in = "'prod'"
    if util.isTEST:
        my_in = my_in + ", 'test'"

    exclude_comp = exclude_comp + f" AND r.stage in ({my_in})"

    installed_category_conditions = " AND p.category > 0 "
    available_category_conditions = " AND p.category > 0 AND p.is_extension = 0"
    ext_component = ""

    extra_extensions = "('')"

    if util.isEXTENSIONS:
        installed_category_conditions = (
            " AND ((p.is_extension = 1) OR (c.component in " + extra_extensions + "))"
        )
        available_category_conditions = (
            " AND ((p.is_extension = 1) OR (v.component in " + extra_extensions + "))"
        )
        if p_comp != "all":
            ext_component = " AND parent = '" + p_comp + "' "

    installed = (
        "SELECT p.category, g.description as category_desc, g.short_desc as short_cat_desc, \n"
        + "       c.component, c.version, c.port, c.status, r.stage, \n"
        + "       coalesce((select is_current from versions where c.component = component AND c.version = version),0), \n"
        + "       c.datadir, p.is_extension, \n"
        + "       coalesce((select parent from versions where c.component = component and c.version = version),'') as parent, \n"
        + "       coalesce((select release_date from versions "
        +  "       where c.component = component and c.version = version),'20200101'), \n"
        + "       c.install_dt, r.disp_name, \n"
        + "       coalesce((select release_date from versions where c.component = component and is_current = 1),'20200101'), \n"
        + "       r.is_available, r.available_ver, '' as pre_reqs \n"
        + "  FROM components c, releases r, projects p, categories g \n"
        + " WHERE c.component = r.component AND r.project = p.project \n"
        + "   AND p.category = g.category \n"
        + "   AND "
        + r_sup_plat
        + installed_category_conditions
        + ext_component
    )

    available = (
        "SELECT c.category, c.description, c.short_desc as short_cat_desc, v.component, v.version, 0, 'NotInstalled', \n"
        + "       r.stage, v.is_current, '', p.is_extension, v.parent as parent, v.release_date, '', \n"
        + "       r.disp_name, \n"
        + "       coalesce((select release_date from versions where v.component = component and is_current = 1),'20200101'), \n"
        + "       r.is_available, r.available_ver, v.pre_reqs \n"
        + "  FROM versions v, releases r, projects p, categories c \n"
        + " WHERE v.component = r.component AND r.project = p.project \n"
        + "   AND p.category = c.category AND v.is_current = 1 \n"
        + "   AND "
        + util.like_pf("v.platform")
        + " \n"
        + "   AND "
        + r_sup_plat
        + exclude_comp
        + available_category_conditions
        + ext_component
    )

    svcs = (
        "SELECT c.category, c.description, c.short_desc as short_cat_desc, v.component, v.version, 0, 'NotInstalled', \n"
        + "       r.stage, v.is_current, '', p.is_extension, v.parent as parent, v.release_date, '', \n"
        + "       r.disp_name, \n"
        + "       coalesce((select release_date from versions where v.component = component and is_current = 1),'20200101'), \n"
        + "       r.is_available, r.available_ver, v.pre_reqs \n"
        + "  FROM versions v, releases r, projects p, categories c \n"
        + " WHERE v.component = r.component AND r.project = p.project \n"
        + "   AND p.category = c.category AND ((v.is_current = 2) or ((p.project = 'pg') AND (v.is_current =1)))"
    )

    extensions = (
        "SELECT c.category, c.description, c.short_desc as short_cat_desc, v.component, v.version, 0, 'NotInstalled', \n"
        + "       r.stage, v.is_current, '', p.is_extension, v.parent as parent, v.release_date, '', \n"
        + "       r.disp_name,  \n"
        + "       coalesce((select release_date from versions where v.component = component and is_current = 1),'20200101'), \n"
        + "       r.is_available, r.available_ver, v.pre_reqs \n"
        + "  FROM versions v, releases r, projects p, categories c \n"
        + " WHERE v.component = r.component AND r.project = p.project \n"
        + "   AND p.is_extension = 1 AND p.category = c.category \n"
        + "   AND "
        + util.like_pf("v.platform")
        + " \n"
        + "   AND v.parent in (select component from components) AND "
        + r_sup_plat
        + exclude_comp
        + "    OR v.component in "
        + extra_extensions
    )

    if os.getenv("isSVCS", "") == "True":
        sql = svcs + "\n ORDER BY 1, 3, 4, 6"
    elif util.isEXTENSIONS:
        sql = installed + "\n UNION \n" + available + "\n ORDER BY 1, 3, 4, 6"
    else:
        sql = (
            installed
            + "\n UNION \n"
            + available
            + "\n UNION \n"
            + extensions
            + "\n ORDER BY 1, 3, 4, 6"
        )

    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()

        headers = [
            "Category",
            "Component",
            "Version",
            "ReleaseDt",
            "Stage",
            "Status",
            "Updates",
            "PreReqs",
        ]
        keys = [
            "short_cat_desc",
            "component",
            "version",
            "release_date",
            "stage",
            "status",
            "current_version",
            "pre_reqs",
        ]

        jsonList = []
        kount = 0
        previous_version = None
        previous_comp = None
        for row in data:
            compDict = {}
            kount = kount + 1

            category = str(row[0])
            category_desc = str(row[1])
            short_cat_desc = str(row[2])
            comp = str(row[3])
            version = str(row[4])
            port = str(row[5])

            if previous_comp and previous_version:
                if previous_comp == comp and previous_version == version:
                    continue

            previous_version = version
            previous_comp = comp

            if str(row[6]) == "Enabled":
                status = "Installed"
            else:
                status = str(row[6])
            if status == "NotInstalled" and p_isJSON is False:
                status = ""

            is_available = str(row[16])
            if (status == "") and (is_available > ""):
                rc = os.system(is_available + " > /dev/null 2>&1")
                if rc == 0:
                    status = "Available"

            stage = str(row[7])
            if stage in ("soon", "bring-own", "included"):
                continue

            is_current = str(row[8])
            if is_current == "0" and status in ("", "NotInstalled"):
                continue

            current_version = get_current_version(comp)
            is_update_available = 0
            cv = Version.coerce(current_version)
            iv = Version.coerce(version)
            if cv > iv:
                is_update_available = 1

            if is_update_available == 0:
                updates = 0
                current_version = ""
            else:
                updates = 1

            if (port == "0") or (port == "1"):
                port = ""

            datadir = row[9]
            if row[9] is None:
                datadir = ""
            else:
                datadir = str(row[9]).strip()

            is_extension = row[10]

            parent = row[11]

            disp_name = row[14]

            release_desc = ""
            release_date = "1970-01-01"
            curr_rel_date = "1970-01-01"

            curr_rel_dt = str(row[15])
            rel_dt = str(row[12])
            if len(rel_dt) == 8:
                release_date = rel_dt[0:4] + "-" + rel_dt[4:6] + "-" + rel_dt[6:8]
                curr_rel_date = (
                    curr_rel_dt[0:4] + "-" + curr_rel_dt[4:6] + "-" + curr_rel_dt[6:8]
                )

            compDict["is_new"] = 0

            try:
                rd = datetime.datetime.strptime(release_date, "%Y-%m-%d")
                today_date = datetime.datetime.today()
                date_diff = (today_date - rd).days

                if date_diff <= 30:
                    compDict["is_new"] = 1
            except Exception:
                pass

            if util.is_postgres(comp):
                if port > "" and status == "Installed" and datadir == "":
                    status = "NotInitialized"
                    port = ""

            ins_date = str(row[13])
            install_date = ""
            compDict["is_updated"] = 0
            if ins_date:
                install_date = (
                    ins_date[0:4] + "-" + ins_date[5:7] + "-" + ins_date[8:10]
                )

                try:
                    insDate = datetime.datetime.strptime(install_date, "%Y-%m-%d")
                    today_date = datetime.datetime.today()
                    date_diff = (today_date - insDate).days
                    if date_diff <= 30:
                        compDict["is_updated"] = 1
                except Exception:
                    pass

            available_ver = str(row[17])
            if (status == "Available") and (available_ver > ""):
                current_version = version
                version = util.getoutput(available_ver)
                if current_version == version:
                    current_version = ""

            pre_reqs = str(row[18])
            if "EL9" in pre_reqs:
                el_v = util.get_el_os()
                if el_v == "EL9":
                    pass
                else:
                    continue

            compDict["category"] = category
            compDict["category_desc"] = category_desc
            compDict["short_cat_desc"] = short_cat_desc
            compDict["component"] = comp
            compDict["version"] = version
            compDict["is_extension"] = is_extension
            compDict["disp_name"] = disp_name
            compDict["release_desc"] = release_desc
            compDict["port"] = port
            compDict["release_date"] = release_date
            compDict["install_date"] = install_date
            compDict["curr_release_date"] = curr_rel_date
            compDict["status"] = status
            compDict["stage"] = stage
            compDict["updates"] = updates
            compDict["is_current"] = is_current
            compDict["current_version"] = current_version
            compDict["parent"] = parent
            compDict["pre_reqs"] = pre_reqs
            jsonList.append(compDict)

        if not jsonList:
            util.exit_message(
                f"No installable components available on '{util.get_el_ver()}'"
            )

        if p_return:
            return jsonList

        if p_isJSON:
            print(json.dumps(jsonList, sort_keys=True, indent=2))
        else:
            if len(jsonList) >= 1:
                print(api.format_data_to_table(jsonList, keys, headers))

    except Exception as e:
        fatal_error(e, sql, "meta.get_list()")
    sys.exit(0)


# Check if component required for platform #########
def is_dependent_platform(p_comp):
    try:
        c = con.cursor()
        sql = "SELECT platform FROM versions WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return False
    except Exception as e:
        fatal_error(e, sql, "meta.is_dependent_platform()")
    platform = str(data[0])
    if len(platform.strip()) == 0 or util.has_platform(platform) >= 0:
        return True
    return False


# get component version ############################
def get_version(p_comp):
    try:
        c = con.cursor()
        sql = "SELECT version FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return ""
    except Exception as e:
        fatal_error(e, sql, "meta.get_version()")
    return str(data[0])


# Get Current Version ###################################################
def get_current_version(p_comp):
    try:
        c = con.cursor()
        sql = "SELECT version FROM versions WHERE component = ? AND is_current >= 1"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            sql = "SELECT version, release_date FROM versions WHERE component = ? ORDER BY 2 DESC"
            c.execute(sql, [p_comp])
            data = c.fetchone()
            if data is None:
                return ""
    except Exception as e:
        fatal_error(e, sql, "meta.get_current_version()")
    return str(data[0])


def get_dependent_components(p_comp):
    data = []
    sql = (
        "SELECT c.component FROM projects p, components c \n"
        + " WHERE p.project = c.project AND p.depends = \n"
        + "   (SELECT project FROM releases \n"
        + "     WHERE component = '"
        + p_comp
        + "')"
    )
    try:
        c = con.cursor()
        c.execute(sql)
        data = c.fetchall()
    except Exception as e:
        fatal_error(e, sql, "meta.get_dependent_components()")
    return data


def get_component_list():
    try:
        c = con.cursor()
        sql = "SELECT component FROM components"
        c.execute(sql)
        t_comp = c.fetchall()
        r_comp = []
        for comp in t_comp:
            r_comp.append(str(comp[0]))
    except Exception as e:
        fatal_error(e, sql, "meta.get_component_list()")
    return r_comp


def get_installed_extensions_list(parent_c):
    try:
        c = con.cursor()
        sql = (
            "SELECT c.component FROM versions v ,components c "
            + "WHERE v.component = c.component AND v.parent='"
            + parent_c
            + "'"
        )
        c.execute(sql)
        t_comp = c.fetchall()
        r_comp = []
        for comp in t_comp:
            r_comp.append(str(comp[0]))
    except Exception as e:
        fatal_error(e, sql, "meta.get_installed_extensions_list()")
    return r_comp


def fatal_error(err, sql, func):
    print("################################################")
    print("# FATAL Error in " + func)
    print("#    Message =  " + err.args[0])
    print("#  Statement = " + sql)
    print("################################################")
    sys.exit(1)


# MAINLINE ################################################################
con = sqlite3.connect(os.getenv("MY_LITE"), check_same_thread=False)
