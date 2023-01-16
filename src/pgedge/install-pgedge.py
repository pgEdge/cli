
import util
import os, sys

thisDir = os.path.dirname(os.path.realpath(__file__))
pgeV="pg15"

withPOSTGREST = str(os.getenv("withPOSTGREST", "False"))
withBACKREST  = str(os.getenv("withBACKREST", "False"))
withBOUNCER   = str(os.getenv("withBOUNCER", "False"))


def osSys(cmd):
  print('#')
  print('# ' + str(cmd))
  rc = os.system(cmd)
  return(rc)


## MAINLINE #####################################################3
rc = os.system("pip3 --version")
if rc != 0:
  print("\n# Trying to install 'pip3'")
  osSys("wget https://bootstrap.pypa.io/get-pip.py")
  osSys("sudo python3 get-pip.py --no-warn-script-location")

try:
  import fire
except ImportError as e:
  osSys("pip3 install fire --no-warn-script-location")

try:
  import psycopg2
except ImportError as e:
  osSys("pip3 install psycopg2-binary --no-warn-script-location")

print(" ")
print("## Install PgEdge for " + pgeV + " #######################################")

if os.path.isdir(pgeV):
  print(" ")
  print("# " + pgeV + " installation found.")
else:
  osSys("./nc install " + pgeV)

osSys("./nc start " + pgeV)
osSys("./nc tune " + pgeV)

db1 = os.getenv('pgName', '')
if db1 > '':
  db1 = " -d " + db1

osSys("./nc install spock" + db1)

if withPOSTGREST == "True":
  print(" ")
  osSys("./nc install postgrest" + db1)

if withBACKREST == "True":
  print(" ")
  osSys("./nc install backrest" + db1)

if withBOUNCER == "True":
  print(" ")
  os.system("./nc install bouncer" + db1)


