
import util
import os, sys

thisDir = os.path.dirname(os.path.realpath(__file__))

pgeV="pg15"

withPOSTGREST = str(os.getenv("withPOSTGREST", "False"))
withBACKREST  = str(os.getenv("withBACKREST", "False"))
withBOUNCER   = str(os.getenv("withBOUNCER", "False"))

print(" ")
print("## Install PgEdge for " + pgeV + " #######################################")

os.system("./nc install " + pgeV + " --start ")
os.system("./nc install spock")

print(" ")
os.system("./nc tune " + pgeV)

if withPOSTGREST == "True":
  print(" ")
  os.system("./nc install postgrest")

if withBACKREST == "True":
  print(" ")
  os.system("./nc install backrest")

if withBOUNCER == "True":
  print(" ")
  os.system("./nc install bouncer")


