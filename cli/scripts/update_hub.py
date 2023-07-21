#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, sqlite3, platform
import util

MY_HOME = os.getenv('MY_HOME', '')
NC = MY_HOME + "/nodectl"

rc = 0


################ run_sql() #######################################
def run_sql(cmd):
  global rc 
  try:
    c = cL.cursor()
    c.execute(cmd)
    cL.commit()
    c.close()
  except Exception as e:
    if "duplicate column" not in str(e.args[0]):
      print ("")
      print ("ERROR: " + str(e.args[0]))
      print (cmd)
    rc = 1


#def update_3_3_0():
#  print("")
#  print("## Updating Metadata to 3.3.0 ##################")
#  ## update components table
#  run_sql("ALTER TABLE components ADD COLUMN pidfile TEXT")
#  return


def mainline():
  ## need from_version & to_version
  if len(sys.argv) == 3:
    p_from_ver = sys.argv[1]
    p_to_ver = sys.argv[2]
  else:
    print ("ERROR: Invalid number of parameters, try: ")
    print ("         python update-hub.py from_version  to_version")
    sys.exit(1)

  print ("")
  print ("Running update-hub from v" + p_from_ver + " to v" + p_to_ver)

  if p_from_ver >= p_to_ver:
    print ("Nothing to do.")
    sys.exit(0)

  if (p_from_ver < "23.124") and (p_to_ver >= "23.124"):
    util.echo_cmd(NC + " remove nclibs")
    util.echo_cmd(NC + " install nclibs")

  #if (p_from_ver < "3.3.0") and (p_to_ver >= "3.3.0"):
  #  update_3_3_0()

  sys.exit(rc)
  return


###################################################################
#  MAINLINE
###################################################################
if MY_HOME == '':
  print ("ERROR: Missing MY_HOME envionment variable")
  sys.exit(1)

## gotta have a sqlite database to (possibly) update
db_local = MY_HOME + os.sep + "conf" + os.sep + "db_local.db"
cL = sqlite3.connect(db_local)

if __name__ == '__main__':
   mainline()
