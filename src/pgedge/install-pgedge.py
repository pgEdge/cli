
import util
import os, sys, random

thisDir = os.path.dirname(os.path.realpath(__file__))

pgN = os.getenv('pgN', '')
if pgN == "":
  pgN = "15"
pgV = "pg" + pgN

withPOSTGREST = str(os.getenv("withPOSTGREST", "False"))
withBACKREST  = str(os.getenv("withBACKREST",  "False"))
withBOUNCER   = str(os.getenv("withBOUNCER",   "False"))
isAutoStart   = str(os.getenv("isAutoStart",   "False"))


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    os.system("./nc remove pgedge")
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

  util.message("  Verifying POSIX")
  if platf != "Linux" and platf != "Darwin":
    error_exit("OS must be POSIX")

  if platf == "Linux":
    util.message("  Verifying Linux supported glibc version")
    if util.get_glibc_version() < "2.28":
      error_exit("Linux has unsupported (old) version of glibc")

  if platf == "Darwin":
    util.message("  Verifying Autostart")
    if isAutoStart == "True":
      error_exit("Autostart is NOT supported on macOS")

  util.message("  Verifying Python 3.6+")
  p3_minor_ver = util.get_python_minor_version()
  if p3_minor_ver < 6:
    error_exit("Python Version must be greater than 3.6")

  util.message("  Verifying non-root user for pg install")
  if util.is_admin():
    error_exit("You must install as non-root user with passwordless sudo privleges")

  util.message("  Verifying port " + str(prt) + " availability")
  if util.is_socket_busy(prt):
    error_exit("Port " + str(prt) + " is busy")

  data_dir = "data/" + pgV
  util.message("  Verifying empty data directory '" + data_dir + "'")
  if os.path.exists(data_dir):
    dir = os.listdir(data_dir)
    if len(dir) != 0:
      error_exit("The '" + data_dir + "' directory is not empty")

  if usr:
    util.message("  Verifying -U usr & -P passwd...")
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
  os.system("pip3 install click --user >/dev/null 2>&1")
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

  util.message("  Ensure FIRE pip3 module")
  try:
    import fire
  except ImportError as e:
    osSys("pip3 install fire --user --upgrade", False)

  util.message("  Ensure PSYCOPG-BINARY pip3 module")
  try:
    import psycopg
  except ImportError as e:
    osSys("pip3 install psycopg-binary --user --upgrade", False)

  util.message("  Ensure PSUTIL pip3 module")
  try:
    import psutil
  except ImportError as e:
    osSys("pip3 install psutil --user --upgrade", False)


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

osSys("./nc install " + pgV)

if util.is_empty_writable_dir("/data") == 0:
  util.message("## symlink empty local data directory to empty /data ###")
  osSys("rm -rf data; ln -s /data data")

osSys("./nc init " + pgV + " --port=" + str(prt))

if isAutoStart == "True":
  util.message("\n## init & config autostart  ###############")
  osSys("./nc init " + pgV + " --svcuser=" + svcuser)
  osSys("./nc config " + pgV + " --autostart=on")

osSys("./nc start " + pgV)

if usr and passwd:
  ncb = './nc pgbin ' + pgN + ' '
  cmd = "CREATE ROLE " + usr + " PASSWORD '" + passwd + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null') 

  cmd = "createdb '" + db1 + "' --owner='" + usr + "'"
  osSys(ncb  + '"' + cmd + '"')

osSys("./nc tune " + pgV)

osSys("./nc install spock -d " + db1)

if withPOSTGREST == "True":
  util.message("  ")
  osSys("./nc install postgrest")

if withBACKREST == "True":
  util.message("  ")
  osSys("./nc install backrest")

if withBOUNCER == "True":
  util.message("  ")
  os.system("./nc install bouncer")


