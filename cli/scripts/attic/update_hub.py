
#  Copyright 2022-2025 PGEDGE  All rights reserved. #

import os, sys, sqlite3
import util
from semantic_version import Version

MY_HOME = os.getenv("MY_HOME", "")
CTL = MY_HOME + "/pgedge"

rc = 0



def run_sql(cmd):
    global rc
    try:
        c = cL.cursor()
        c.execute(cmd)
        cL.commit()
        c.close()
    except Exception as e:
        if "duplicate column" not in str(e.args[0]):
            print("")
            print("ERROR: " + str(e.args[0]))
            print(cmd)
        rc = 1


def mainline():
    # need from_version & to_version
    if len(sys.argv) == 3:
        p_from_ver = Version.coerce(sys.argv[1])
        p_to_ver = Version.coerce(sys.argv[2])
    else:
        print("ERROR: Invalid number of parameters, try: ")
        print("         python3 update-hub.py  from_version  to_version")
        sys.exit(1)

    print(f"\nRunning update-hub from v{p_from_ver} to v{p_to_ver}")

    if p_from_ver >= p_to_ver:
        print("Nothing to do.")
        sys.exit(0)

    util.echo_cmd(f"cp {MY_HOME}/hub_new/hub/scripts/sh/cli.sh {MY_HOME}/pgedge")
   
    sys.exit(0)
    return


#  MAINLINE ###########################
if MY_HOME == "":
    print("ERROR: Missing MY_HOME environment variable")
    sys.exit(1)

# gotta have a sqlite database to (possibly) update
cL = sqlite3.connect(os.getenv("MY_LITE"))

if __name__ == "__main__":
    mainline()
