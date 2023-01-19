
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

db1 = os.getenv('pgName', '')
if db1 == "":
  db1="postgres"

usr = os.getenv('pgeUser', None)
passwd = os.getenv('pgePasswd', None)
  

def osSys(cmd):
  print('#')
  print('# ' + str(cmd))
  rc = os.system(cmd)
  if rc != 0:
    print("FATAL ERROR running install-pgedge")
    sys.exit(1)

  return


## MAINLINE #####################################################3
rc = os.system("pip3 --version")
if rc != 0:
  print("\n# Trying to install 'pip3'")
  osSys("wget https://bootstrap.pypa.io/get-pip.py")
  osSys("sudo python3 get-pip.py --no-warn-script-location")
  osSys("rm get-pip.py")
  osSys("pip3 install click")

try:
  import fire
except ImportError as e:
  osSys("pip3 install fire")

try:
  import psycopg2
except ImportError as e:
  osSys("pip3 install psycopg2-binary")

print(" ")
print("## Install PgEdge for " + pgV + " #######################################")

if os.path.isdir(pgV):
  print(" ")
  print("# " + pgV + " installation found.")
else:
  osSys("./nc install " + pgV)

svcuser = util.get_user()

osSys("./nc init " + pgV + " --svcuser=" + svcuser)
osSys("./nc config " + pgV + " --autostart=on")
osSys("./nc start " + pgV)

if usr and passwd:
  ncb = './nc pgbin ' + pgN + ' '
  cmd = "CREATE ROLE " + usr + " PASSWORD '" + passwd + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres"') 

  cmd = "createdb '" + db1 + "' --owner='" + usr + "'"
  osSys(ncb  + '"' + cmd + '"')

  ## deterministic shuffle of passwd
  l = list(passwd)
  random.Random(123).shuffle(l)
  rpasswd = ''.join(l)

  cmd = "CREATE ROLE replication WITH SUPERUSER REPLICATION NOLOGIN ENCRYPTED PASSWORD '" + rpasswd + "'"
  osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres"') 
  util.remember_pgpassword(rpasswd, "*", "*", "*", "replication")

osSys("./nc tune " + pgV)

osSys("./nc install spock -d " + db1)

if withPOSTGREST == "True":
  print(" ")
  osSys("./nc install postgrest")

if withBACKREST == "True":
  print(" ")
  osSys("./nc install backrest")

if withBOUNCER == "True":
  print(" ")
  os.system("./nc install bouncer")


