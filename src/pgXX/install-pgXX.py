import util
import os, sys

pgver = "pgXX"
thisDir = os.path.dirname(os.path.realpath(__file__))

isAutoStart = str(os.getenv("isAutoStart", "False"))
isFIPS = str(os.getenv("isFIPS", "False"))
isSTART = str(os.getenv("isSTART", "False"))

rc = os.system("grep el8 /etc/os-release > /dev/null 2>&1")
if isFIPS == "True" or rc == 0:
    util.message(" Configuring for FIPS")
    os.system("rm " + thisDir + "/lib/libcrypt*")
    os.system("rm " + thisDir + "/lib/libssl*")

if isSTART == "True":
    util.message("Starting PG with: ")
    MY_CMD = os.getenv("MY_CMD")
    MY_HOME = os.getenv("MY_HOME")
    start_cmd = MY_HOME + os.sep + MY_CMD + " start " + pgver + " -y"
    util.message(start_cmd)
    os.system(start_cmd)
    sys.exit(0)

##if isAutoStart != "True":
##  sys.exit(0)
sys.exit(0)

#########################################################
## AutoStart
#########################################################
svcuser = util.get_user()

util.message("Initializing " + str(pgver) + " as a service to run as " + str(svcuser))
script = thisDir + os.sep + "init-" + pgver + ".py --svcuser=" + str(svcuser)
cmd = sys.executable + " -u " + script
rc = os.system(cmd)

util.message("Configuring " + str(pgver) + " to Autostart")
script = thisDir + os.sep + "config-" + pgver + ".py --autostart=on"
cmd = sys.executable + " -u " + script
rc = os.system(cmd)

util.tune_postgresql_conf(pgver)

##MY_CMD = os.getenv('MY_CMD')
##MY_HOME = os.getenv('MY_HOME')
##install_cmd = MY_HOME + os.sep + MY_CMD + " install "
##
##if os.getenv("isJson"):
##  jflag = " --json"
##else:
##  jflag = ""
##
##os.system(install_cmd + "bouncer" + jflag)
##os.system(install_cmd + "backrest" + jflag)
##os.system(install_cmd + "patroni" + jflag)

util.message("\nStarting " + str(pgver) + " for first time")
script = thisDir + os.sep + "start-" + pgver + ".py"
cmd = sys.executable + " -u " + script
rc = os.system(cmd)

# This script runs after the install script succeeds and
# therefore always has to return "success"
sys.exit(0)
