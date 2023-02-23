
import util
import os, sys, random, time

thisDir = os.path.dirname(os.path.realpath(__file__))
nc = "./nodectl "

pgN = os.getenv('pgN', '')
if pgN == "":
  pgN = "15"
pgV = "pg" + pgN

withPOSTGREST = str(os.getenv("withPOSTGREST", "False"))
withBACKREST  = str(os.getenv("withBACKREST",  "False"))
withBOUNCER   = str(os.getenv("withBOUNCER",   "False"))
isAutoStart   = str(os.getenv("isAutoStart",   "False"))
isDebug       = str(os.getenv("pgeDebug",      "0"))


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    if isDebug == "0":
      os.system(nc + "remove pgedge")

    sys.exit(p_rc)


def osSys(cmd, fatal_exit=True):
  isSilent = os.getenv('isSilent', 'False')
  if isSilent == "False":
    s_cmd = util.scrub_passwd(cmd)
    util.message('#')
    util.message('# ' + str(s_cmd))

  rc = os.system(cmd)
  if rc != 0 and fatal_exit:
    error_exit("FATAL ERROR running install-pgedge", 1)

  return


def check_pre_reqs():
  util.message("#### Checking for Pre-Req's #########################")
  platf = util.get_platform()

  util.message("  Verify Linux or macOS")
  if platf != "Linux" and platf != "Darwin":
    error_exit("OS must be Linux or macOS")

  if platf == "Linux":
    util.message("  Verify Linux supported glibc version")
    if util.get_glibc_version() < "2.28":
      error_exit("Linux has unsupported (older) version of glibc")

  if platf == "Darwin":
    util.message("  Verify autostart not set for macOS")
    if isAutoStart == "True":
      error_exit("autostart is NOT supported on macOS")

  util.message("  Verify Python 3.6+")
  p3_minor_ver = util.get_python_minor_version()
  if p3_minor_ver < 6:
    error_exit("Python version must be greater than 3.6")

  util.message("  Verify non-root user")
  if util.is_admin():
    error_exit("You must install as non-root user with passwordless sudo privleges")

  util.message("  Verify port " + str(prt) + " availability")
  if util.is_socket_busy(prt):
    error_exit("Port " + str(prt) + " is busy")

  data_dir = "data/" + pgV
  util.message("  Verify empty data directory '" + data_dir + "'")
  if os.path.exists(data_dir):
    dir = os.listdir(data_dir)
    if len(dir) != 0:
      error_exit("The '" + data_dir + "' directory is not empty")

  if usr:
    util.message("  Verify -U usr & -P passwd...")
    usr_l = usr.lower()
    if usr_l == "pgedge":
      error_exit("The user defined supersuser may not be called 'pgedge'")

    if usr_l == util.get_user():
      error_exit("The user-defined superuser may not be the same as the OS user")

    usr_len = len(usr_l)
    if (usr_len < 1) or (usr_len > 64):
      error_exit("The user-defined superuser must be >=1 and <= 64 in length")

    if passwd:
      pwd_len = len(passwd)
      if (pwd_len < 8) or (pwd_len > 128):
        error_exit("The password must be >= 8 and <= 128 in length")

      for pwd_char in passwd:
        pwd_c = pwd_char.strip()
        if pwd_c in (",", "'", '"', "@", ""):
          error_exit("The password must not contain {',', \"'\", \", @, or a space")

    else:
      error_exit("Must specify a -P passwd when specifying a -U usr")

  util.message("  Ensure recent pip3")
  rc = os.system("pip3 --version >/dev/null 2>&1")
  if rc == 0:
    os.system("pip3 install --upgrade pip --user >/dev/null 2>&1")
  else:
    url="https://bootstrap.pypa.io/get-pip.py"
    if p3_minor_ver == 6:
      url="https://bootstrap.pypa.io/pip/3.6/get-pip.py"
    util.message("\n# Trying to install 'pip3'")
    osSys("rm -f get-pip.py", False)
    osSys("curl -O " + url, False)
    osSys("python3 get-pip.py --user", False)
    osSys("rm -f get-pip.py", False)

  util.message("  Ensure PSYCOPG-BINARY pip3 module")
  try:
    import psycopg
  except ImportError as e:
    osSys("pip3 install psycopg-binary --user --upgrade", False)

  util.message("  Check for PSUTIL module")
  try:
    import psutil
  except ImportError as e:
    util.message("  You need a native PSUTIL module to run 'metrics-check' or 'top'")


## MAINLINE #####################################################3

svcuser = util.get_user()

db1 = os.getenv('pgName', '')
if db1 == "":
  db1="postgres"

usr = os.getenv('pgeUser', None)
passwd = os.getenv('pgePasswd', None)
prt = 0
try:
  prt = int(os.getenv('pgePort', '5432'))
except Exception as e:
  error_exit("Port " + os.getenv('pgePort') + " is not an integer")

check_pre_reqs()

osSys(nc + "install " + pgV)

if util.is_empty_writable_dir("/data") == 0:
  util.message("## symlink empty local data directory to empty /data ###")
  osSys("rm -rf data; ln -s /data data")

if isAutoStart == "True":
  util.message("\n## init & config autostart  ###############")
  osSys(nc + "init " + pgV + " --svcuser=" + svcuser)
  osSys(nc + "config " + pgV + " --autostart=on")
else:
  osSys(nc + "init " + pgV)

osSys(nc + "config " + pgV + " --port=" + str(prt))

osSys(nc + "start " + pgV)
time.sleep(3)

if usr and passwd:
  ncb = nc + 'pgbin ' + pgN + ' '
  cmd = "CREATE ROLE " + usr + " PASSWORD '" + passwd + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null') 

  cmd = "createdb '" + db1 + "' --owner='" + usr + "'"
  osSys(ncb  + '"' + cmd + '"')

osSys(nc + "tune " + pgV)
time.sleep(3)

osSys(nc + "install spock -d " + db1)

if withPOSTGREST == "True":
  util.message("  ")
  osSys(nc + "install postgrest")

if withBACKREST == "True":
  util.message("  ")
  osSys(nc + "install backrest")

if withBOUNCER == "True":
  util.message("  ")
  os.system(nc + "install bouncer")


