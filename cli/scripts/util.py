#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os

MY_VERSION = "24.4.1"
DEFAULT_PG = "16"
DEFAULT_SPOCK = "33"
MY_CMD = os.getenv("MY_CMD", None)
MY_HOME = os.getenv("MY_HOME", None)
MY_LITE = os.getenv("MY_LITE", None)

import sys
import socket
import sqlite3
import signal
import hashlib
import random
import json
import tarfile
import uuid
import logging
import logging.handlers
import tempfile
import shutil
import traceback
import time
import platform
import subprocess
import getpass
import filecmp

from subprocess import Popen, PIPE, STDOUT
from datetime import datetime, timedelta
from urllib import request as urllib2

try:
    import psycopg
except Exception:
    # Psycopg is only used for advanced functionality
    #  and may throw errors in some cases
    pass

from log_helpers import bcolours, characters
import api, meta, ini


isJSON = False
if os.environ.get("isJson", "False") == "True":
    isJSON = True

pid_file = os.path.join(MY_HOME, "conf", "cli.pid")

isTEST = False
if os.environ.get("isTest", "False") == "True":
    isTEST = True
isENT = False
if os.environ.get("isEnt", "False") == "True":
    isENT = True
isSHOWDUPS = False
isEXTENSIONS = False

ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7

scripts_lib_path = os.path.join(os.path.dirname(__file__), "lib")
if scripts_lib_path not in sys.path:
    sys.path.append(scripts_lib_path)

this_platform_system = str(platform.system())
platform_lib_path = os.path.join(scripts_lib_path, this_platform_system)
if os.path.exists(platform_lib_path):
    if platform_lib_path not in sys.path:
        sys.path.append(platform_lib_path)

################ Logging Configuration ############
# Custom Logging
COMMAND = 15
DEBUG = 10
DEBUG2 = 9


def get_parsed_json(file_nm):
    parsed_json = None
    try:
        with open(file_nm, "r") as f:
            parsed_json = json.load(f)
    except Exception as e:
        util.exit_message(f"Unable to load json file: {file_nm}\n{e}")

    return(parsed_json)


# Custom loglevel functions
def debug2(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG2):
        self._log(DEBUG2, message, args, **kws)


def command(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(COMMAND):
        self._log(COMMAND, message, args, **kws)

my_logger = logging.getLogger()
LOG_FILENAME = os.getenv('MY_LOGS')
if not LOG_FILENAME:
   MY_HOME = os.getenv("MY_HOME")
   LOG_FILENAME = os.path.join(MY_HOME,"logs","cli_log.out")
LOG_DIRECTORY = os.path.split(LOG_FILENAME)[0]

isDebug=0
pgeDebug = int(os.getenv('pgeDebug', '0'))
if pgeDebug == 1:
    LOG_LEVEL = DEBUG
    isDebug = 1
elif pgeDebug == 2:
    LOG_LEVEL = DEBUG2
    isDebug = 2
else:
    LOG_LEVEL = COMMAND
    isDebug = 0

if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)

logging.addLevelName(COMMAND, "COMMAND")
logging.Logger.command = command

logging.addLevelName(DEBUG2, "DEBUG2")
logging.Logger.debug2 = debug2

my_logger.setLevel(LOG_LEVEL)
handler = logging.handlers.RotatingFileHandler(
                  LOG_FILENAME, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
my_logger.addHandler(handler)

def trim_plat(ver):
    if not ver:
        return None
    v1 = ver.replace("-el9", "")
    v2 = v1.replace("-arm9", "")
    v3 = v2.replace("-el8", "")
    return v3


def num_pg_minors(pg_minor, is_display=False):
    ## print(f"util.num_pg_minors({pg_minor})")
    try:
        c = cL.cursor()
        sql = (
            f"SELECT component, version, release_date, is_current FROM versions\n "
            + f" WHERE component LIKE 'pg%' AND version LIKE '{pg_minor}%'\n"
            + f"   AND platform LIKE '%{get_el_ver()}%'"
        )
    
        c.execute(sql)
        data = c.fetchall()
        c.close()

        kount = 0
        for d in data:
          kount = kount + 1
          if is_display:
             if kount == 1:
                message(f"    Component    Version  Released  IsCurrent")
             message(f"    {str(d[0]).ljust(12)} {str(d[1]).ljust(8)} {d[2]}  {d[3]}")
    except Exception as e:
        fatal_sql_error(e, sql, "num_pg_minors()")

    return(kount)


def num_spocks(pg, ver, is_display=False):
    try:
        c = cL.cursor()
        sql = (
            f"SELECT component, version, release_date, is_current FROM versions\n "
            + f" WHERE component LIKE 'spock%{pg}' AND version LIKE '{ver}%'\n"
            + f"   AND platform LIKE '%{get_el_ver()}%'"
        )
      
        c.execute(sql)
        data = c.fetchall()
        c.close()

        kount = 0
        for d in data:
          kount = kount + 1
          if is_display:
             if kount == 1:
                message(f"    Component    Version  Released  IsCurrent")
             message(f"    {str(d[0]).ljust(12)} {str(d[1]).ljust(8)} {d[2]}  {d[3]}")
    except Exception as e:
        fatal_sql_error(e, sql, "num_spocks()")

    return(kount)


def copytree(cmd):
    os.system(f"cp -r {cmd}")


def load_ini(file_nm, section):
    try:
        text = open(file_nm, "r").read()
        config = ini.parse(text)
        for s in config:
            if s == section:
                return config[s]
    except Exception as e:
        exit_message(str(e), 1)

    return None


def run_psyco_sql(pg_v, db, cmd, usr=None):
    if usr is None:
        usr = get_user()

    if is_verbose():
        message(cmd, "info")

    if debug_lvl() > 0:
        message(cmd, "debug")

    con = get_pg_connection(pg_v, db, usr)
    if debug_lvl() > 0:
        message("run_psyco_sql(): " + str(con), "debug")

    try:
        cur = con.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute(cmd)
        con.commit()

        print(json_dumps(cur.fetchall()))

        try:
            cur.close()
            con.close()
        except Exception:
            pass

    except Exception as e:
        if "already exists" in str(e):
            exit_message("already exists", 0)
        elif "already subscribes" in str(e):
            exit_message("already subscribes", 0)
        else:
            exit_exception(e)


def get_pg_connection(pg_v, db, usr):
    dbp = get_column("port", pg_v)

    if debug_lvl() > 0:
        message(f"get_pg_connection(): dbname={db}, user={usr}, port={dbp}", "debug")

    try:
        con = psycopg.connect(
            dbname=db, user=usr, host="127.0.0.1", port=dbp, autocommit=False
        )
    except Exception as e:
        exit_exception(e)

    return con


def get_table_list(table, db, pg_v):
    w_schema = None
    w_table = None

    l_tbl = table.split(".")
    if len(l_tbl) > 2:
        exit_message("Invalid table wildcard", 1)

    if len(l_tbl) == 2:
        w_schema = str(l_tbl[0])
        w_table = str(l_tbl[1])
    elif len(l_tbl) == 1:
        w_table = str(l_tbl[0])

    sql = (
        "SELECT table_schema || '.' || table_name as schema_table \n"
        + "  FROM information_schema.tables\n"
        + " WHERE TABLE_TYPE = 'BASE TABLE' \n"
        + " AND table_schema NOT IN ('spock','pg_catalog','information_schema')"
    )

    if w_schema:
        sql = sql + "\n   AND table_schema = '" + w_schema + "'"

    sql = sql + "\n   AND table_name LIKE '" + w_table.replace("*", "%") + "'"

    con = get_pg_connection(pg_v, db, get_user())

    try:
        cur = con.cursor()
        cur.execute(sql)

        ret = cur.fetchall()

        try:
            cur.close()
            con.close()
        except Exception:
            pass

    except Exception as e:
        exit_exception(e)

    if len(ret) > 0:
        return ret

    exit_message(f"Could not find table that matches {table}", 1)


def get_seq_list(seq, db, pg_v):
    w_schema = None
    w_seq = None

    l_seq = seq.split(".")
    if len(l_seq) > 2:
        exit_message("Invalid sequnce wildcard", 1)

    if len(l_seq) == 2:
        w_schema = str(l_seq[0])
        w_seq = str(l_seq[1])
    elif len(l_seq) == 1:
        w_seq = str(l_seq[0])

    sql = (
        "SELECT sequence_schema || '.' || sequence_name as schema_seq \n"
        + "  FROM information_schema.sequences \n"
        + " WHERE sequence_schema NOT IN ('spock','pg_catalog','information_schema','snowflake')"
    )

    if w_schema:
        sql = sql + "\n   AND sequence_schema = '" + w_schema + "'"

    sql = sql + "\n   AND sequence_name LIKE '" + w_seq.replace("*", "%") + "'"

    con = get_pg_connection(pg_v, db, get_user())

    try:
        cur = con.cursor()
        cur.execute(sql)

        ret = cur.fetchall()

        try:
            cur.close()
            con.close()
        except Exception:
            pass

    except Exception as e:
        exit_exception(e)

    if len(ret) > 0:
        return ret

    exit_message(f"Could not find sequence that matches {seq}", 1)


def json_dumps(p_input):
    if os.getenv("isJson", "") == "True":
        return json.dumps(p_input)

    return json.dumps(p_input, indent=2)


def get_pg_v(pg):
    pg_v = str(pg)

    if pg_v.isdigit():
        pg_v = "pg" + str(pg_v)

    if pg_v == "None":
        k = 0
        pg_s = meta.get_installed_pg()

        for p in pg_s:
            k = k + 1

        if k == 1:
            pg_v = str(p[0])
        elif k == 0:
            exit_message("PG is not installed", 1)
        else:
            exit_message("must be one PG installed", 1)

    if not os.path.isdir(pg_v):
        exit_message(str(pg_v) + " not installed", 1)

    return pg_v


def get_cloud_info():
    try:
        ciq = subprocess.run(
            ["cloud-init", "query", "--all"], check=True, capture_output=True, text=True
        ).stdout
        ciq_j = json.loads(ciq)

    except Exception:
        return ("", "", "", "", "", "", "")

    try:
        cloud_name = ciq_j["v1"]["cloud-name"]
    except Exception:
        cloud_name = ""

    try:
        platform = ciq_j["v1"]["platform"]
    except Exception:
        platform = ""

    try:
        region = ciq_j["v1"]["region"]
    except Exception:
        region = ""

    try:
        availability_zone = ciq_j["v1"]["availability-zone"]
    except Exception:
        availability_zone = ""

    try:
        instance_id = ciq_j["v1"]["instance-id"]
    except Exception:
        instance_id = ""

    try:
        instance_type = ciq_j["ds"]["meta-data"]["instance-type"]
    except Exception:
        instance_type = ""

    try:
        local_ipv4 = ciq_j["ds"]["meta-data"]["local-ipv4"]
    except Exception:
        local_ipv4 = ""

    return (
        cloud_name,
        platform,
        instance_id,
        instance_type,
        region,
        availability_zone,
        local_ipv4,
    )


def check_node_exists(cluster_name, node_name, base_dir="cluster"):
    node_dir = base_dir + "/" + str(cluster_name) + "/" + str(node_name)

    if not os.path.exists(node_dir):
        exit_message("node not found: " + node_dir, 1)


def check_cluster_exists(cluster_name, base_dir="cluster"):
    cluster_dir = base_dir + "/" + str(cluster_name)

    if not os.path.exists(cluster_dir):
        exit_message("cluster not found: " + cluster_dir, 1)


def is_verbose():
    isVerbose = os.getenv("isVerbose", "False")
    if isVerbose == "True":
        return True
    else:
        return False


def debug_lvl():
    lvl = str(os.getenv("pgeDebug", "0"))
    if lvl.isnumeric():
        return int(lvl)
    else:
        return 0


def echo_cmd(cmd, echo=True, sleep_secs=0, host="", usr="", key=""):
    if host > "":
        ssh_cmd = "ssh -o StrictHostKeyChecking=no -q -t "
        if usr > "":
            ssh_cmd = ssh_cmd + str(usr) + "@"

        ssh_cmd = ssh_cmd + str(host) + " "

        if key > "":
            ssh_cmd = ssh_cmd + "-i " + str(key) + " "

        cmd = cmd.replace('"', '\\"')
        cmd = ssh_cmd + ' "' + str(cmd) + '"'

    isSilent = os.getenv("isSilent", "False")
    if isSilent == "False":
        s_cmd = scrub_passwd(cmd)
        if echo:
            message("#  " + str(s_cmd))

    rc = os.system(str(cmd))
    if rc == 0:
        if int(sleep_secs) > 0:
            os.system("sleep " + str(sleep_secs))
        return 0

    return 1


def psql_cmd(cmd, nc, db, pg, host, usr, key):
    echo_cmd(nc + ' psql "' + cmd + '" ' + db, host=host, usr=usr, key=key)


def print_exception(e, msg_type="error"):
    lines = str(e).splitlines()
    for line in lines:
        if line.startswith("HINT:"):
            pass
        else:
            message(line, msg_type)


def exit_exception(e):
    print_exception(e)
    sys.exit(1)


def is_empty_writable_dir(p_dir):
    if not os.path.isdir(p_dir):
        # directory does not exist
        return 1

    if os.listdir(p_dir):
        # directory is not empty
        return 2

    test_file = p_dir + "/test_file.txt"
    try:
        with open(test_file, "w") as file:
            file.write("hello!")
            file.close()
    except Exception:
        # directory is not writeable
        return 3
    os.system("rm -f " + test_file)

    # directory is empty & writeable
    return 0


def get_python_minor_version():
    return sys.version_info.minor


def remove_prefix(p_prefix, p_str):
    if p_str.find(p_prefix) == 0:
        pref_len = len(p_prefix)
        return p_str[pref_len:]

    return p_str


def remove_suffix(p_suffix, p_str):
    suf_len = len(p_suffix)
    suf_start = len(p_str) - suf_len
    if p_str[suf_start:] == p_suffix:
        return p_str[:suf_start]

    return p_str


def shuffle_string(p_input):
    # deterministic shuffle of a string
    ll = list(p_input)
    random.Random(123).shuffle(ll)
    shuffled = "".join(ll)
    return shuffled


def scrub_passwd(p_cmd):
    ll = p_cmd.split()
    flag = False
    new_s = ""
    key_wd = ""

    for i in ll:
        if ((i == "PASSWORD") or (i == "-P")) and (flag is False):
            flag = True
            key_wd = str(i)
            continue

        if flag:
            new_s = new_s + " " + key_wd + " '???'"
            flag = False
        else:
            new_s = new_s + " " + i

    return new_s


def is_selinux_active():
    if get_platform() != "Linux":
        return False

    rc = os.system("getenforce > /dev/null 2>&1")
    if rc != 0:
        return False

    status = getoutput("getenforce")
    if status.lower() == "disabled":
        return False

    return True


def get_glibc_version():
    if get_platform() != "Linux":
        return ""

    # the 'ldd --version' command gives back the glibc version on the last word
    #   of the first line
    glibcV = getoutput("ldd --version | head -1 | grep -oE '[^ ]+$'")

    return glibcV


def get_random_password(p_length=12):
    import string
    import random

    passwd_chars = string.ascii_letters + string.digits + "~!@()_+-{}|"
    passwd = []
    for x in range(p_length):
        passwd.append(random.choice(passwd_chars))
    return "".join(passwd)


def get_1st_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


def run_native(component, bin_path, cmd):
    if not os.path.isfile(bin_path):
        message(f"{component} not installed, missing '{bin_path}'", "error")
        return

    return echo_cmd(bin_path + " " + cmd)


def sysdate():
    return datetime.utcnow()


def print_list(p_headers, p_keys, p_json_list):
    if os.getenv("isJson", None):
        print(json.dumps(p_json_list, sort_keys=True, indent=2))
    else:
        print(api.format_data_to_table(p_json_list, p_keys, p_headers))


def get_perl_ver():
    perl_ver = getoutput('perl -E "say $^V" 2>/dev/null')
    if len(perl_ver) == 0:
        return ""
    if perl_ver[0] == "v":
        perl_ver = perl_ver[1:]
    return perl_ver.strip()


def get_java_ver(pDisplay=False):
    java_ver = getoutput("java -version 2>&1")
    java_ver = java_ver.replace('"', "")
    java_lines = java_ver.split("\n")
    java_ver = java_lines[0]
    parts = java_ver.split(" ")
    if pDisplay:
        print(str(parts))

    if len(parts) >= 3:
        java_ver = parts[2]
        java_ver_pieces = java_ver.split(".")
        if str(java_ver_pieces[0]) == "1":
            java_major_ver = str(java_ver_pieces[1])
        else:
            java_major_ver = str(java_ver_pieces[0])
    else:
        java_major_ver = ""
        java_ver = ""

    return [java_major_ver, java_ver]


def is_systemctl():
    rc = os.system("sudo systemctl status > /dev/null 2>&1")
    if rc == 0:
        return True

    print("systemctl not present")
    return False


def remove_symlinks(p_link_dir, p_target_dir):
    # disabled because it dangerously didn't work
    return


def create_symlinks(p_link_dir, p_target_dir):
    cmd = "sudo ln -fst " + p_link_dir + " " + p_target_dir + "/*"
    message(cmd, "info")
    os.system(cmd)

    return


def cmd_system(p_sys_cmd, p_display=True):
    if p_sys_cmd.strip() == "":
        return 0

    cmd = MY_HOME + os.sep + "pgedge " + str(p_sys_cmd)

    if p_display:
        print("\n## " + str(cmd))

    rc = os.system(cmd)
    return rc


def run_cmd(p_cmd, p_display=False):
    cmd = MY_HOME + os.sep + p_cmd

    if p_display:
        print("  " + cmd)

    rc = os.system(sys.executable + " -u " + cmd)
    if rc == 0:
        return 0

    return 1


def run_sql_cmd(p_pg, p_sql, p_display=False):
    port = get_column("port", p_pg)
    cmd = "psql -p " + str(port) + ' -c "' + p_sql + '"'

    db = os.getenv("pgName", "")
    if db > "":
        cmd = cmd + "  " + str(db)
    else:
        cmd = cmd + " postgres"

    cmd = os.path.join(p_pg, "bin", cmd)

    if p_display:
        message("$ " + cmd, "info")

    cmd = os.path.join(MY_HOME, cmd)
    rc = os.system(cmd)
    return rc


def posix_unpack(file_nm):
    rc = os.system(f"tar -xf {file_nm}")
    return(rc)


def restart_postgres(p_pg):
    print("")
    run_cmd(p_pg + os.sep + "stop-" + p_pg + ".py", False)
    time.sleep(3)
    run_cmd(p_pg + os.sep + "start-" + p_pg + ".py", False)
    time.sleep(4)


def config_extension(p_pg, p_comp, create=True):

    extension_name, default_conf = meta.get_extension_meta(p_comp)

    for df in default_conf.split("|"):
        df1 = df.strip()
        df_l = df1.split("=")
        if len(df_l) != 2:
            message(f"skipping bad extension metadata \n  '{df_l}'")
        else:
            change_pgconf_keyval(p_pg, str(df_l[0]), str(df_l[1]), True)

    if create:
        create_extension(p_pg, extension_name, True)


def create_extension(p_pg, p_ext, p_reboot=False, p_extension="", p_cascade=False):
    isPreload = os.getenv("isPreload")

    if p_ext > " " and isPreload == "True":
        rc = change_pgconf_keyval(p_pg, "shared_preload_libraries", p_ext)

    isRestart = os.getenv("isRestart")
    if p_reboot and isRestart == "True":
        restart_postgres(p_pg)

    print("")
    if p_extension == "":
        p_extension = p_ext

    if p_extension == "none" or isRestart == "False":
        pass
    else:
        create_ext_cmd(p_extension, p_cascade, p_pg)

    return True


def create_ext_cmd(p_extension, p_cascade, p_pg):
    cmd = "CREATE EXTENSION IF NOT EXISTS " + p_extension
    if p_cascade:
        cmd = cmd + " CASCADE"
    run_sql_cmd(p_pg, cmd, True)


def secure_win_dir(p_dir, p_is_exe, p_user):
    CLI = os.path.join(MY_HOME, "hub", "scripts")
    cmnd = os.path.join(CLI, "PsExec.exe -accepteula -nobanner -s /c ")
    cmnd = cmnd + os.path.join(CLI, "secure-win-dir.bat") + ' "' + p_dir + '" '
    cmnd = cmnd + '"' + p_is_exe + '" "' + p_user + '" >> '
    cmnd = cmnd + os.path.join(MY_HOME, "logs", "fix-security.log") + " 2>&1"
    system(cmnd, is_display=True)


def source_env_file(p_env_file):
    try:
        command = ["bash", "-c", "source " + p_env_file + " && env"]
        proc = Popen(command, stdout=PIPE)
        for line in proc.stdout:
            (key, _, value) = line.partition("=")
            os.environ[key] = value.strip()
        proc.communicate()

    except Exception as e:
        exit_message(str(e), 1, False)

    return


def encrypt(plaintext, key):
    """
    Encrypt the plaintext with AES method.

    Parameters:
        plaintext -- String to be encrypted.
        key       -- Key for encryption.
    """
    try:
        import base64

        from Crypto import Random
        from Crypto.Cipher import AES
    except ImportError as e:
        exit_message(str(e), 1, False)

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(pad(key), AES.MODE_CFB, iv)
    # If user has entered non ascii password (Python2)
    # we have to encode it first
    if hasattr(str, "decode"):
        plaintext = plaintext.encode("utf-8")
    encrypted = base64.b64encode(iv + cipher.encrypt(plaintext))

    return encrypted


def decrypt(ciphertext, key):
    """
    Decrypt the AES encrypted string.

    Parameters:
        ciphertext -- Encrypted string with AES method.
        key        -- key to decrypt the encrypted string.
    """
    try:
        import base64

        from Crypto.Cipher import AES
    except ImportError as e:
        exit_message(str(e), 1, False)

    padding_string = b"}"

    ciphertext = base64.b64decode(ciphertext)
    iv = ciphertext[: AES.block_size]
    cipher = AES.new(pad(key), AES.MODE_CFB, iv)
    decrypted = cipher.decrypt(ciphertext[AES.block_size :])

    return decrypted


def pad(str):
    """Add padding to the key."""

    padding_string = b"}"
    str_len = len(str)

    # Key must be maximum 32 bytes long, so take first 32 bytes
    if str_len > 32:
        return str[:32]

    # If key size id 16, 24 or 32 bytes then padding not require
    if str_len == 16 or str_len == 24 or str_len == 32:
        return str

    # Add padding to make key 32 bytes long
    return str + ((32 - len(str) % 32) * padding_string)


def get_parent_dir_path(p_path):
    from os.path import dirname

    parent_path = dirname(p_path)
    if not os.path.isdir(p_path):
        parent_path = dirname(parent_path)
    return parent_path


def dirlist(p_isJSON, p_path):
    import glob

    dir_list = []
    for name in glob.iglob(p_path):
        dir_dict = {}
        dir_dict["name"] = name
        if os.path.isdir(name):
            dir_dict["type"] = "d"
        else:
            dir_dict["type"] = "-"
        last_accessed = datetime.fromtimestamp(os.path.getatime(name))
        dir_dict["last_accessed"] = last_accessed.strftime("%Y-%m-%d %H:%M:%S")
        dir_list.append(dir_dict)

    if len(dir_list) > 0:
        dir_list = sorted(
            dir_list,
            key=lambda k: (k["type"].lower, os.path.getatime(k["name"])),
            reverse=True,
        )
    parent_path = get_parent_dir_path(os.path.split(p_path)[0])
    if not parent_path.endswith(os.sep):
        parent_path = parent_path + os.sep
    if os.path.exists(parent_path):
        parent_dict = {
            "type": ".",
            "name": parent_path,
            "last_accessed": datetime.fromtimestamp(
                os.path.getatime(parent_path)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }
        dir_list.insert(0, parent_dict)
    if p_isJSON:
        json_dict = {}
        json_dict["data"] = dir_list
        json_dict["state"] = "completed"
        print(json.dumps([json_dict]))
        return 0

    print("DIRLIST for '" + p_path + "':")
    for d in dir_list:
        print("  " + d["type"] + " " + d["name"] + " " + d["last_accessed"])

    return 0


def fatal_error(p_msg):
    msg = "ERROR: " + p_msg
    if os.getenv("isJson", None):
        jsonMsg = {}
        jsonMsg["status"] = "error"
        jsonMsg["msg"] = msg
        print(json.dumps([jsonMsg]))
    else:
        print(msg)
    sys.exit(1)


def escape_ansi_chars(p_str):
    import re

    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    final_lines = ansi_escape.sub("", p_str)
    striped_lines = str(final_lines).strip()
    return striped_lines


def getoutput(p_cmd):
    if sys.version_info < (2, 7):
        import commands

        try:
            out = commands.getoutput(p_cmd)
            return out.strip()
        except Exception:
            return ""

    from subprocess import check_output

    try:
        out = check_output(p_cmd, shell=True)
        return out.strip().decode("ascii")
    except Exception:
        return ""


def is_systemd():
    if get_platform() != "Linux":
        return False

    return (
        os.path.isfile("/usr/bin/systemctl")
        and os.access("/usr/bin/systemctl", os.X_OK)
    ) or (os.path.isfile("/bin/systemctl") and os.access("/bin/systemctl", os.X_OK))


def run_sudo(p_cmd, p_display=True, p_isJSON=False):
    if p_cmd.startswith("sudo "):
        cmd = p_cmd
    else:
        cmd = "sudo " + p_cmd

    rc = run_sh_cmd(cmd, p_display, p_isJSON)

    return rc


def run_sh_cmd(p_cmd, p_display=True, p_isJSON=False):
    if p_display:
        message("$ " + p_cmd, "info")

    rc = os.system(p_cmd)

    return rc


def get_systemd_dir():
    systemd_dir = "/usr/lib/systemd/system"
    if os.path.isdir(systemd_dir):
        # This directory is common to RedHat based systems
        return systemd_dir

    systemd_dir = "/lib/systemd/system"
    if os.path.isdir(systemd_dir):
        # This directory is common to deb / ubuntu
        return systemd_dir

    return ""


def get_service_status(p_svcname):
    if get_platform() == "Linux":
        if is_systemd():
            cmd = "sudo systemctl status " + p_svcname
        else:
            cmd = "sudo service " + p_svcname + " status"

        p = Popen(
            cmd, shell=True, stdout=PIPE, stderr=PIPE, executable=None, close_fds=False
        )
        (stdout, stderr) = p.communicate()
        if p.returncode == 0:
            return "Running"
        else:
            return "Stopped"

    return "?"


def delete_service_win(svcName):
    import win32serviceutil

    is_service_installed = False
    try:
        win32serviceutil.QueryServiceStatus(svcName)
        is_service_installed = True
    except Exception:
        is_service_installed = False
    if is_service_installed:
        sc_path = os.getenv("SYSTEMROOT", "") + os.sep + "System32" + os.sep + "sc"
        system(sc_path + " delete " + svcName, is_admin=True)
    return True


def is_postgres(p_comp):
    pgXX = ["pg11", "pg12", "pg13", "pg14", "pg15", "pg16", "pg17"]
    if p_comp in pgXX:
        return True

    return False


def get_owner_name(p_path=None):
    file_path = p_path
    if not p_path:
        file_path = os.getenv("MY_HOME")
    import pwd

    st = os.stat(file_path)
    uid = st.st_uid
    userinfo = pwd.getpwuid(uid)
    ownername = userinfo.pw_name
    return ownername


# anonymous data from the INFO command
def get_anonymous_info():
    jsonInfo = api.info(True, "", "", False)
    platform = jsonInfo["platform"]
    os = jsonInfo["os"]
    mem = str(jsonInfo["mem"])
    cores = str(jsonInfo["cores"])
    cpu = jsonInfo["cpu"]
    anon = "(" + platform + "; " + os + "; " + mem + "; " + cores + "; " + cpu + ")"
    return anon


# abruptly terminate with a codified message
def exit_message(p_msg, p_rc=1, p_isJSON=None):
    if p_isJSON is None:
        isJSON = os.getenv("isJson", "False")
        if isJSON == "True":
            p_isJSON = True
        else:
            p_isJSON = False

    if p_rc == 0:
        message(p_msg, "info", p_isJSON)
    else:
        message(p_msg, "error", p_isJSON)

    sys.exit(p_rc)


# print codified message to stdout & logfile
def message(p_msg, p_state="info", p_isJSON=None):
    if p_isJSON is None:
        p_isJSON = isJSON

    if p_msg is None:
        return

    jsn_msg = None

    log_level = p_state.lower()
    cur_level = logging.root.level

    if log_level == "error":
        log_level_num = 40
        my_logger.error(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(bcolours.FAIL + characters.CROSS + " " + p_msg + bcolours.ENDC)
                return
            else:
                jsn_msg = p_msg
    elif log_level == "warning":
        log_level_num = 30
        my_logger.warning(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(
                    bcolours.YELLOW + characters.WARNING + " " + p_msg + bcolours.ENDC
                )
                return
            else:
                jsn_msg = p_msg
    elif log_level == "alert":
        log_level_num = 20
        my_logger.alert(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(bcolours.YELLOW + p_msg + bcolours.ENDC)
                return
            else:
                jsn_msg = p_msg
    elif log_level == "debug":
        log_level_num = 10
        my_logger.debug(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(bcolours.YELLOW + p_msg + bcolours.ENDC)
                return
            else:
                jsn_msg = p_msg
    elif log_level == "success":
        log_level_num = 20
        my_logger.info(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(bcolours.OKGREEN + characters.TICK + " " + p_msg + bcolours.ENDC)
                return
            else:
                jsn_msg = p_msg
    elif log_level == "info":
        log_level_num = 20
        my_logger.info(p_msg)
        if log_level_num >= cur_level:
            if not p_isJSON:
                print(p_msg)
                return
            else:
                jsn_msg = p_msg
    else:
        if not p_isJSON:
            print(p_msg)
            return
        else:
            jsn_msg = p_msg

    if jsn_msg != None:
        msg = p_msg.replace("\n", "")
        if msg.strip() > "":
            json_dict = {}
            json_dict["state"] = p_state
            json_dict["msg"] = msg
            print(json.dumps([json_dict]))

    return


def set_colour(message, colour):
    if colour == "red":
        return bcolours.FAIL + message + bcolours.ENDC
    elif colour == "green":
        return bcolours.OKGREEN + message + bcolours.ENDC
    elif colour == "yellow":
        return bcolours.YELLOW + message + bcolours.ENDC
    elif colour == "blue":
        return bcolours.OKBLUE + message + bcolours.ENDC
    elif colour == "purple":
        return bcolours.OKPURPLE + message + bcolours.ENDC
    elif colour == "cyan":
        return bcolours.OKCYAN + message + bcolours.ENDC
    elif colour == "white":
        return bcolours.BOLD + message + bcolours.ENDC
    else:
        return message


def verify(p_json):
    try:
        c = cL.cursor()
        sql = (
            "SELECT component, version, platform, release_date "
            + " FROM versions WHERE is_current = 1 "
            + "ORDER BY 4 DESC, 1"
        )
        c.execute(sql)
        data = c.fetchall()
        for row in data:
            comp_ver = str(row[0]) + "-" + str(row[1])
            plat = str(row[2])
            if plat == "":
                verify_comp(comp_ver)
            else:
                if "win" in plat:
                    verify_comp(comp_ver + "-win")
                elif "osx" in plat:
                    verify_comp(comp_ver + "-osx")
                elif "linux" in plat:
                    if is_el8():
                        verify_comp(comp_ver + "-el8")
                    else:
                        verify_comp(comp_ver + "-amd")
    except Exception as e:
        fatal_sql_error(e, sql, "verify()")

    return


def round_timedelta(dt):
    microseconds_in_tenth_of_second = 100000
    half_of_tenth_of_second = microseconds_in_tenth_of_second // 2
    remainder = dt.microseconds % microseconds_in_tenth_of_second

    if remainder < half_of_tenth_of_second:
        return dt - timedelta(microseconds=remainder)
    else:
        return dt + timedelta(microseconds=microseconds_in_tenth_of_second - remainder)


def verify_comp(p_comp_ver_plat):
    base = get_value("GLOBAL", "REPO") + "/" + p_comp_ver_plat
    url_file = base + ".tgz"
    rc1 = http_is_file(url_file)

    url_checksum = url_file + ".sha512"
    rc2 = http_is_file(url_checksum)

    if rc1 == 0 and rc2 == 0:
        print("GOOD: " + base)
        return 0

    print("BAD:  " + base)
    return 1


def utc_to_local(dt):
    import time

    dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    time_stamp = time.mktime(dt_obj.timetuple())
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    dt_local = dt_obj + offset
    return dt_local


def update_installed_date(p_app):
    try:
        c = cL.cursor()
        install_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE components SET install_dt = ? WHERE component = ?"
        c.execute(sql, [install_date, p_app])
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "update_installed_date()")

    return


def get_uuid():
    return str(uuid.uuid4())


def update_hosts(p_host, p_unique_id, updated=False):
    last_update_utc = datetime.utcnow()

    current_time = last_update_utc

    if p_unique_id:
        unique_id = p_unique_id
    else:
        unique_id = get_uuid()

    if updated:
        exec_sql(
            "UPDATE hosts "
            + "   SET last_update_utc = '"
            + last_update_utc.strftime("%Y-%m-%d %H:%M:%S")
            + "', "
            + "       unique_id = '"
            + str(unique_id)
            + "' "
            + " WHERE host = '"
            + str(p_host)
            + "'"
        )
    return


def get_versions_sql():
    return get_value("GLOBAL", "VERSIONS", "versions.sql")


def get_stage():
    return get_value("GLOBAL", "STAGE", "off")


def get_value(p_section, p_key, p_value=""):
    try:
        c = cL.cursor()
        sql = "SELECT s_value FROM settings WHERE section = ? AND s_key = ?"
        c.execute(sql, [p_section, p_key])
        data = c.fetchone()
        if data is None:
            return p_value
    except Exception as e:
        fatal_sql_error(e, sql, "get_value()")
    return data[0]


def set_value(p_section, p_key, p_value):
    try:
        c = cL.cursor()
        sql = "DELETE FROM settings WHERE section = ? AND s_key = ?"
        c.execute(sql, [p_section, p_key])
        sql = "INSERT INTO settings (section, s_key, s_value) VALUES (?, ?, ?)"
        c.execute(sql, [p_section, p_key, p_value])
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "set_value()")
    return


def remove_comp(p_comp):
    try:
        c = cL.cursor()
        sql = "DELETE FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "remove_comp()")
    return


def unset_value(p_section, p_key):
    try:
        c = cL.cursor()
        sql = "DELETE FROM settings WHERE section = ? AND s_key = ?"
        c.execute(sql, [p_section, p_key])
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "unset_value()")
    return


def get_hosts_file_name():
    pw_file = ""
    host_dir = os.path.join(MY_HOME, "conf")
    pw_file = os.path.join(host_dir, ".hosts")
    return pw_file


def get_host(p_host):
    host_dict = {}
    try:
        c = cL.cursor()
        sql = "SELECT host, name, dir_home FROM hosts where name=?"
        c.execute(sql, [p_host])
        data = c.fetchone()
        if data:
            host_dict = {}
            host_dict["host"] = str(data[0])
            host_dict["host_name"] = str(data[1])
            host_dict["my_home"] = str(data[2])
    except Exception as e:
        print("ERROR: Retrieving host info")
        exit_message(str(e), 1)
    return host_dict


def get_host_with_id(p_host_id):
    try:
        c = cL.cursor()
        sql = "SELECT host FROM hosts where host_id=?"
        c.execute(sql, [p_host_id])
        data = c.fetchone()
        if data:
            return True
    except Exception as e:
        print("ERROR: Retrieving host")
        exit_message(str(e), 1)
    return False


def get_host_with_name(p_host_name):
    try:
        c = cL.cursor()
        sql = "SELECT host FROM hosts where name=?"
        c.execute(sql, [p_host_name])
        data = c.fetchone()
        if data:
            return True
    except Exception as e:
        print("ERROR: Retrieving host")
        exit_message(str(e), 1)
    return False


def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds
        + 0.0
        + (timedelta.seconds + timedelta.days * 24 * 3600) * 10**6
    ) / 10**6


def read_hosts(p_host):
    sql = (
        "SELECT last_update_utc, unique_id \n"
        + "  FROM hosts WHERE host = '"
        + p_host
        + "'"
    )

    try:
        c = cL.cursor()
        c.execute(sql)
        data = c.fetchone()
        if data is None:
            return ["", "", "", ""]
    except Exception as e:
        fatal_sql_error(e, sql, "get_host()")

    last_update_utc = data[0]
    last_update_local = ""
    if last_update_utc:
        last_update_local = str(utc_to_local(data[0]))
    unique_id = data[1]

    return [last_update_utc, last_update_local, unique_id]


def is_password_less_ssh():
    cmd = "ssh -o 'PreferredAuthentications=publickey' localhost 'echo' >/dev/null 2>&1"
    rc = system(cmd)
    if rc:
        return False
    return True


def read_env_file(component):
    script = os.path.join(MY_HOME, component, component + ".env")
    if os.path.isfile(script):
        try:
            pipe1 = Popen(
                ". %s; env" % script, stdout=PIPE, shell=True, executable="/bin/bash"
            )
            output = str(pipe1.communicate()[0].strip())
            lines = output.split("\n")
            env = dict((line.split("=", 1) for line in lines))
            for e in env:
                os.environ[e] = env[e]
        except Exception:
            my_logger.error(traceback.format_exc())
            pass

    return


def get_pgpass_file():
    if get_platform() == "Darwin":
        home = os.getenv("HOME")
        pw_file = home + "/.pgpass"
    else:
        home = get_unix_user_home()
        if home is not None:
            pw_file = home + "/.pgpass"
        else:
            message("No valid HOME for user %s" % get_user(), "error")
            return None

    return pw_file


def set_con(p_args, p_pwd):
    arg = p_args.split()
    if len(arg) != 5:
        message("5 arguments required: svc, host, port, db, user", "error")
        return

    if arg[0] == "postgres":
        host = arg[1]
        port = arg[2]
        db = arg[3]
        user = arg[4]
        remember_pgpassword(p_pwd, port, host, db, user)
        return

    message("Svc '" + str(arg[0]) + "' not supported.  Must be 'postgres'", "error")
    return


def get_con(p_args):
    arg = p_args.split()
    if len(arg) != 5:
        message("5 arguments required: svc, host, port, db, user", "error")
        return

    if arg[0] == "postgres":
        pwd = retrieve_pgpassword(arg[1], arg[2], arg[3], arg[4])
        if pwd is None:
            message("not found", "error")
        else:
            message(pwd)

        return

    message("Svc '" + str(arg[0]) + "' not supported.  Must be 'postgres'", "error")
    return


def retrieve_pgpassword(p_host="localhost", p_port="5432", p_db="*", p_user="postgres"):
    pw_file = get_pgpass_file()
    if pw_file is None:
        return None

    if os.path.isfile(pw_file):
        s_pw = read_file_string(pw_file)
    else:
        return None

    lines = s_pw.split("\n")
    for line in lines:
        f = line.split(":")
        if len(f) != 5:
            continue

        host = f[0]
        port = f[1]
        db = f[2]
        user = f[3]
        pwd = f[4]

        if host != "*" and host != p_host and p_host != "*":
            continue

        if port != "*" and port != p_port and p_port != "*":
            continue

        if db != "*" and db != p_db and p_db != "*":
            continue

        if user != "*" and user != p_user and p_user != "*":
            continue

        # we've got a match
        return pwd

    # we looped through the file and never found a match
    return None


def change_pgpassword(
    p_passwd,
    p_port="5432",
    p_host="localhost",
    p_db="*",
    p_user="postgres",
    p_ver="pg15",
):
    # try and login with the old password and set the new one
    rc = run_sql_cmd(
        p_ver, "ALTER role " + p_user + " PASSWORD '" + p_passwd + "'", False
    )
    if rc == 0:
        rc = remember_pgpassword(p_passwd, p_port, p_host, p_db, p_user, p_ver)
        return
    else:
        message("unable to change password", "error")
        return None


def remember_pgpassword(
    p_passwd,
    p_port="5432",
    p_host="localhost",
    p_db="*",
    p_user="postgres",
    p_ver="pg15",
):
    pw_file = get_pgpass_file()
    if pw_file is None:
        return None

    if os.path.isfile(pw_file):
        s_pw = read_file_string(pw_file)
    else:
        s_pw = ""

    file = open(pw_file, "w")

    # pre-pend the new
    escaped_passwd = p_passwd
    escaped_passwd = escaped_passwd.replace("\\", "\\\\")
    escaped_passwd = escaped_passwd.replace(":", "\\:")

    prt_db_usr_pwd = p_port + ":" + p_db + ":" + p_user + ":" + escaped_passwd
    s_host = p_host + ":" + prt_db_usr_pwd
    file.write(s_host + "\n")
    s_host2 = s_host
    if p_host == "localhost":
        s_host2 = "127.0.0.1:" + prt_db_usr_pwd
        file.write(s_host2 + "\n")

    # append the old (skipping duplicate & blank lines)
    if s_pw > "":
        lines = s_pw.split("\n")
        for line in lines:
            if (line == s_host) or (line == s_host2):
                pass
            else:
                if line.strip() > "":
                    file.write(line + "\n")

    file.close()

    os.chmod(pw_file, 0o600)

    message("Password securely remembered")

    return pw_file


def get_pgconf_filename(p_pgver):
    pg_data = get_column("datadir", p_pgver)
    return pg_data + os.sep + "postgresql.conf"


def get_pgconf(p_pgver):
    config_file = get_pgconf_filename(p_pgver)

    if not os.path.isfile(config_file):
        print("ERROR: Cannot locate file '" + str(config_file) + "'")
        return ""

    if not os.access(config_file, os.W_OK):
        print("ERROR: Write permission denied on '" + str(config_file) + "'")
        return ""

    return read_file_string(config_file)


def put_pgconf(p_pgver, p_conf):
    config_file = get_pgconf_filename(p_pgver)

    write_string_file(p_conf, config_file)

    return


def get_pgconf_filename_auto(p_pgver):
    pg_data = get_column("datadir", p_pgver)
    return pg_data + os.sep + "postgresql.auto.conf"


def get_pgconf_auto(p_pgver):
    config_file = get_pgconf_filename_auto(p_pgver)

    if not os.path.isfile(config_file):
        print("ERROR: Cannot locate file '" + str(config_file) + "'")
        return ""

    if not os.access(config_file, os.W_OK):
        print("ERROR: Write permission denied on '" + str(config_file) + "'")
        return ""

    return read_file_string(config_file)


def put_pgconf_auto(p_pgver, p_conf):
    config_file = get_pgconf_filename_auto(p_pgver)

    write_string_file(p_conf, config_file)

    return


def remove_pgconf_keyval(p_pgver, p_key, p_val=""):
    s = get_pgconf(p_pgver)
    if s == "":
        return False

    ns = ""
    new_line = ""
    old_val_quoted = ""
    lines = s.split("\n")
    for line in lines:
        if line.startswith(p_key):
            print("  old: " + line)
            if p_val == "":
                # skip over this line and continue processing the rest of the file
                continue
            else:
                new_line = remove_line_val(line, p_val)
                print("  new: " + new_line + "\n")
                ns = ns + "\n" + new_line
        else:
            if ns == "":
                ns = line
            else:
                ns = ns + "\n" + line

    put_pgconf(p_pgver, ns)

    return True


def get_val_tokens(p_line):
    comment_pos = p_line.find("#", 1)
    if comment_pos > 0:
        p_line = p_line[1 : (comment_pos - 1)]

    q_start = p_line.find("'", 1)
    if q_start == -1:
        q_start = p_line.find("=", 1)
    q_end = p_line.find("'", (q_start + 1))
    if q_end == -1:
        q_end = len(p_line)
    old_val = p_line[(q_start + 1) : q_end]
    old_val = old_val.replace(",", " ")
    return old_val.split()


def remove_line_val(p_line, p_val):
    old_tokens = get_val_tokens(p_line)

    new_tokens = []
    for tok in old_tokens:
        if tok == p_val:
            continue
        else:
            new_tokens.append(tok)

    return assemble_line_val(p_line, new_tokens)


def assemble_line_val(p_old_line, p_new_tokens, p_val=""):
    tokens = p_old_line.split()
    key = tokens[0]
    if key.startswith("#"):
        key = key[1:]

    new_val = ""
    token_in_list = False
    for token in p_new_tokens:
        if token == p_val:
            if not token_in_list:
                new_val = append_val(new_val, token, key)
                token_in_list = True
        else:
            new_val = append_val(new_val, token, key)

    if not token_in_list:
        new_val = append_val(new_val, p_val, key)

    if new_val.isnumeric():
        new_line = key + " = " + new_val
    else:
        new_line = key + " = '" + new_val + "'"
    return new_line


def prepend_val(p_base, p_val):
    if p_base == "":
        return p_val

    if p_val == "":
        return p_base

    return p_val + ", " + p_base


def append_val(p_base, p_val, p_key=""):
    if (p_key == "shared_preload_libraries") and (p_val == "citus"):
        return prepend_val(p_base, p_val)

    if p_base == "":
        return p_val

    if p_val == "":
        return p_base

    return p_base + ", " + p_val


def change_pgconf_keyval(p_pgver, p_key, p_val, p_replace=False):
    s = get_pgconf(p_pgver)
    if s == "":
        return False

    ns = ""
    new_line = ""
    boolFoundLine = False
    old_val_quoted = ""

    lines = s.split("\n")
    for line in lines:
        if line.startswith(p_key) or line.startswith("#" + p_key):
            boolFoundLine = True
            old_line = line

            if p_replace:
                old_line = p_key + " = ''"

            old_tokens = get_val_tokens(old_line)
            new_line = assemble_line_val(old_line, old_tokens, p_val)

            ns = ns + "\n" + new_line
        else:
            if ns == "":
                ns = line
            else:
                ns = ns + "\n" + line

    if not boolFoundLine:
        if p_val.isnumeric():
            new_line = p_key + " = " + str(p_val)
        else:
            new_line = p_key + " = '" + str(p_val) + "'"
        ns = ns + "\n" + new_line + "\n"

    message("  new: " + new_line)

    put_pgconf(p_pgver, ns)

    return True


def change_pgconf_keyval_auto(p_pgver, p_key, p_val, p_replace=False):
    s = get_pgconf_auto(p_pgver)
    if s == "":
        return False

    ns = ""
    new_line = ""
    boolFoundLine = False
    old_val_quoted = ""

    lines = s.split("\n")
    for line in lines:
        if line.startswith(p_key) or line.startswith("#" + p_key):
            boolFoundLine = True
            old_line = line

            if p_replace:
                old_line = p_key + " = ''"

            old_tokens = get_val_tokens(old_line)
            new_line = assemble_line_val(old_line, old_tokens, p_val)

            ns = ns + "\n" + new_line
        else:
            if ns == "":
                ns = line
            else:
                ns = ns + "\n" + line

    if not boolFoundLine:
        if p_val.isnumeric():
            new_line = p_key + " = " + str(p_val)
        else:
            new_line = p_key + " = '" + str(p_val) + "'"
        ns = ns + "\n" + new_line + "\n"

    message("  new: " + new_line)

    put_pgconf_auto(p_pgver, ns)

    return True

def update_pg_hba_conf(p_pgver, rules):
    pg_data = get_column("datadir", p_pgver)
    pg_hba_path = os.path.join(pg_data, "pg_hba.conf")

    with open(pg_hba_path, "a") as pg_hba:
        for rule in rules:
            line = f"{rule['type']} {rule['database']} {rule['user']} {rule['address']} {rule['method']}\n"
            pg_hba.write(line)

def update_postgresql_conf(p_pgver, p_port, is_new=True, update_listen_addr=True):
    set_column("port", p_pgver, str(p_port))

    pg_data = get_column("datadir", p_pgver)
    s = get_pgconf(p_pgver)
    ns = ""
    lines = s.split("\n")
    pkg_mgr = get_pkg_mgr()
    for line in lines:
        if pkg_mgr == "apt" and (line.startswith("#jit ") or line.startswith("jit ")):
            ns = ns + "\njit = off"

        elif pkg_mgr == "apt" and (
            line.startswith("#dynamic_shared_memory_type")
            or line.startswith("dynamic_shared_memory_type")
        ):
            ns = ns + "\ndynamic_shared_memory_type = mmap"

        elif line.startswith("#archive_mode") or line.startswith("archive_mode"):
            ns = ns + "\narchive_mode = 'on'"

        elif line.startswith("#archive_command") or line.startswith("archive_command"):
            ns = ns + "\narchive_command = '/bin/true'"

        elif line.startswith("#checkpoint_timeout") or line.startswith(
            "checkpoint_timeout"
        ):
            ns = ns + "\ncheckpoint_timeout = 15min"

        elif line.startswith("#checkpoint_completion_target") or line.startswith(
            "checkpoint_completion_target"
        ):
            ns = ns + "\ncheckpoint_completion_target = 0.9"

        elif line.startswith("#port") or line.startswith("port"):
            pt = "port = " + str(p_port) + "\t\t\t\t# (change requires restart)"
            ns = ns + "\n" + pt

        elif (
            is_new
            and line.startswith("#listen_addresses = 'localhost'")
            and update_listen_addr
        ):
            # override default to match default for pg_hba.conf
            la = "listen_addresses = '*'" + "\t\t\t# what IP address(es) to listen on;"
            ns = ns + "\n" + la

        elif is_new and line.startswith("#logging_collector"):
            ns = ns + "\n" + "logging_collector = on"

        elif is_new and line.startswith("#log_directory"):
            log_directory = os.path.join(MY_HOME, "data", "logs", p_pgver).replace(
                "\\", "/"
            )
            ns = ns + "\n" + "log_directory = '" + log_directory + "'"

        elif is_new and line.startswith("#log_filename"):
            ns = ns + "\n" + "log_filename = 'postgresql-%a.log'"

        elif is_new and line.startswith("#log_line_prefix"):
            ns = (
                ns
                + "\n"
                + "log_line_prefix =  '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '"
            )

        elif is_new and line.startswith("#log_truncate_on_rotation"):
            ns = ns + "\n" + "log_truncate_on_rotation = on "

        elif is_new and line.startswith("#log_checkpoints"):
            ns = ns + "\n" + "log_checkpoints = on"

        elif is_new and line.startswith("#log_autovacuum_min_duration"):
            ns = ns + "\n" + "log_autovacuum_min_duration = 0"

        elif is_new and line.startswith("#log_temp_files"):
            ns = ns + "\n" + "log_temp_files = 0"

        elif is_new and line.startswith("#log_lock_waits"):
            ns = ns + "\n" + "log_lock_waits = on"

        elif is_new and line.startswith("#checkpoint_segments"):
            ns = ns + "\n" + "checkpoint_segments = 16"

        elif is_new and line.startswith("#maintenance_work_mem"):
            ns = ns + "\n" + "maintenance_work_mem = 64MB"

        elif is_new and line.startswith("#max_wal_senders"):
            ns = ns + "\n" + "max_wal_senders = 5"

        elif is_new and line.startswith("#track_io_timing"):
            ns = ns + "\n" + "track_io_timing = on"

        elif is_new and line.startswith("#wal_keep_segments"):
            ns = ns + "\n" + "wal_keep_segments = 32"

        elif is_new and line.startswith("#max_replication_slots"):
            ns = ns + "\n" + "max_replication_slots = 5"

        elif is_new and line.startswith("#wal_level"):
            ns = ns + "\n" + "wal_level = hot_standby"

        elif is_new and line.startswith("#ssl = ") and (get_platform() == "Linux"):
            l_ssl = "ssl = on"
            ns = ns + "\n" + l_ssl
            message(l_ssl)

        elif (
            is_new
            and line.startswith("#ssl_cert_file = ")
            and (get_platform() == "Linux")
        ):
            l_scf = "ssl_cert_file = '" + pg_data + "/server.crt'"
            ns = ns + "\n" + l_scf

        elif (
            is_new
            and line.startswith("#ssl_key_file = ")
            and (get_platform() == "Linux")
        ):
            l_skf = "ssl_key_file = '" + pg_data + "/server.key'"
            ns = ns + "\n" + l_skf

        elif is_new and line.startswith("#password_encryption = "):
            ns = ns + "\n" + "password_encryption = scram-sha-256"

        else:
            if ns == "":
                ns = line
            else:
                ns = ns + "\n" + line

    put_pgconf(p_pgver, ns)

    if str(p_port) != "5432":
        message("\nUsing PostgreSQL Port " + str(p_port))

    return


def get_cpu_cores():
    cpu_cores = 0

    if get_platform() == "Linux":
        cpu_cores = int(
            getoutput("grep -E -c 'processor([[:space:]]+):.*' /proc/cpuinfo")
        )
    elif get_platform() == "Darwin":
        cpu_cores = int(getoutput("/usr/sbin/sysctl hw.physicalcpu | awk '{print $2}'"))

    return cpu_cores


def get_mem_mb():
    mem_mb = 0

    if get_platform() == "Linux":
        mem_kb = int(getoutput("cat /proc/meminfo | awk '/MemTotal/ {print $2}'"))
        mem_mb = int(mem_kb / 1024)
    elif get_platform() == "Darwin":
        mem_bytes = int(getoutput("/usr/sbin/sysctl hw.memsize | awk '{print $2}'"))
        mem_mb = int(mem_bytes / 1024 / 1024)

    return mem_mb


def str_mem(in_mb):
    if in_mb < 2000:
        return str(in_mb) + "MB"

    in_gb = round((in_mb / 1000))
    return str(in_gb) + "GB"


def tune_postgresql_conf(p_pgver):
    message("Tuning 'postgresql.conf' parms for '" + p_pgver + "':")
    mem_mb = get_mem_mb()

    s = get_pgconf(p_pgver)
    ns = ""
    lines = s.split("\n")
    for line in lines:
        if line.startswith("shared_buffers") or line.startswith("#shared_buffers"):
            shared_buf_mb = int(mem_mb * 0.25)
            shared_buf = "shared_buffers = " + str_mem(shared_buf_mb)
            message("  new: " + shared_buf)
            ns = ns + "\n" + shared_buf

        elif line.startswith("maintenance_work_mem") or line.startswith(
            "#maintenance_work_mem"
        ):
            maint_mb = int(mem_mb / 10)
            if maint_mb > 4096:
                maint_mb = 4096
            maint_buf = "maintenance_work_mem = " + str_mem(maint_mb)
            message("  new: " + maint_buf)
            ns = ns + "\n" + maint_buf

        elif line.startswith("effective_cache_size") or line.startswith(
            "#effective_cache_size"
        ):
            cache_mb = int(mem_mb * 0.75)
            cache_size = "effective_cache_size = " + str_mem(cache_mb)
            message("  new: " + cache_size)
            ns = ns + "\n" + cache_size

        elif line.startswith("#wal_log_hints"):
            newb = "wal_log_hints = on"
            message("  new: " + newb)
            ns = ns + "\n" + newb

        elif line.startswith("#shared_preload_libraries"):
            newb = "shared_preload_libraries = 'pg_stat_statements'"
            message("  new: " + newb)
            ns = ns + "\n" + newb

        elif line.startswith("#log_min_duration_statement"):
            newb = "log_min_duration_statement = 1000"
            message("  new: " + newb)
            ns = ns + "\n" + newb

        else:
            if ns == "":
                ns = line
            else:
                ns = ns + "\n" + line

    put_pgconf(p_pgver, ns)


def get_email_address(p_email=""):
    print(" ")
    email = "user@domain.com"

    prompt = p_email + "Email [" + email + "]:\n"

    isYES = str(os.getenv("isYes", "False"))
    if isYES == "True":
        print(prompt)

    try:
        while True:
            email1 = input(prompt)
            if email1.strip() == "":
                email1 = email
                break
            email2 = input("Confirm Email:\n")
            if email1 == email2:
                break
            else:
                print(" ")
                print("Email mis-match, try again.")
                print(" ")
                continue
    except KeyboardInterrupt:
        sys.exit(1)

    return email1


def get_superuser_passwd(p_user="Superuser"):
    message(" ")

    passwd = get_random_password()
    prompt = p_user + " Password: "

    isYES = str(os.getenv("isYes", "False"))
    if isYES == "True":
        message(prompt)
        return passwd

    try:
        while True:
            pg_pass1 = getpass.getpass(prompt)
            if pg_pass1.strip() == "":
                pg_pass1 = passwd
                break
            pg_pass2 = getpass.getpass(str("Confirm Password: "))
            if pg_pass1 == pg_pass2:
                break
            else:
                print("\nPassword mis-match, try again.\n")
                continue
    except KeyboardInterrupt:
        sys.exit(1)

    return pg_pass1


def write_pgenv_file(
    p_pghome, p_pgver, p_pgdata, p_pguser, p_pgdatabase, p_pgport, p_pgpassfile
):
    pg_bin_path = os.path.join(p_pghome, "bin")

    export = "export "
    source = "source"
    newpath = export + "PATH=" + pg_bin_path + ":$PATH"
    env_file = p_pghome + os.sep + p_pgver + ".env"

    try:
        file = open(env_file, "w")
        file.write(export + "PGHOME=" + p_pghome + "\n")
        file.write(export + "PGDATA=" + p_pgdata + "\n")
        file.write(newpath + "\n")
        file.write(export + "PGUSER=" + p_pguser + "\n")
        file.write(export + "PGDATABASE=" + p_pgdatabase + "\n")
        file.write(export + "PGPORT=" + p_pgport + "\n")
        if p_pgpassfile:
            file.write(export + "PGPASSFILE=" + p_pgpassfile + "\n")
        file.write(
            export + "GDAL_DATA=" + os.path.join(p_pghome, "share", "gdal") + "\n"
        )
        file.write("if [ -f /usr/lib64/perl5/CORE/libperl.so ]; then \n")
        file.write(
            "    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/perl5/CORE \n"
        )
        file.write("fi \n")
        if os.path.exists("/etc/lsb-release"):
            # ubuntu xterm incompatible with el8 xterm key mappings
            file.write("export TERM=vt100\n")
        file.close()
        os.chmod(env_file, 0o755)
    except IOError:
        return 1

    message(" ")
    return 0


def is_port_assigned(p_port, p_comp):
    try:
        c = cL.cursor()
        sql = (
            "SELECT port FROM components WHERE component != '"
            + p_comp
            + "' and port='"
            + str(p_port)
            + "' and datadir !=''"
        )
        c.execute(sql)
        data = c.fetchone()
        if data is None:
            return False
    except Exception as e:
        fatal_sql_error(e, sql, "is_port_assigned()")
    return True


def get_avail_port(p_prompt, p_def_port, p_comp="", isJSON=False):
    def_port = int(p_def_port)

    # iterate to first non-busy port
    while is_socket_busy(def_port, p_comp):
        def_port = def_port + 1
        continue

    err_msg = "Port must be between 1000 and 9999, try again."

    while True:
        s_port = str(def_port)

        if s_port.isdigit() == False:
            print(err_msg)
            continue

        i_port = int(s_port)

        if (i_port < 1000) or (i_port > 9999):
            print(err_msg)
            continue

        if is_port_assigned(i_port, p_comp) or is_socket_busy(i_port, p_comp):
            if not isJSON:
                print("Port " + str(i_port) + " is in use.")
            def_port = str(i_port + 1)
            continue

        break

    return i_port


def delete_dir(p_dir):
    cmd = 'rm -rf "' + p_dir + '"'
    rc = system(cmd)
    return rc


def system(p_cmd, is_display=False):
    if is_display:
        print("\n$  " + p_cmd)

    rc = os.system(p_cmd)

    if is_display:
        if str(rc) == "0":
            pass
        else:
            print("rc = " + str(rc))

    return rc


def pretty_rounder(p_num, p_scale):
    rounded = round(p_num, p_scale)
    if not (rounded % 1):
        return int(rounded)
    return rounded


def get_version():
    return MY_VERSION


def get_depend():
    dep = []
    try:
        c = cL.cursor()
        sql = (
            "SELECT DISTINCT r1.component, r2.component, p.start_order \n"
            + "  FROM projects p, releases r1, releases r2, versions v \n"
            + " WHERE v.component = r1.component \n"
            + "   AND "
            + like_pf("v.platform")
            + " \n"
            + "   AND p.project = r1.project \n"
            + "   AND p.depends = r2.project \n"
            + "ORDER BY 3"
        )
        c.execute(sql)
        data = c.fetchall()
        for row in data:
            component = str(row[0])
            depends = str(row[1])
            p = component + " " + depends
            if meta.is_extension(component):
                last5_comp = component[-5:]
                last5_dep = depends[-5:]
                if last5_comp != last5_dep:
                    continue
            dep.append(p.split())
    except Exception as e:
        fatal_sql_error(e, sql, "get_depend()")
    return dep


def process_sql_file(p_file, p_json):
    isSilent = os.environ.get("isSilent", None)

    rc = True

    # verify the hub version ##################
    file = open(p_file, "r")
    cmd = ""
    for line in file:
        line_strip = line.strip()
        if line_strip == "":
            continue
        cmd = cmd + line
        if line_strip.endswith(";"):
            if ("hub" in cmd) and ("INSERT INTO versions" in cmd) and ("1," in cmd):
                cmdList = cmd.split(",")
                newHubV = cmdList[1].strip().replace("'", "")
                oldHubV = get_version()
                msg_frag = "'hub' from v" + oldHubV + " to v" + newHubV + "."
                if newHubV == oldHubV:
                    msg = "'hub' is v" + newHubV
                if newHubV > oldHubV:
                    msg = "Automatic updating " + msg_frag
                if newHubV < oldHubV:
                    msg = "ENVIRONMENT ERROR:  Cannot downgrade " + msg_frag
                    rc = False
                if p_json:
                    print('[{"status":"wip","msg":"' + msg + '"}]')
                else:
                    if not isSilent:
                        print(msg)
                my_logger.info(msg)
                break
            cmd = ""
    file.close()

    if rc == False:
        if p_json:
            print('[{"status":"completed","has_updates":0}]')
        return False

    # process the file ##########################
    file = open(p_file, "r")
    cmd = ""
    for line in file:
        line_strip = line.strip()
        if line_strip == "":
            continue
        cmd = cmd + line
        if line_strip.endswith(";"):
            exec_sql(cmd)
            cmd = ""
    file.close()

    return True


def exec_sql(cmd):
    try:
        c = cL.cursor()
        c.execute(cmd)
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, cmd, "exec_sql()")


def show_metrics(p_home, p_port, p_data, p_log, p_pid):
    return
    if p_home:
        print("  --homedir " + str(p_home))
    if p_port:
        print("  --port    " + str(p_port))
    if p_data:
        print("  --datadir " + p_data)
    if p_log:
        print("  --logfile " + p_log)
    if p_pid:
        print("  --pidfile " + p_pid)


def get_column(p_column, p_comp, p_env=""):
    try:
        c = cL.cursor()
        sql = (
            "SELECT " + p_column + " FROM components WHERE component = '" + p_comp + "'"
        )
        c.execute(sql)
        data = c.fetchone()
        if data is None:
            return "-1"
        col_val = str(data[0])
        if col_val == "None" or col_val == "" or col_val is None:
            if p_env > "":
                if p_env.startswith("$"):
                    env = os.getenv(p_env[1:], "")
                else:
                    env = p_env
                if env > "":
                    set_column(p_column, p_comp, env)
                    return env
                else:
                    return "-1"
    except Exception as e:
        fatal_sql_error(e, sql, "get_column()")
    return col_val


def set_column(p_column, p_comp, p_value):
    try:
        c = cL.cursor()
        sql = (
            "UPDATE components SET "
            + p_column
            + " = '"
            + str(p_value)
            + "' "
            + " WHERE component = '"
            + p_comp
            + "'"
        )
        c.execute(sql)
        cL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "set_column()")


def fatal_sql_error(err, sql, func):
    msg = "#"
    msg = msg + "\n" + "################################################"
    msg = msg + "\n" + "FATAL SQL Error in " + func
    msg = msg + "\n" + "    SQL Message =  " + err.args[0]
    msg = msg + "\n" + "  SQL Statement = " + sql
    msg = msg + "\n" + "################################################"
    print(msg)
    if str(err.args[0]).startswith("no such table: versions") and func.startswith(
        "get_depend()"
    ):
        pass
    else:
        my_logger.error(msg)
    sys.exit(1)


def get_file_checksum(p_filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha512()
    with open(p_filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_file_string(p_filename, action=None):
    try:
        f = open(p_filename, "r")
        filedata = f.read()
        f.close()
        return filedata
    except IOError as e:
        if action is None:
            print(e)
        return ""


def write_string_file(p_stringname, p_filename):
    f = open(p_filename, "w")
    f.write(p_stringname)
    f.close()


def replace(p_olddata, p_newdata, p_filename, p_quiet=False):
    filestring = read_file_string(p_filename)
    if not p_quiet:
        print(
            "  replace ("
            + p_olddata
            + ") with ("
            + p_newdata
            + ") on file ("
            + p_filename
            + ")"
        )
    newstring = filestring.replace(p_olddata, p_newdata)
    write_string_file(newstring, p_filename)
    return


def get_pid(name):
    from subprocess import check_output

    return check_output(["pidof", name])


def kill_pid(pid):
    if pid < 1:
        return
    os.kill(pid, signal.SIGKILL)
    return


# Terminate a process tree with the PID
def kill_process_tree(pid):
    import psutil

    process = psutil.Process(pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
    return True


def is_pid_running(p_pid):
    import psutil

    return psutil.pid_exists(int(p_pid))


def get_platform():
    return str(platform.system())


def get_arch():
    return get_el_ver()


def get_el_os():
    rel_file = "/etc/redhat-release"
    if os.path.exists(rel_file):
        rc = os.system('grep "platform:el9" /etc/os-release > /dev/null 2>&1')
        if rc == 0:
            return "EL9"

        rc = os.system('grep "platform:el8" /etc/os-release > /dev/null 2>&1')
        if rc == 0:
            return "EL8"

        return "EL"

    return None


def get_el_ver():
    if platform.system() == "Darwin":
        arch = getoutput("arch")
        if arch == "i386":
            return "osx-i386"
        else:
            return "osx"

    elv = os.getenv("ELV", None)
    if elv:
        return str(elv)

    glibc_v = get_glibc_version()
    arch = getoutput("uname -m")
    if arch == "aarch64":
        if glibc_v >= "2.34":
            return "arm9"
        else:
            return "arm"
    else:
        if glibc_v >= "2.34":
            return "el9"
        else:
            return "el8"


def is_el8():
    if platform.system() != "Linux":
        return False

    glibc_v = get_glibc_version()

    if get_glibc_version() < "2.34":
        return True

    return False


def get_os():
    if platform.system() == "Darwin":
        arch = getoutput("arch")
        if arch == "i386":
            return "osx-i386"
        else:
            return "osx"

    if platform.system() != "Linux":
        return "xxx"

    try:
        rel_file = ""
        if os.path.exists("/etc/redhat-release"):
            # el
            rel_file = "/etc/redhat-release"
        elif os.path.exists("/etc/system-release"):
            # amazon linux
            rel_file = "/etc/system-release"
        elif os.path.exists("/etc/lsb-release"):
            # ubuntu
            rel_file = "/etc/lsb-release"
        else:
            rel_file = "/etc/os-release"

        if rel_file > "" and os.path.exists(rel_file):
            return get_el_ver()

    except Exception:
        pass

    return "???"


def get_pkg_mgr():
    yum_ver = getoutput("yum --version 2>/dev/null")
    if yum_ver == "":
        return "apt"
    return "yum"


def has_admin_rights():
    status = True
    return status


def get_default_pf():
    if get_platform() == "Darwin":
        return "osx"

    return "el8"


def get_pf():
    return get_os()


def like_pf(p_col):
    pf = get_pf()
    OR = " OR "
    c1 = p_col + " LIKE ''"
    c2 = p_col + " LIKE '%" + pf + "%'"
    clause = "(" + c1 + OR + c2 + ")"

    return clause


def has_platform(p_platform):
    pf = get_pf()
    return p_platform.find(pf)


def set_lang_path():
    perl_home = MY_HOME + os.sep + "perl5" + os.sep + "perl"
    if os.path.exists(perl_home):
        os.environ["PERL_HOME"] = perl_home
        path = os.getenv("PATH")
        os.environ["PATH"] = (
            perl_home
            + os.sep
            + "site"
            + os.sep
            + "bin"
            + os.pathsep
            + perl_home
            + os.sep
            + "bin"
            + os.pathsep
            + MY_HOME
            + os.sep
            + "perl5"
            + os.sep
            + "c"
            + os.sep
            + "bin"
            + os.pathsep
            + path
        )
    tcl_home = MY_HOME + os.sep + "tcl86"
    if os.path.exists(tcl_home):
        os.environ["TCL_HOME"] = tcl_home
        path = os.getenv("PATH")
        os.environ["PATH"] = tcl_home + os.sep + "bin" + os.pathsep + path
    java_home = MY_HOME + os.sep + "java8"
    if os.path.exists(java_home):
        os.environ["JAVA_HOME"] = java_home
        path = os.getenv("PATH")
        os.environ["PATH"] = java_home + os.sep + "bin" + os.pathsep + path


def get_user():
    return getpass.getuser()


def get_unix_user_home():
    return os.path.expanduser("~")


def get_host():
    host = ""
    if get_platform() == "Linux":
        host = get_linux_hostname()
    else:
        try:
            host = getoutput("hostname")
        except Exception:
            host = "127.0.0.1"
    return host


def get_host_short():
    return get_host()


def get_linux_hostname():
    return getoutput("cat /etc/hostname | sed '/^#/d'")


def get_host_ip():
    return "127.0.0.1"


def make_uri(in_name):
    return "///" + in_name.replace("\\", "/")


def launch_daemon(arglist, p_logfile_name):
    if p_logfile_name is None:
        f_logfile = os.devnull
    else:
        f_logfile = p_logfile_name

    with open(f_logfile, "wb") as outfile:
        Popen(arglist, stdin=PIPE, stdout=outfile, stderr=STDOUT)

    return 0


def delete_file(p_file_name):
    if os.path.isfile(p_file_name):
        os.remove(p_file_name)
    return


def download_file(p_url, p_file):
    if os.path.exists(p_file):
        os.system("rm -f " + p_file)

    message(f"Downloading {p_url}/{p_file}")
    f = str(p_url) + "/" + p_file
    try:
        fu = urllib2.urlopen(f)
        local_file = open(p_file, "wb")
        local_file.write(fu.read())
        local_file.close()
    except Exception as e:
        message("ERROR: Unable to download " + f + "\n" + str(e))
        return False

    return True


def unpack_file(p_file):
    if platform.system() in ("Linux", "Darwin"):
        rc = posix_unpack(os.getcwd() + os.sep + p_file)
        if rc == 0:
            return True
        else:
            return False

    message(f"Unpacking {p_file} ...")
    try:
        tar = tarfile.open(p_file)
        tar.extractall(path=".")
        tar.close()
    except Exception as e:
        message("ERROR: Unable to unpack \n" + str(e))
        return False

    return True


def http_is_file(p_url):
    try:
        req = urllib2.Request(p_url, None, http_headers())
        u = urllib2.urlopen(req, timeout=10)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        return 1

    return 0


def urlEncodeNonAscii(b):
    import re

    return re.sub("[\x80-\xFF]", lambda c: "%%%02x" % ord(c.group(0)), b)


def http_headers():
    user_agent = "CLI/" + get_version() + " " + get_anonymous_info()
    headers = {"User-Agent": urlEncodeNonAscii(user_agent)}
    return headers


def get_url(url):
    import urllib.request

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=0.05) as response:
            the_page = response.read()
    except Exception:
        return ""

    return the_page.decode("utf-8").replace("\n", "")


# retrieve a remote file via http #################################################
def http_get_file(
    p_json, p_file_name, p_url, p_out_dir, p_display_status, p_msg, component_name=None
):
    file_exists = False
    file_name_complete = p_out_dir + os.sep + p_file_name
    file_name_partial = file_name_complete + ".part"
    json_dict = {}
    json_dict["state"] = "download"
    file_size_dl = 0
    file_size_dl_mb = 0

    if component_name is not None:
        json_dict["component"] = component_name
    if p_display_status:
        if not p_json:
            print(p_msg)
    try:
        delete_file(file_name_partial)
        file_url = p_url + "/" + p_file_name
        req = urllib2.Request(file_url, None, http_headers())

        u = urllib2.urlopen(req, timeout=10)

        meta = u.info()
        file_size = int(meta.get_all("Content-Length")[0])

        block_sz = 8192
        f = open(file_name_partial, "wb")
        file_exists = True
        log_file_name = p_file_name.replace(".tgz", "")
        log_msg = "Downloading file %s " % log_file_name
        is_checksum = False
        if p_file_name.find("sha512") >= 0:
            log_file_name = p_file_name.replace(".tgz.sha512", "")
            log_msg = "Downloading checksum for %s " % log_file_name
        if p_display_status:
            my_logger.info(log_msg)
        previous_time = datetime.now()
        while True:
            if (
                not p_file_name.endswith(".txt")
                and not p_file_name.startswith("install.py")
                and not os.path.isfile(pid_file)
            ):
                raise KeyboardInterrupt("No lock file exists.")
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            file_size_dl_mb = int(file_size_dl / 1024 / 1024)
            download_pct = int(file_size_dl * 100 / file_size)
            if p_display_status:
                my_modulo = file_size_dl % (1024 * 1024 * 50)
                if (file_size_dl_mb > 1) and (my_modulo == 0):
                    if p_json:
                        json_dict["status"] = "wip"
                        json_dict["mb"] = get_file_size(file_size_dl)
                        json_dict["pct"] = download_pct
                        json_dict["file"] = p_file_name
                        if component_name:
                            json_dict["component"] = component_name
                        print(json.dumps([json_dict]))
                    else:
                        print_status_msg(file_size_dl_mb, download_pct)
                        current_time = datetime.now()
                        log_diff = current_time - previous_time
                        if log_diff.seconds > 0:
                            previous_time = current_time

        if p_display_status and p_json:
            json_dict.clear()
            if component_name is not None:
                json_dict["component"] = component_name
            json_dict["state"] = "download"
            json_dict["status"] = "complete"
            print(json.dumps([json_dict]))
    except (urllib2.URLError, urllib2.HTTPError) as e:
        msg = "url=" + p_url + ", file=" + p_file_name
        if p_json:
            json_dict.clear()
            json_dict["msg"] = "Unable to download."
            if component_name is not None:
                json_dict["component"] = component_name
                json_dict["msg"] = (
                    "Unable to download " + component_name + " component."
                )
            json_dict["state"] = "error"
            print(json.dumps([json_dict]))
        else:
            print("\n" + "ERROR: " + str(e))
            print("       " + msg)
        my_logger.error("URL Error while dowloading file %s (%s)", p_file_name, str(e))
        if file_exists and not f.closed:
            f.close()
        delete_file(file_name_partial)
        file_exists = False
        return False
    except socket.timeout as e:
        if p_json:
            json_dict.clear()
            if component_name is not None:
                json_dict["component"] = component_name
            json_dict["state"] = "error"
            json_dict["msg"] = "Connection timed out while downloading."
            print(json.dumps([json_dict]))
        else:
            print("\n" + str(e))
        my_logger.error(
            "Timeout Error while dowloading file %s (%s)", p_file_name, str(e)
        )
        if file_exists and not f.closed:
            f.close()
        delete_file(file_name_partial)
        file_exists = False
        return False
    except (IOError, OSError) as e:
        if p_json:
            json_dict.clear()
            if component_name is not None:
                json_dict["component"] = component_name
            json_dict["state"] = "error"
            json_dict["msg"] = str(e)
            print(json.dumps([json_dict]))
        else:
            print("\n" + str(e))
        my_logger.error("IO Error while dowloading file %s (%s)", p_file_name, str(e))
        if file_exists and not f.closed:
            f.close()
        delete_file(file_name_partial)
        file_exists = False
        return False
    except KeyboardInterrupt:
        if p_json:
            json_dict.clear()
            if component_name is not None:
                json_dict["component"] = component_name
            json_dict["state"] = "download"
            json_dict["status"] = "cancelled"
            json_dict["msg"] = "Download cancelled"
            print(json.dumps([json_dict]))
        else:
            print("Download Cancelled")
        my_logger.error("Cancelled dowloading file %s ", p_file_name)
        if file_exists and not f.closed:
            f.close()
        delete_file(file_name_partial)
        file_exists = False
        return False
    except ValueError as e:
        if p_json:
            json_dict.clear()
            if component_name is not None:
                json_dict["component"] = component_name
            json_dict["state"] = "error"
            json_dict["msg"] = str(e)
            print(json.dumps([json_dict]))
        else:
            print("\n" + str(e))
        my_logger.error(
            "Value Error while dowloading file %s (%s)", p_file_name, str(e)
        )
        if file_exists and not f.closed:
            f.close()
        delete_file(file_name_partial)
        file_exists = False
        return False
    finally:
        if file_size_dl_mb >= 1 and not p_json:
            print_status_msg(file_size_dl_mb, 100)
        if file_exists and not f.closed:
            f.close()

    delete_file(file_name_complete)
    f.close()
    os.rename(file_name_partial, file_name_complete)
    return True


def print_status_msg(p_mb, p_pct):
    str_size_mb = str(p_mb)
    pretty_size_mb = str_size_mb.rjust(5) + " MB"
    print(pretty_size_mb + " [" + str(p_pct) + "%]")


def is_writable(path):
    try:
        testfile = tempfile.TemporaryFile(dir=path)
        testfile.close()
    except (IOError, OSError):
        return False
    return True


# is running with Admin/Root priv's #########################################
def is_admin():
    rc = getoutput("id -u")

    if str(rc) == "0":
        return True
    else:
        return False


def is_protected(p_comp, p_platform):
    if p_comp.startswith("python") or p_comp.startswith("postgres"):
        return True
    return False


def is_server(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT pidfile, port FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return False
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_state()")

    pidfile = data[0]
    port = data[1]

    if str(pidfile) != "None" and str(pidfile) > " ":
        return True

    if str(port) > "1":
        return True

    return False


def print_error(p_error):
    print("")
    print("ERROR: " + p_error)
    return


# Get Component Datadir ###################################################
def get_comp_datadir(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT datadir FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "NotInstalled"
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_state()")
    if data[0] is None:
        return ""
    return str(data[0])


# Get postgres components installed
def get_installed_postgres_components():
    try:
        c = cL.cursor()
        sql = "SELECT component, project, version, port, datadir, logdir FROM components WHERE project = 'pg' "
        c.execute(sql)
        data = c.fetchall()
        return data
    except Exception as e:
        fatal_sql_error(e, sql, "get_installed_postgres_components()")
    return None


# Get parent component for extension
def get_parent_component(p_ext, p_ver):
    try:
        c = cL.cursor()
        sql = "SELECT parent FROM versions WHERE component = ? "
        if p_ver != 0:
            sql = sql + " AND version = '" + p_ver + "'"
        c.execute(sql, [p_ext])
        data = c.fetchone()
        if data is None:
            return ""
    except Exception as e:
        fatal_sql_error(e, sql, "get_parent_component()")
    return str(data[0])


def get_comp_state(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT status FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "NotInstalled"
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_state()")
    return str(data[0])


def get_comp_port(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT port FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "-1"
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_port()")
    return str(data[0])


def get_comp_pidfile(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT pidfile FROM components WHERE component = ?"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return "-1"
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_pidfile()")
    return str(data[0])


def is_socket_busy(p_port, p_comp=""):
    if p_comp > "":
        is_ready_file = "pg_isready"
        isready = os.path.join(os.getcwd(), p_comp, "bin", is_ready_file)
        if os.path.isfile(isready):
            rc = system(isready + " -d postgres -q -p " + str(p_port))
            if rc == 0:
                return True

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((get_host_ip(), p_port))
    s.close()
    if result == 0:
        return True
    else:
        return False


def is_pg_ready(pg_v):
    rc = os.system(
        os.getcwd() + "/" + pg_v + "/bin/pg_isready -d postgres > /dev/null 2>&1"
    )
    if rc == 0:
        return True

    return False


def wait_pg_ready(pg_v, max_tries=10):
    for n in range(1, max_tries):
        time.sleep(1)
        if is_pg_ready(pg_v):
            message(f"{pg_v} is ready {n}", "info")
            return True
        else:
            message(f"{pg_v} is not ready {n}", "info")

    return False


def get_comp_category(p_comp):
    try:
        c = cL.cursor()
        sql = "SELECT p.category FROM projects p,components c WHERE component = ? and p.project=c.project"
        c.execute(sql, [p_comp])
        data = c.fetchone()
        if data is None:
            return None
    except Exception as e:
        fatal_sql_error(e, sql, "get_comp_port()")
    return data[0]


# get the list for files in a folder recursively:
def get_files_recursively(directory):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            filename = os.path.join(root, basename)
            yield filename


# create the manifest file for the extension
def create_manifest(ext_comp, parent_comp, upgrade=None):
    PARENT_DIR = os.path.join(MY_HOME, parent_comp)
    COMP_DIR = os.path.join(MY_HOME, ext_comp)
    if upgrade:
        COMP_DIR = os.path.join(COMP_DIR + "_new", ext_comp)

    manifest = {}
    manifest["component"] = ext_comp
    manifest["parent"] = parent_comp

    target_files = []

    files_list = get_files_recursively(COMP_DIR)
    for file in files_list:
        target_file = file.replace(COMP_DIR, PARENT_DIR)
        target_files.append(target_file)

    manifest["files"] = target_files

    manifest_file_name = ext_comp + ".manifest"

    manifest_file_path = os.path.join(MY_HOME, "conf", manifest_file_name)

    try:
        with open(manifest_file_path, "w") as f:
            json.dump(manifest, f, sort_keys=True, indent=4)
    except Exception as e:
        my_logger.error(str(e))
        my_logger.error(traceback.format_exc())
        print(str(e))
        pass

    return True


def copy_extension_files(ext_comp, parent_comp, upgrade=None):
    # always overlay these files ##
    PARENT_DIR = os.path.join(MY_HOME, parent_comp)
    COMP_DIR = os.path.join(MY_HOME, ext_comp)
    if upgrade:
        COMP_DIR = os.path.join(COMP_DIR + "_new", ext_comp)

    cmd = "cp -r " + COMP_DIR + "/. " + PARENT_DIR
    os.system(cmd)
    return True


def delete_extension_files(manifest_file, upgrade=None):
    my_logger.info("# checking for extension files.")
    try:
        with open(manifest_file) as data_file:
            data = json.load(data_file)
    except Exception as e:
        print(str(e))
        exit(1)
    for file in data["files"]:
        if os.path.isfile(file) or os.path.islink(file):
            pass
        else:
            continue
        try:
            fp = open(file)
            fp.close()
        except IOError as e:
            if upgrade:
                raise e
            print(str(e))
            exit(1)
    my_logger.info("deleting extension files.")
    for file in data["files"]:
        if os.path.isfile(file) or os.path.islink(file):
            pass
        else:
            continue
        try:
            os.remove(file)
        except IOError as e:
            my_logger.error("failed to remove " + file)
            my_logger.error(str(e))
            my_logger.error(traceback.format_exc())
            print(str(e))
    return True


# Get file size in readable format
def get_file_size(file_size, precision=1):
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    suffixIndex = 0
    while file_size > 1024:
        suffixIndex += 1  # increment the index of the suffix
        file_size = file_size / 1024.0  # apply the division
    return "%.*f %s" % (precision, file_size, suffixes[suffixIndex])


def get_readable_time_diff(amount, units="seconds", precision=0):
    def process_time(amount, units):
        INTERVALS = [
            1,
            60,
            60 * 60,
            60 * 60 * 24,
            60 * 60 * 24 * 7,
            60 * 60 * 24 * 7 * 4,
            60 * 60 * 24 * 7 * 4 * 12,
        ]

        NAMES = [
            ("second", "seconds"),
            ("minute", "minutes"),
            ("hour", "hours"),
            ("day", "days"),
            ("week", "weeks"),
            ("month", "months"),
            ("year", "years"),
        ]

        result = []

        unit = list(map(lambda a: a[1], NAMES)).index(units)
        # Convert to seconds
        amount = amount * INTERVALS[unit]

        for i in range(len(NAMES) - 1, -1, -1):
            a = amount // INTERVALS[i]
            if a > 0:
                result.append((a, NAMES[i][1 % a]))
                amount -= a * INTERVALS[i]

        return result

    if int(amount) == 0:
        return "0 Seconds"
    rd = process_time(int(amount), units)
    cont = 0
    for u in rd:
        if u[0] > 0:
            cont += 1

    buf = ""
    i = 0

    if precision > 0 and len(rd) > 2:
        rd = rd[:precision]
    for u in rd:
        if u[0] > 0:
            buf += "%d %s" % (u[0], u[1])
            cont -= 1

        if i < (len(rd) - 1):
            if cont > 1:
                buf += ", "
            else:
                buf += " and "

        i += 1

    return buf


# recursively check and restore all env / extension files during upgrade
def recursively_copy_old_files(dcmp, diff_files=[], ignore=None):
    for name in dcmp.left_only:
        if ignore and name in ignore:
            continue
        try:
            source_file = os.path.join(dcmp.left, name)
            shutil.move(source_file, dcmp.right)
        except Exception as e:
            my_logger.error(
                "Failed to restore the file %s due to %s"
                % (os.path.join(dcmp.right, name), str(e))
            )
            my_logger.error(traceback.format_exc())
            diff_files.append([name, dcmp.left, dcmp.right])
    for sub_dcmp in dcmp.subdirs.values():
        allfiles = diff_files
        recursively_copy_old_files(sub_dcmp, allfiles)
    return diff_files


# restore any extensions or env/conf files during upgrade
def restore_conf_ext_files(src, dst, ignore=None):
    if os.path.isdir(dst):
        diff = filecmp.dircmp(src, dst)
        recursively_copy_old_files(diff, ignore=ignore)
    return True


# Add the application to launchpad in OSX
def create_shortlink_osx(short_link, target_link):
    short_link_path = os.path.join("/Applications", short_link)
    cmd = "ln -s '{0}' '{1}'".format(target_link, short_link_path)
    os.system(cmd)
    os.system("killall Dock")


# delete the application from launchpad in OSX
def delete_shortlink_osx(short_link):
    short_link_path = os.path.join("/Applications", short_link)
    cmd = "rm '{0}'".format(short_link_path)
    if os.path.exists(short_link_path):
        os.system(cmd)
        os.system("killall Dock")


def exit_cleanly(p_rc, conn=None):
    if conn:
        try:
            conn.close()
        except Exception:
            pass
    sys.exit(p_rc)


def get_comp_lists(p_mode, arg, args, ignore_comp_list, p_host, connL):
    isJSON = False
    if os.environ.get("isJson", "False") == "True":
        isJSON = True
    p_comp_list = []
    extra_args = ""
    p_version = ""
    info_arg = 0
    try:
        if p_mode in ignore_comp_list:
            pass
        else:
            for i in range((arg + 1), len(args)):
                if p_host > "":
                    break
                if p_mode in ("update", "cancel"):
                    print_error("No additional parameters allowed.")
                    exit_cleanly(1, connL)
                comp1 = meta.wildcard_component(args[i])
                if meta.is_component(comp1):
                    p_comp_list.append(comp1)
                    if p_mode == "info" and args[i] == "all":
                        info_arg = 1
                        p_version = "all"
                else:
                    if (
                        p_mode in ("config", "init", "provision")
                        and len(p_comp_list) == 1
                    ):
                        if str(args[i]) > "":
                            extra_args = extra_args + '"' + str(args[i]) + '" '
                    elif (
                        p_mode in ("info", "download", "install", "update")
                        and len(p_comp_list) == 1
                        and info_arg == 0
                    ):
                        if p_mode == "info":
                            p_version = args[i]
                        else:
                            ver1 = meta.wildcard_version(p_comp_list[0], args[i])
                            p_version = meta.get_platform_specific_version(
                                p_comp_list[0], ver1
                            )
                            if p_version == "-1":
                                print_error(
                                    "Invalid component version parameter  ("
                                    + ver1
                                    + ")"
                                )
                                exit_cleanly(1, connL)
                            info_arg = 1
                    elif p_mode in ignore_comp_list:
                        pass
                    else:
                        exit_message(
                            "Invalid component parameter (" + args[i] + ")", 1, isJSON
                        )

        if len(p_comp_list) == 0:
            if p_mode == "download":
                print_error("No component parameter specified.")
                exit_cleanly(1, connL)
            p_comp_list.append("all")

        if len(p_comp_list) >= 1:
            p_comp = p_comp_list[0]
    except Exception as e:
        exit_message(str(e), 1, isJSON)
        exit_cleanly(1, connL)

    return info_arg, p_comp_list, p_comp, p_version, extra_args


def check_comp(p_comp, p_port, p_kount, check_status=False):
    ver = meta.get_ver_plat(p_comp)
    app_state = get_comp_state(p_comp)

    if app_state in ("Disabled", "NotInstalled"):
        api.status(isJSON, p_comp, ver, app_state, p_port, p_kount)
        return

    if ((p_port == "0") or (p_port == "1")) and get_column("autostart", p_comp) != "on":
        api.status(isJSON, p_comp, ver, "Installed", "", p_kount)
        return

    is_pg = is_postgres(p_comp)
    if is_pg or p_comp in ("pgdevops"):
        if is_pg:
            read_env_file(p_comp)
        app_datadir = get_comp_datadir(p_comp)
        if app_datadir == "":
            if check_status:
                return "NotInitialized"
            api.status(isJSON, p_comp, ver, "Not Initialized", "", p_kount)
            return

    status = "Stopped"
    comp_svcname = get_column("svcname", p_comp)
    if (
        get_platform() != "Darwin"
        and comp_svcname != ""
        and get_column("autostart", p_comp) == "on"
    ):
        status = get_service_status(comp_svcname)
    elif is_socket_busy(int(p_port), p_comp):
        status = "Running"
    else:
        status = "Stopped"
    if check_status:
        return status
    api.status(isJSON, p_comp, ver, status, p_port, p_kount)

    return


# run external scripts #######################################
def run_script(componentName, scriptName, scriptParm):
    message(f"run_script('{componentName}', '{scriptName}', '{scriptParm}')", "debug")
    installed_comp_list = meta.get_component_list()
    if componentName not in installed_comp_list:
        return

    componentDir = componentName

    cmd = ""
    scriptFile = os.path.join(MY_HOME, componentDir, scriptName)
    if os.path.isfile(scriptFile):
        cmd = "bash"
    else:
        cmd = sys.executable + " -u"
        scriptFile = scriptFile + ".py"

    rc = 0
    compState = get_comp_state(componentName)
    if compState == "Enabled" and os.path.isfile(scriptFile):
        run = cmd + " " + scriptFile + " " + scriptParm
        rc = os.system(run)

    if rc != 0:
        print("Error running " + scriptName)
        exit_cleanly(1)

    return


def update_component_state(p_app, p_mode, p_ver=None):
    db_local = MY_LITE
    connL = sqlite3.connect(db_local)

    new_state = "Disabled"
    if p_mode == "enable":
        new_state = "Enabled"
    elif p_mode == "install":
        new_state = "Enabled"
    elif p_mode == "remove":
        new_state = "NotInstalled"

    current_state = get_comp_state(p_app)
    ver = ""

    if current_state == new_state:
        return

    if p_mode == "disable" or p_mode == "remove":
        run_script(p_app, "stop-" + p_app, "kill")

    try:
        c = connL.cursor()

        if p_mode in ("enable", "disable"):
            ver = meta.get_version(p_app)
            sql = "UPDATE components SET status = ? WHERE component = ?"
            c.execute(sql, [new_state, p_app])

        if p_mode == "remove":
            ver = meta.get_version(p_app)
            sql = "DELETE FROM components WHERE component = ?"
            c.execute(sql, [p_app])

        if p_mode == "install":
            sql = (
                "INSERT INTO components (component, project, version, platform, port, status) "
                + "SELECT v.component, r.project, v.version, "
                + " CASE WHEN v.platform='' THEN '' ELSE '"
                + get_pf()
                + "' END, p.port, 'Enabled' "
                + "  FROM versions v, releases r, projects p "
                + " WHERE v.component = ? "
                + "   AND v.component = r.component "
                + "   AND r.project = p.project "
                + "   AND v.version = ? "
            )
            if p_ver:
                ver = p_ver
            else:
                ver = meta.get_current_version(p_app)
            c.execute(sql, [p_app, ver])

        connL.commit()
        c.close()
    except Exception as e:
        fatal_sql_error(e, sql, "update_component_state()")

    msg = p_app + " " + new_state
    message(msg, "debug", isJSON)
    return


# MAINLINE ################################################################
cL = sqlite3.connect(MY_LITE, check_same_thread=False)
