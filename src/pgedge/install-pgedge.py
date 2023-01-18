
import util
import os, sys

thisDir = os.path.dirname(os.path.realpath(__file__))
pgeV="pg15"

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
print("## Install PgEdge for " + pgeV + " #######################################")

if os.path.isdir(pgeV):
  print(" ")
  print("# " + pgeV + " installation found.")
else:
  osSys("./nc install " + pgeV)

svcuser = util.get_user()

osSys("./nc init pg15 --svcuser=" + svcuser)
osSys("./nc config pg15 --autostart=on")
osSys("./nc start " + pgeV)

if usr and passwd:
  cmd = "CREATE ROLE " + usr + " PASSWORD '" + passwd + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  osSys('./nc pgbin 15 "psql -c \\"' + cmd + '\\" postgres"') 

  cmd = "createdb '" + db1 + "' --owner='" + usr + "'"
  osSys('./nc pgbin 15 "' + cmd + '"')

osSys("./nc tune " + pgeV)

osSys("./nc install spock -d " + db1)

if withPOSTGREST == "True":
  print(" ")
  osSys("./nc install postgrest" + db1)

if withBACKREST == "True":
  print(" ")
  osSys("./nc install backrest" + db1)

if withBOUNCER == "True":
  print(" ")
  os.system("./nc install bouncer" + db1)


