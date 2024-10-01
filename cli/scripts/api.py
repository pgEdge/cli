
#  Copyright 2022-2024 PGEDGE  All rights reserved. #


import json, os, platform, subprocess, sys, time
from datetime import datetime, timedelta
from operator import itemgetter

isPy3 = True

try:
    from colorama import init

    init()
except Exception:
    pass

scripts_lib_path = os.path.join(os.path.dirname(__file__), "lib")
this_platform_system = str(platform.system())
platform_lib_path = os.path.join(scripts_lib_path, this_platform_system)
if os.path.exists(platform_lib_path):
    if platform_lib_path not in sys.path:
        sys.path.append(platform_lib_path)

import util, meta


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BACKGROUND = "\033[42m"
    ITALIC = "\033[3m"


bold_start = bcolors.BOLD
bold_end = bcolors.ENDC
italic_start = bcolors.ITALIC
italic_end = bcolors.ENDC
table_header_style = bcolors.BOLD + bcolors.BACKGROUND
error_start = bcolors.FAIL


def format_help(p_input):
    inp = str(p_input)
    inp_lst = inp.split()

    p_1st = None
    if inp_lst:
        p_1st = str(inp_lst[0])

    if p_1st in ("#", "##", "###"):
        skip_len = len(p_1st) + 1
        inp = inp[skip_len:]
        inp = inp.replace("`", "")
        inp = bold_start + str(inp.upper()) + bold_end

    elif inp == "```":
        return None

    else:
        inp = inp.replace(" # ", italic_start + " # ")
        inp = "  " + inp + " " + italic_end

    return inp


def cli_unicode(p_str, p_encoding, errors="ignore"):
    return str(p_str)


try:
    test_unicode = unicode("test")
except NameError:
    unicode = cli_unicode


def check_output_wmic(p_cmds):
    out1 = subprocess.check_output(p_cmds)
    try:
        out2 = str(out1, "utf-8")
    except Exception:
        out2 = str(out1)
    out3 = out2.strip().split("\n")[1]
    return out3


def top(display=True, isJson=False):
    import pypsutil

    current_timestamp = int(time.mktime(datetime.utcnow().timetuple()))
    jsonDict = {}
    procs = []

    for p in pypsutil.process_iter():
        print(f"{p.pid: <7}  {p.username(): <10}  {p.memory_percent():.2f}  {p.name()}")

    return

    # TODO:
        
    #    try:
    #        p = p(
    #            attrs=[
    #                "pid",
    #                "username",
    #                "cpu_percent",
    #                "memory_percent",
    #                "cpu_times",
    #                "name",
    #            ]
    #        )
    #    except (pypsutil.NoSuchProcess, IOError, OSError):
    #        pass
    #    else:
    #        procs.append(p)

    if not display:
        return

    processes = sorted(procs, key=lambda p: p["cpu_percent"], reverse=True)

    network_usage = pypsutil.net_io_counters()
    jsonDict["kb_sent"] = network_usage.bytes_sent / 1024
    jsonDict["kb_recv"] = network_usage.bytes_recv / 1024

    cpu = pypsutil.cpu_times_percent(percpu=False)
    iowait = ""
    if util.get_platform() == "Linux":
        jsonDict["iowait"] = str(cpu.iowait)
        iowait = "," + str(cpu.iowait).rjust(5) + "%wa"

    jsonDict["current_timestamp"] = current_timestamp
    jsonDict["cpu_user"] = str(cpu.user)
    jsonDict["cpu_system"] = str(cpu.system)
    jsonDict["cpu_idle"] = str(cpu.idle)
    if not isJson:
        print(
            "CPU(s):"
            + str(cpu.user).rjust(5)
            + "%us,"
            + str(cpu.system).rjust(5)
            + "%sy,"
            + str(cpu.idle).rjust(5)
            + "%id"
            + iowait
        )

    disk = pypsutil.disk_io_counters(perdisk=False)
    read_kb = disk.read_bytes / 1024
    write_kb = disk.write_bytes / 1024
    jsonDict["kb_read"] = str(read_kb)
    jsonDict["kb_write"] = str(write_kb)
    if not isJson:
        print("DISK: kB_read " + str(read_kb) + ", kB_written " + str(write_kb))

    uptime = datetime.now() - datetime.fromtimestamp(pypsutil.boot_time())
    str_uptime = str(uptime).split(".")[0]
    line = ""
    uname_len = 8
    av1, av2, av3 = os.getloadavg()
    str_loadavg = "%.2f %.2f %.2f  " % (av1, av2, av3)
    line = bold_start + "Load average: " + bold_end + str_loadavg
    jsonDict["load_avg"] = str(str_loadavg)
    line = line + bold_start + "Uptime:" + bold_end + " " + str_uptime
    jsonDict["uptime"] = str(str_uptime)
    if not isJson:
        print(line)

    i = 0
    my_pid = os.getpid()
    if not isJson:
        print("")
        print(
            bold_start
            + "    PID "
            + "USER".ljust(uname_len)
            + "   %CPU %MEM      TIME+ COMMAND"
            + bold_end
        )

    jsonList = []
    for pp in processes:
        if pp["pid"] == my_pid:
            continue
        i += 1
        if i > 10:
            break

        # TIME+ column shows process CPU cumulative time and it
        # is expressed as: "mm:ss.ms"

        ctime = timedelta(seconds=sum(pp["cpu_times"]))
        ctime_mm = str(ctime.seconds // 60 % 60)
        ctime_ss = str(int(ctime.seconds % 60)).zfill(2)
        ctime_ms = str(ctime.microseconds)[:2].ljust(2, str(0))
        ctime = "{0}:{1}.{2}".format(ctime_mm, ctime_ss, ctime_ms)

        username = pp["username"][:uname_len]
        if isJson:
            pp["username"] = username
            pp["ctime"] = ctime
            pp["cpu_percent"] = float(pp["cpu_percent"])
            pp["memory_percent"] = float(round(pp["memory_percent"], 1))
            jsonList.append(pp)
        else:
            print(
                str(pp["pid"]).rjust(7)
                + " "
                + username.ljust(uname_len)
                + " "
                + str(pp["cpu_percent"]).rjust(6)
                + " "
                + str(round(pp["memory_percent"], 1)).rjust(4)
                + " "
                + str(ctime).rjust(10)
                + " "
                + pp["name"]
            )
    if isJson:
        jsonDict["top"] = jsonList
        print(json.dumps([jsonDict]))
    else:
        print("")


def list(p_json, p_cat, p_comp, p_ver, p_port, p_status, p_kount):
    lst = " "
    if p_kount > 1:
        lst = ","
    if p_json:
        lst = (
            lst
            + '{"category": "'
            + p_cat.rstrip()
            + '",'
            + ' "component": "'
            + p_comp.rstrip()
            + '",'
            + ' "version": "'
            + p_ver.rstrip()
            + '",'
            + ' "port": "'
            + p_port.rstrip()
            + '",'
            + ' "status": "'
            + p_status.rstrip()
            + '"}'
        )
        print(lst)
        return

    print(p_comp + "  " + p_ver + "  " + p_port + "  " + p_status)


def status(p_json, p_comp, p_ver, p_state, p_port, p_kount):
    status = " "
    if p_kount > 1:
        status = ","
    if p_json:
        jsonStatus = {}
        jsonStatus["component"] = p_comp
        jsonStatus["version"] = p_ver
        jsonStatus["state"] = p_state
        if p_port != "" and int(p_port) > 1:
            jsonStatus["port"] = p_port
        category = util.get_comp_category(p_comp)
        if category:
            jsonStatus["category"] = category
        elif p_comp.startswith == "pgdg":
            jsonStatus["category"] = 1
        print(status + json.dumps(jsonStatus))
        return

    app_ver = p_comp + "-" + p_ver
    app_ver = app_ver + (" " * (35 - len(app_ver)))

    if p_state in ("Running", "Stopped") and int(p_port) > 1:
        on_port = " on port " + p_port
    else:
        on_port = ""

    # print(app_ver + "(" + p_state + on_port + ")")
    print(p_comp + " " + p_state.lower() + on_port)


def info(p_json, p_home, p_repo, print_flag=True):
    (
        cloud_name,
        cloud_platform,
        instance_id,
        flavor,
        region,
        az,
        private_ip,
    ) = util.get_cloud_info()

    p_user = util.get_user()
    p_is_admin = util.is_admin()
    arch = platform.machine()

    this_os = ""
    this_uname = str(platform.system())[0:7]
    if private_ip > "":
        host_ip = private_ip
    else:
        host_ip = util.get_host_ip()
    wmic_path = (
        os.getenv("SYSTEMROOT", "")
        + os.sep
        + "System32"
        + os.sep
        + "wbem"
        + os.sep
        + "wmic"
    )
    host_display = util.get_host_short()

    # Check the OS & Resources ########################################
    plat = util.get_os()
    glibcV = util.glibc_ver()

    os_major_ver = ""

    system_cpu_cores, cpu_model = util.get_cpu_info()

    if this_uname == "Darwin":
        mem_mb = util.get_mem_mb()
        system_memory_in_kbytes = mem_mb * 1024
        system_memory_in_gb = mem_mb / 1024.0
        prod_name = util.getoutput("sw_vers -productName")
        prod_version = util.getoutput("sw_vers -productVersion")
        this_os = prod_name + " " + prod_version
    elif this_uname == "Linux":
        mem_mb = util.get_mem_mb()
        system_memory_in_kbytes = mem_mb * 1024
        system_memory_in_gb = mem_mb / 1024.0
        os_major_ver = util.getoutput(
            "cat /etc/os-release | grep VERSION_ID | cut -d= -f2 | tr -d '\"'"
        )
        if os.path.exists("/etc/redhat-release"):
            this_os = util.getoutput("cat /etc/redhat-release")
        elif os.path.exists("/etc/system-release"):
            this_os = util.getoutput("cat /etc/system-release")
        elif os.path.exists("/etc/lsb-release"):
            this_os = util.getoutput(
                "cat /etc/lsb-release | grep DISTRIB_DESCRIPTION | cut -d= -f2 | tr -d '\"'"
            )
        elif os.path.exists("/etc/os-release"):
            this_os = util.getoutput(
                "cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'"
            )

    cpu_model = cpu_model.replace("Intel(R) Core(TM)", "Intel Core")
    ctlib_ver = os.getenv("MY_CTLIB_VER", "")


    if system_memory_in_gb > 0.6:
        round_mem = round(system_memory_in_gb)
    else:
        round_mem = round(system_memory_in_gb, 1)

    mem = str(round_mem) + " GB"

    cores = str(system_cpu_cores)

    os2 = this_os.replace(" release ", "")
    os2 = os2.replace(" (Final)", "")
    os2 = os2.replace(" (Core)", "")

    gpu_info = util.get_gpu_info()

    ver = util.get_version()
    [last_update_utc, last_update_local, unique_id] = util.read_hosts("localhost")
    if last_update_local:
        last_upd_dt = datetime.strptime(last_update_local, "%Y-%m-%d %H:%M:%S")
        time_diff = int(util.timedelta_total_seconds(datetime.now() - last_upd_dt))
        last_update_readable = util.get_readable_time_diff(str(time_diff), precision=2)

    os_pkg_mgr = util.get_pkg_mgr()

    client_id = util.get_value("PGEDGE", "CLIENT_ID")
    cluster_id = util.get_value("PGEDGE", "CLUSTER_ID")
    node_id = util.get_value("PGEDGE", "NODE_ID")

    if p_json:
        infoJsonArray = []
        infoJson = {}
        infoJson["version"] = ver
        infoJson["home"] = p_home
        infoJson["user"] = p_user
        infoJson["host"] = host_display
        infoJson["host_short"] = util.get_host_short()
        infoJson["host_long"] = util.get_host()
        infoJson["host_ip"] = host_ip
        infoJson["os"] = unicode(
            str(os2), sys.getdefaultencoding(), errors="ignore"
        ).strip()
        infoJson["os_pkg_mgr"] = os_pkg_mgr
        infoJson["os_major_ver"] = os_major_ver
        infoJson["os_memory_mb"] = round_mem
        infoJson["cores"] = system_cpu_cores
        infoJson["arch"] = arch
        infoJson["last_update_utc"] = last_update_utc
        if last_update_local:
            infoJson["last_update_readable"] = last_update_readable
        infoJson["repo"] = p_repo
        infoJson["system_memory_in_kb"] = system_memory_in_kbytes
        infoJson["python3_ver"] = util.python3_ver()
        infoJson["glibc_ver"] = glibcV

        infoJson["pgedge_client_id"] = client_id
        infoJson["pgedge_cluster_id"] = cluster_id
        infoJson["pgedge_node_id"] = node_id
        infoJson["ctlib_ver"] = ctlib_ver

        infoJson["cloud_region"] = region
        infoJson["cloud_az"] = az
        infoJson["cloud_instance_id"] = instance_id
        infoJson["cloud_flavor"] = flavor
        infoJson["cloud_private_ip"] = private_ip
        infoJsonArray.append(infoJson)
        if print_flag:
            print(json.dumps(infoJsonArray, sort_keys=True, indent=2))
            return
        else:
            return infoJson

    INFO_WIDTH = 80

    if p_is_admin:
        admin_display = " (Admin)"
    else:
        admin_display = ""

    if glibcV <= " ":
        glibc_v_display = ""
    else:
        glibc_v_display = f", glibc-{glibcV},"


    if util.MY_CODENAME > " ":
       ver_display = f"pgEdge {util.format_ver(ver)} ({util.MY_CODENAME})"
    else:
       ver_display = f"pgEdge {util.format_ver(ver)}"
   
    print("#" * INFO_WIDTH)
    print(f"#{bold_start}     Version:{bold_end} {ver_display}")

    print(f"#{bold_start} User & Host:{bold_end} " +
              f"{p_user}{admin_display}  {host_display}  {p_home}")

    if ctlib_ver == "":
        ctlib_ver == "?"
    py3_display = f"Python {util.python3_ver()} ({ctlib_ver})"
    print(f"#{bold_start}          OS:{bold_end} {os2}{glibc_v_display} {py3_display}")

    cores_model = ""
    if cores != "0":
        cores_model = f", vCPU {cores}, {cpu_model}"

    print(f"#{bold_start}     Machine:{bold_end} {mem}{cores_model}")

    if os.path.exists(f"{util.getreqenv('MY_HOME')}/m2m"):
        print(f"#{bold_start}      M2M ID:{bold_end} {client_id}/{cluster_id}/{node_id}")
      
    if gpu_info > "":
        print(f"#{bold_start}    GPU Info:{bold_end} {gpu_info}")

    if instance_id > "" and not cloud_name == "unknown":
        print(f"#{bold_start}  Cloud Info:{bold_end} " +
              f"{cloud_name}  {cloud_platform}  {instance_id}  {flavor}  {az}"
        )

    print(f"#{bold_start}    Repo URL:{bold_end} {p_repo}")

    if not last_update_local:
        last_update_local = "None"

    print(f"#{bold_start} Last Update:{bold_end} {last_update_local}")
    print("#" * INFO_WIDTH)


def info_component(p_comp_dict, p_kount):
    if p_kount > 1:
        print(bold_start + ("-" * 90) + bold_end)

    print(
        bold_start
        + "     Project: "
        + bold_end
        + p_comp_dict["project"]
        + " ("
        + p_comp_dict["project_url"]
        + ")"
    )

    print(
        bold_start
        + "   Component: "
        + bold_end
        + p_comp_dict["component"]
        + " "
        + p_comp_dict["version"]
        + " ("
        + p_comp_dict["proj_description"]
        + ")"
    )

    if p_comp_dict["port"] > 1:
        print(bold_start + "        port: " + bold_end + str(p_comp_dict["port"]))

    if p_comp_dict["datadir"] > "":
        print(bold_start + "     datadir: " + bold_end + p_comp_dict["datadir"])

    if p_comp_dict["logdir"] > "":
        print(bold_start + "      logdir: " + bold_end + p_comp_dict["logdir"])

    if p_comp_dict["autostart"] == "on":
        print(bold_start + "   autostart: " + bold_end + p_comp_dict["autostart"])

    if p_comp_dict["svcuser"] > "" and util.get_platform() == "Linux":
        print(bold_start + "     svcuser: " + bold_end + p_comp_dict["svcuser"])

    if ("status" in p_comp_dict) and ("up_time" in p_comp_dict):
        print(
            bold_start
            + "      status: "
            + bold_end
            + p_comp_dict["status"]
            + bold_start
            + " for "
            + bold_end
            + p_comp_dict["up_time"]
        )
    else:
        if "status" in p_comp_dict:
            print(bold_start + "      status: " + bold_end + p_comp_dict["status"])
        if "up_time" in p_comp_dict:
            print(bold_start + "    up since: " + bold_end + p_comp_dict["up_time"])

    if "data_size" in p_comp_dict:
        print(bold_start + "   data size: " + bold_end + p_comp_dict["data_size"])

    if "connections" in p_comp_dict:
        print(bold_start + " connections: " + bold_end + p_comp_dict["connections"])

    print(
        bold_start
        + "Release Date: "
        + bold_end
        + p_comp_dict["release_date"]
        + bold_start
        + "  Stage: "
        + bold_end
        + p_comp_dict["stage"]
    )

    if p_comp_dict["platform"] > "":
        print(
            bold_start
            + "Supported On: "
            + bold_end
            + "["
            + p_comp_dict["platform"]
            + "]"
        )

    if p_comp_dict["pre_reqs"] > "":
        print(bold_start + "   Pre Req's: " + bold_end + p_comp_dict["pre_reqs"])

    print(bold_start + "     License: " + bold_end + p_comp_dict["license"])

    is_installed = str(p_comp_dict["is_installed"])
    if str(is_installed) == "0":
        is_installed = "NO"

    print(
        bold_start
        + "   IsCurrent: "
        + bold_end
        + str(p_comp_dict["is_current"])
        + bold_start
        + "  IsInstalled: "
        + bold_end
        + is_installed
    )


def format_data_to_table(
    data,
    keys,
    header=None,
    error_key=None,
    error_msg_column=None,
    sort_by_key=None,
    sort_order_reverse=False,
):
    """Takes a list of dictionaries, formats the data, and returns
    the formatted data as a text table.

    Required Parameters:
        data - Data to process (list of dictionaries). (Type: List)
        keys - List of keys in the dictionary. (Type: List)

    Optional Parameters:
        header - The table header. (Type: List)
        sort_by_key - The key to sort by. (Type: String)
        sort_order_reverse - Default sort order is ascending, if
            True sort order will change to descending. (Type: Boolean)
    """
    # Sort the data if a sort key is specified (default sort order
    # is ascending)
    if sort_by_key:
        data = sorted(data, key=itemgetter(sort_by_key), reverse=sort_order_reverse)

    # If header is not empty, add header to data
    if header:
        # Get the length of each header and create a divider based
        # on that length
        header_divider = []
        for name in header:
            header_divider.append("-" * len(name))

        # Create a list of dictionary from the keys and the header and
        # insert it at the beginning of the list. Do the same for the
        # divider and insert below the header.
        # header_divider = dict(zip(keys, header_divider))
        # data.insert(0, header_divider)
        header = dict(zip(keys, header))
        data.insert(0, header)

    column_widths = []
    for key in keys:
        column_widths.append(max(len(str(column[key])) for column in data) + 2)

    # Create a tuple pair of key and the associated column width for it
    key_width_pair = zip(keys, column_widths)
    key_length = len(keys)

    str_format = ("%-*s " * len(keys)).strip() + "\n"
    formatted_data = ""

    for element in data:
        data_to_format = []
        s = 0
        key_width_pair = zip(keys, column_widths)
        # Create a tuple that will be used for the formatting in
        # width, value format
        for pair in key_width_pair:
            dataStr = str(element[pair[0]])
            spaces = " " * ((int(float(pair[1])) - len(dataStr)) - 2)
            if s < key_length - 1:
                spaces = spaces + " |"

            if dataStr in header.values():
                if s == 0:
                    dataStr = table_header_style + dataStr
                dataStr = dataStr + spaces
                if s == key_length - 1:
                    dataStr = dataStr + bold_end
                s = s + 1
            elif error_key and error_msg_column:
                if (
                    pair[0] in error_msg_column
                    and element.get(error_key[0]) == error_key[1]
                ):
                    dataStr = error_start + dataStr + bold_end

            data_to_format.append(pair[1])
            data_to_format.append(dataStr)
        formatted_data += str_format % tuple(data_to_format)
    return formatted_data
