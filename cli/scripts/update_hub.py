
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, sys, sqlite3, platform
import util

MY_HOME = os.getenv("MY_HOME", "")
CTL = MY_HOME + "/ctl"

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
        p_from_ver = sys.argv[1]
        p_to_ver = sys.argv[2]
    else:
        print("ERROR: Invalid number of parameters, try: ")
        print("         python update-hub.py from_version  to_version")
        sys.exit(1)

    print("")
    print("Running update-hub from v" + p_from_ver + " to v" + p_to_ver)

    if p_from_ver >= p_to_ver:
        print("Nothing to do.")
        sys.exit(0)

    if (p_from_ver < "24.1.1"):
        util.echo_cmd(CTL + " remove ctlibs")
        util.echo_cmd(CTL + " install ctlibs")

    sys.exit(rc)
    return


#  MAINLINE ###########################
if MY_HOME == "":
    print("ERROR: Missing MY_HOME envionment variable")
    sys.exit(1)

# gotta have a sqlite database to (possibly) update
cL = sqlite3.connect(os.getenv("MY_LITE"))

if __name__ == "__main__":
    mainline()
