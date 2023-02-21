
import util, fire
import os, sys, random, time

#thisDir = os.path.dirname(os.path.realpath(__file__))
nc = "./nodectl "

#pgN = os.getenv('pgN', '')
#if pgN == "":
#  pgN = "15"
#pgV = "pg" + pgN
#

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


def install(User=None, Password=None, database=None, country=None, port=5432, pgV="pg15",
            autostart=True, with_bouncer=False, with_backrest=False, with_postgrest=False):
  """Install pgEdge components"""

  pgeUser = os.getenv('pgeUser', None)
  if not User and pgeUser:
    User = pgeUser
  else:
    User = str(User)

  pgePasswd = os.getenv('pgePasswd', None)
  if not Password and pgePasswd:
    Password = pgePasswd
  else:
    Password = str(Password)

  pgName = os.getenv('pgName', None)
  if not database and pgName:
    database = pgName

  pgeCountry = os.getenv('pgeCountry', None)
  if not country and pgeCountry:
    country = pgeCountry
  else
    country = str(country)

  try:
    pgePort = int(os.getenv('pgePort', '5432'))
  except Exception as e:
    error_exit("Port " + os.getenv('pgePort') + " is not an integer")
  if not port and pgePort != 5432:
    port = pgePort

  if util.get_platform() == "Darwin":
    if isAutoStart == "True":
      util.message("--autostart is ignored on macOS")
      autostart = False

  print(f"User={User}, Password={Password}, database={database}, country={country}, port={port}")
  print(f"autostart={autostart}, with_bouncer={with_bouncer}")

  database = str(database)
  country = str(country)
  try:
    port = int(port)
  except Exception as e:
    error_exit("The port must be an integer")

  pgV = str(pgV)
  #print(f"pgN = {pgV[2:]} pg = {pgV[:2]}")
  if pgV[:2] != "pg":
    error_exit("pgV parm must start with 'pg'")
  try:
    pgN = int(pgV[2:])
  except Exception as e:
    error_exit("pgV parm must end with a two digit integer")

  if User == None and Password == None:
    pass
  elif User and Password:
    pass
  else:
    error_exit("The User and Password must be specified as a pair")

  if User:
    util.message("  Verify -U user & -P password...")

    usr_l = User.lower()
    if usr_l == "pgedge":
      error_exit("The user defined supersuser may not be called 'pgedge'")

    if usr_l == util.get_user():
      error_exit("The user-defined superuser may not be the same as the OS user")

    usr_len = len(usr_l)
    if (usr_len < 2) or (usr_len > 64):
      error_exit("The user-defined superuser must be >=1 and <= 64 in length")

    if str(usr_l[0]).isnumeric():
      error_exit("The user may not start with a numeric character")

  if Password:
    pwd_len = len(Password)
    if (pwd_len < 6) or (pwd_len > 128):
      error_exit("The password must be >= 6 and <= 128 in length")

    for pwd_char in Password:
      pwd_c = pwd_char.strip()
      if pwd_c in (",", "'", '"', "@", ""):
        error_exit("The password must not contain ',', \"'\", \", @, or a space")

  if util.is_socket_busy(port):
    error_exit("Port " + str(port) + " is busy")

  osSys(nc + "install " + pgV)

  if util.is_empty_writable_dir("/data") == 0:
    util.message("## symlink empty local data directory to empty /data ###")
    osSys("rm -rf data; ln -s /data data")

  if autostart:
    util.message("\n## init & config autostart  ###############")
    osSys(nc + "init " + pgV + " --svcuser=" + util.get_user())
    osSys(nc + "config " + pgV + " --autostart=on")
  else:
    osSys(nc + "init " + pgV)

  osSys(nc + "config " + pgV + " --port=" + str(port))

  osSys(nc + "start " + pgV)
  time.sleep(3)

  if User and Password:
    ncb = nc + 'pgbin ' + str(pgN) + ' '
    cmd = "CREATE ROLE " + User + " PASSWORD '" + Password + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
    osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null')

    cmd = "createdb '" + database + "' --owner='" + User + "'"
    osSys(ncb  + '"' + cmd + '"')

  osSys(nc + "tune " + pgV)
  time.sleep(3)

  osSys(nc + "install spock -d " + database)


def remove(rm_data=False):
  """Remove pgEdge components"""
  pass


def tune(component="pg15"):
  """Tune pgEdge components"""

  if not os.path.isdir(component):
    util.exit_message(f"{component} is not installed", 1)

  rc = os.system("./nodectl tune " + component)
  return(rc)


def pre_reqs(port=5432):
  """Check Pre Requisites for installing pgEdge"""

  util.message("#### Checking for Pre-Req's #########################")
  platf = util.get_platform()

  util.message("  Ensure CLICK pip3 module")
  try:
    import click
  except Exception as e:
    error_exit("You must 'pip3 install click' before running this installer further")

  util.message("  Verify Linux or macOS")
  if platf != "Linux" and platf != "Darwin":
    error_exit("OS must be Linux or macOS")

  if platf == "Linux":
    util.message("  Verify Linux supported glibc version")
    if util.get_glibc_version() < "2.28":
      error_exit("Linux has unsupported (older) version of glibc")

  util.message("  Verify Python 3.6+")
  p3_minor_ver = util.get_python_minor_version()
  if p3_minor_ver < 6:
    error_exit("Python version must be greater than 3.6")

  util.message("  Verify non-root user")
  if util.is_admin():
    error_exit("You must install as non-root user with passwordless sudo privleges")

  data_dir = "data/" + pgV
  util.message("  Verify empty data directory '" + data_dir + "'")
  if os.path.exists(data_dir):
    dir = os.listdir(data_dir)
    if len(dir) != 0:
      error_exit("The '" + data_dir + "' directory is not empty")

  util.message("  Ensure recent pip3")
  rc = os.system("pip3 --version >/dev/null 2>&1")
  if rc == 0:
    os.system("pip3 install --upgrade pip --user")
  else:
    url="https://bootstrap.pypa.io/get-pip.py"
    if p3_minor_ver == 6:
      url="https://bootstrap.pypa.io/pip/3.6/get-pip.py"
    util.message("\n# Trying to install 'pip3'")
    osSys("rm -f get-pip.py", False)
    osSys("curl -O " + url, False)
    osSys("python3 get-pip.py --user", False)
    osSys("rm -f get-pip.py", False)

  ##util.message("  Ensure FIRE pip3 module")
  ##try:
  ##  import fire
  ##except ImportError as e:
  ##  osSys("pip3 install fire --user --upgrade", False)

  util.message("  Ensure PSYCOPG-BINARY pip3 module")
  try:
    import psycopg
  except ImportError as e:
    osSys("pip3 install psycopg-binary --user --upgrade", False)

  util.message("  Check PSUTIL module")
  try:
    import psutil
  except ImportError as e:
    util.message("  You need a native PSUTIL module to run 'metrics-check' or 'top'")


if __name__ == '__main__':
  fire.Fire({
    'pre-reqs':pre_reqs,
    'install':install,
    'tune':tune,
    'remove':remove,
  })

