
import util
import os, sys, random, subprocess

thisDir = os.path.dirname(os.path.realpath(__file__))
homeDir = os.getcwd()

print(f"DEBUG:  cwd={os.getcwd()}")
print(f"DEBUG: thisDir={thisDir}")

pgV="pg15"
if not os.path.isdir(pgV):
  print("installing " + pgV + " as a pre-req")
  os.system("./nc install " + pgV + " --start")

os.chdir(thisDir)

os.system("rm -r lib")
os.system("rm -r share")

os.system("sudo cp bin/pgbackrest  /usr/bin/.")
os.system("sudo chmod 755 /usr/bin/pgbackrest")
os.system("sudo mkdir -p -m 770 /var/log/pgbackrest")

usrUsr = util.get_user() + ":" + util.get_user()

os.system("sudo chown " + usrUsr + " /var/log/pgbackrest")
os.system("sudo mkdir -p /etc/pgbackrest")
os.system("sudo mkdir -p /etc/pgbackrest/conf.d")
os.system("sudo touch /etc/pgbackrest/pgbackrest.conf")
os.system("sudo chmod 640 /etc/pgbackrest/pgbackrest.conf")
os.system("sudo chown " + usrUsr + " /etc/pgbackrest/pgbackrest.conf")

os.system("sudo mkdir -p /var/lib/pgbackrest")
os.system("sudo chmod 750 /var/lib/pgbackrest")
os.system("sudo chown " + usrUsr + " /var/lib/pgbackrest")

dataDir= os.getenv("MY_HOME") + "/data/pg15"

conf_file=thisDir + "/pgbackrest.conf"
util.replace("pgXX", pgV, conf_file, True)
util.replace("pg1-path=xx", "pg1-path=" + dataDir, conf_file, True)

bCipher = subprocess.check_output("dd if=/dev/urandom bs=256 count=1 2> /dev/null | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c32", shell=True)
sCipher = bCipher.decode('ascii')
util.replace("repo1-cipher-pass=xx", "repo1-cipher-pass=" + sCipher, conf_file, True)

aCmd = "pgbackrest --stanza=" + pgV + " archive-push %p"
util.change_pgconf_keyval(pgV, "archive_command", aCmd)
util.change_pgconf_keyval(pgV, "archive_mode", "on", p_replace=True)

os.system("cp " + conf_file + "  /etc/pgbackrest/.")

