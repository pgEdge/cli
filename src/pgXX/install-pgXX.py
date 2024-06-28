import util
import os, sys

pgver = "pgXX"
thisDir = os.path.dirname(os.path.realpath(__file__))

isAutoStart = str(os.getenv("isAutoStart", "False"))
isFIPS = str(os.getenv("isFIPS", "False"))
isSTART = str(os.getenv("isSTART", "False"))

rc8 = os.system("grep el8 /etc/os-release > /dev/null 2>&1")
rc9 = os.system("grep el9 /etc/os-release > /dev/null 2>&1")
rc = rc8 + rc9
if isFIPS == "True" or rc == 1:
    util.message(" Configuring for FIPS")
    os.system("rm " + thisDir + "/lib/libcrypt*")
    os.system("rm " + thisDir + "/lib/libssl*")

if isAutoStart == "True":
    util.autostart_verify_prereqs()
    util.autostart_config("pgXX")
    isSTART = "True"

if isSTART == "True":
    MY_CMD = os.getenv("MY_CMD")
    MY_HOME = os.getenv("MY_HOME")
    start_cmd = MY_HOME + os.sep + MY_CMD + " start " + pgver + " -y"
    util.osSys(start_cmd)
    sys.exit(0)

