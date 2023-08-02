
import util
import os, sys, random, subprocess, time

thisDir = os.path.dirname(os.path.realpath(__file__))

def osSys(p_input, p_display=True):
  if p_display:
    util.message("# " + p_input)
  rc = os.system(p_input)
  return(rc)

#### MAINLINE #####################################

if os.path.isdir("/var/lib/pgbackrest"):
  util.message("ERROR: '/var/lib/pgbackrest' directory already exists")
  osSys("./nc remove backrest")
  sys.exit(1)

pgV = ""
if os.path.isdir("pg15"):
  pgV = "pg15"
elif os.path.isdir("pg16"):
  pgV = "pg16"

if pgV == "":
  util.exit_message("pg15+ must be installed")

os.chdir(thisDir)
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

## cleanup cruft
osSys("rm -r lib", False)
osSys("rm -r share", False)

util.message("\n## creating /usr/bin/pgbackrest link #################")
osSys("sudo rm -f /usr/bin/pgbackrest")
osSys("sudo ln -s " + thisDir + "/bin/pgbackrest /usr/bin/pgbackrest")
osSys("sudo chmod 755 /usr/bin/pgbackrest")

osSys("sudo mkdir -p -m 770 /var/log/pgbackrest")

util.message("\n## creating '/etc/pgbackrest/pgbackrest.conf' ########")
osSys("sudo chown " + usrUsr + " /var/log/pgbackrest")
osSys("sudo mkdir -p /etc/pgbackrest")
osSys("sudo mkdir -p /etc/pgbackrest/conf.d")
osSys("sudo touch /etc/pgbackrest/pgbackrest.conf")
osSys("sudo chmod 640 /etc/pgbackrest/pgbackrest.conf")
osSys("sudo chown " + usrUsr + " /etc/pgbackrest/pgbackrest.conf")

osSys("sudo mkdir -p /var/lib/pgbackrest")
osSys("sudo chmod 750 /var/lib/pgbackrest")
osSys("sudo chown " + usrUsr + " /var/lib/pgbackrest")

dataDir= os.getenv("MY_HOME") + "/data/" + pgV

util.message("\n## creating '/etc/pgbackrest/pgbackrest.conf' ########")
conf_file=thisDir + "/pgbackrest.conf"
util.replace("pgXX", pgV, conf_file, True)
util.replace("pg1-path=xx", "pg1-path=" + dataDir, conf_file, True)
util.replace("pg1-user=xx", "pg1-user=" + osUsr, conf_file, True)
util.replace("pg1-database=xx", "pg1-database=" + "postgres", conf_file, True)

cmd="dd if=/dev/urandom bs=256 count=1 2> /dev/null | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c32"
bCipher = subprocess.check_output(cmd, shell=True)
sCipher = bCipher.decode('ascii')
util.replace("repo1-cipher-pass=xx", "repo1-cipher-pass=" + sCipher, conf_file, True)
osSys("cp " + conf_file + "  /etc/pgbackrest/.")

stanza = "--stanza=" + pgV + " "
util.message("\n## Modify 'postgresql.conf' #########################")
aCmd = "pgbackrest " + stanza + " archive-push %p"
util.change_pgconf_keyval(pgV, "archive_command", aCmd, p_replace=True)
util.change_pgconf_keyval(pgV, "archive_mode", "on", p_replace=True)

osSys("../nc restart " + pgV)
time.sleep(3)

osSys("pgbackrest stanza-create " + stanza)
osSys("pgbackrest check " + stanza)
