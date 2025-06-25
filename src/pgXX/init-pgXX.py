
####################################################################
######          Copyright (c)  2022-2025 PGEDGE             ##########
####################################################################

import util, startup
import argparse, os, sys, shutil, subprocess, getpass, json

MY_HOME = os.getenv("MY_HOME", "")

sys.path.append(os.path.join(MY_HOME, "hub", "scripts", "lib"))

from ConsoleLogger import ConsoleLogger


def fatal_error(p_msg):
    util.message(p_msg, "error")
    sys.exit(1)
    return


#######################################################
##                     MAINLINE                      ##
#######################################################
pgver = "pgXX"

app_datadir = util.get_comp_datadir(pgver)
update_install_date = False
if app_datadir == "":
    update_install_date = True

parser = argparse.ArgumentParser()
parser.add_argument("--datadir", type=str, default="")
parser.add_argument("--svcuser", type=str, default="")
parser.add_argument("--port", type=int, default=0)
parser.add_argument("--options", type=str, default="")
parser.add_argument("--pwfile", type=str, default="")
args = parser.parse_args()


isSilent = os.getenv("isSilent", None)

## Initialize the ConsoleLogger to redirect the console output log file
previous_stdout = sys.stdout
sys.stdout = ConsoleLogger()

pg_home = os.path.join(MY_HOME, pgver)

util.message("\n## Initializing " + pgver + " #######################")

## PORT ###############################################
if args.port > 0:
    i_port = args.port
else:
    i_port = util.get_avail_port("PG Port", 5432, pgver)

## DATA ###############################################
data_root = os.path.join(MY_HOME, "data")
if not os.path.isdir(data_root):
    os.mkdir(data_root)

if args.datadir == "":
    pg_data = os.path.join(data_root, pgver)
else:
    pg_data = args.datadir

if not os.path.isdir(pg_data):
    os.makedirs(pg_data)

## SVCUSER ###########################################
svcuser = ""
curr_user = ""

svcuser = args.svcuser
if util.is_admin():
    if svcuser == "":
        svcuser = util.get_user()

## PASSWD #############################################
is_password = True
pgpass_file = pg_home + os.sep + ".pgpass"
if args.pwfile:
    pgpass_file = args.pwfile
    if not os.path.isfile(pgpass_file):
        fatal_error("Error: Invalid --pwfile")

if os.path.isfile(pgpass_file):
    is_password = True
    file = open(pgpass_file, "r")
    line = file.readline()
    pg_password = line.rstrip()
    file.close()
else:
    pgePasswd = os.getenv("pgePasswd", "")
    if pgePasswd > "":
        pg_password = util.shuffle_string(pgePasswd)
        file = open(pgpass_file, "w")
        file.write(pg_password + "\n")
        is_password = True
        file.close()

    elif not isSilent:
        pg_password = util.get_superuser_passwd()
        file = open(pgpass_file, "w")
        file.write(pg_password + "\n")
        file.close()
        is_password = True

if is_password:
    os.chmod(pgpass_file, 0o600)

## LOGS ###############################################
data_root_logs = os.path.join(data_root, "logs")
if not os.path.isdir(data_root_logs):
    os.mkdir(data_root_logs)
pg_log = os.path.join(data_root_logs, pgver)
if not os.path.isdir(pg_log):
    os.mkdir(pg_log)

## PERMISSIONS ########################################
##util.message("\nSetting secure directory permissions")
if util.is_admin():
    chown_cmd = "chown " + svcuser + ":" + svcuser
    if not startup.user_exists(svcuser):
        startup.useradd_linux(svcuser)
    os.system(chown_cmd + " " + pg_data)
    os.system(chown_cmd + " " + pgpass_file)
    os.system(chown_cmd + " " + pg_log)
os.chmod(pg_data, 0o600)

logfile = os.path.join(pg_log, "install.log")

## INITDB #############################################
util.message("\nInitializing Postgres DB with:")
initdb_cmd = os.path.join(pg_home, "bin", "initdb")

if args.options == "":
    init_options = "-E UTF8"
    if pgver >= "pg15":
        init_options = init_options + " --data-checksums"
    else:
        init_options = init_options + " --no-locale"

else:
    init_options = args.options

os_user = util.get_user()

# Does the user want to assign a password ?
if is_password:
    batcmd = (
        initdb_cmd
        + " -U "
        + os_user
        + " -A scram-sha-256 "
        + init_options
        + ' -D "'
        + pg_data
        + '" '
        + '--pwfile="'
        + pgpass_file
        + '" > "'
        + logfile
        + '" 2>&1'
    )
else:
    # If not, use -A ident (actually sets peer for local and ident for loopback)
    batcmd = (
        initdb_cmd
        + " -U "
        + os_user
        + " -A ident "
        + init_options
        + ' -D "'
        + pg_data
        + '" '
        + ' > "'
        + logfile
        + '" 2>&1'
    )

##if svcuser > "" and svcuser != curr_user:
##  batcmd = "sudo su - " + svcuser + " -c '" + batcmd + "'"

util.message("  " + batcmd)
err = os.system(batcmd)

if err:
    msg = "ERROR: Unable to Initialize PG. see logfile: " + logfile
    fatal_error(msg)

util.set_column("datadir", pgver, pg_data)
util.set_column("svcuser", pgver, svcuser)
util.set_column("logdir", pgver, pg_log)

util.update_postgresql_conf(pgver, i_port)

if util.get_platform() == "Linux":
    os.system("cp " + pgver + "/genSelfCert.sh " + pg_data + "/.")
    os.system(pg_data + "/genSelfCert.sh")

os.system("cp " + pgver + "/pg_hba.conf.nix " + pg_data + "/pg_hba.conf")

if is_password:
    pg_pass_file = util.remember_pgpassword(pg_password, "*", "*", "*", os_user)
else:
    pg_pass_file = None

util.write_pgenv_file(
    pg_home, pgver, pg_data, os_user, "postgres", str(i_port), pg_pass_file
)

if is_password:
    src_dir = pg_home + os.sep + "init" + os.sep
    os.remove(pgpass_file)

if update_install_date:
    util.update_installed_date(pgver)

if util.is_admin() and util.is_systemctl():
    systemsvc = "pg" + pgver[2:4]
    pg_ctl = os.path.join(MY_HOME, pgver, "bin", "pg_ctl")
    cmd_start = pg_ctl + " start  -D " + pg_data + " -w -t 300"
    cmd_stop = pg_ctl + " stop   -D " + pg_data + " -m fast"
    cmd_reload = pg_ctl + " reload -D " + pg_data
    cmd_status = pg_ctl + " status -D " + pg_data
    cmd_log = "-l " + pg_data + "/pgstartup.log"
    startup.config_linux(
        pgver, systemsvc, svcuser, cmd_start, cmd_log, cmd_stop, cmd_reload, cmd_status)
        ##p_env=f"LD_LIBRARY_PATH={os.path.join(MY_HOME, pgver, 'lib')}"
    util.set_column("svcname", pgver, systemsvc)
    util.set_column("autostart", pgver, "on")
