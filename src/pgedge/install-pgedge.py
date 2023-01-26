
import util
import os, sys, random

thisDir = os.path.dirname(os.path.realpath(__file__))

pgN = os.getenv('pgN', '')
if pgN == "":
  pgN = "15"
pgV = "pg" + pgN

withPOSTGREST = str(os.getenv("withPOSTGREST", "False"))
withBACKREST  = str(os.getenv("withBACKREST", "False"))
withBOUNCER   = str(os.getenv("withBOUNCER", "False"))
isAutoStart   = str(os.getenv("isAutoStart", "False"))

db1 = os.getenv('pgName', '')
if db1 == "":
  db1="postgres"

usr = os.getenv('pgeUser', None)
passwd = os.getenv('pgePasswd', None)


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    os.system("./nc remove pgedge")
    sys.exit(p_rc)


def osSys(cmd):
  isSilent = os.getenv('isSilent', 'False')
  if isSilent == "False":
    s_cmd = util.scrub_passwd(cmd)
    util.message('#')
    util.message('# ' + str(s_cmd))

  rc = os.system(cmd)
  if rc != 0:
    error_exit("FATAL ERROR running install-pgedge", 1)

  return


## MAINLINE #####################################################3

svcuser = util.get_user()

if util.is_admin():
  error_exit("You must install as non-root user with passwordless sudo privleges", 1)

if util.is_socket_busy(5432):
  error_exit("Postgres already running on port 5432", 1)

data_dir = "data/" + pgV
if os.path.exists(data_dir):
  dir = os.listdir(data_dir)
  if len(dir) != 0:
    error_exit("The '" + data_dir + "' directory is not empty", 1)

rc = os.system("pip3 --version > /dev/null")
if rc != 0:
  util.message("\n# Trying to install 'pip3'")
  osSys("wget https://bootstrap.pypa.io/get-pip.py")
  osSys("sudo python3 get-pip.py --no-warn-script-location")
  osSys("rm get-pip.py")
  os.system("pip3 install click")

try:
  import fire
except ImportError as e:
  osSys("pip3 install fire")

try:
  import psycopg2
except ImportError as e:
  osSys("pip3 install psycopg2-binary")

osSys("./nc install " + pgV)


##if os.path.isdir("/data"):
##  util.message("\n## /data directory found ###################")
##else:
##  util.message("\n## creating /data directory ################")
##  osSys("sudo mkdir /data")
##  osSys("sudo chown " + svcuser + ":" + svcuser + " /data")
##
##util.message("\n## symlink local data directory to /data ###")
##osSys("cp -r  data/* /data/.")
##osSys("rm -rf data")
##osSys("ln -s /data data")

if isAutoStart == "True":
  util.message("\n## init & config autostart  ###############")
  osSys("./nc init " + pgV + " --svcuser=" + svcuser)
  osSys("./nc config " + pgV + " --autostart=on")

osSys("./nc start " + pgV)

if usr and passwd:
  util.message("\n## creating roles & database ##############")
  ncb = './nc pgbin ' + pgN + ' '
  cmd = "CREATE ROLE " + usr + " PASSWORD '" + passwd + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null') 

  cmd = "createdb '" + db1 + "' --owner='" + usr + "'"
  osSys(ncb  + '"' + cmd + '"')

  #### deterministic shuffle of passwd
  ##l = list(passwd)
  ##random.Random(123).shuffle(l)
  ##rpasswd = ''.join(l)
  ##
  ##cmd = "CREATE ROLE replication WITH SUPERUSER REPLICATION NOLOGIN ENCRYPTED PASSWORD '" + rpasswd + "'"
  ##osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null') 
  ##util.remember_pgpassword(rpasswd, "*", "*", "*", "replication")

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


