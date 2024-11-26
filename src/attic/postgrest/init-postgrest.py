import os, time
import util

comp = "postgrest"

this_dir = os.path.dirname(os.path.realpath(__file__))

bin_file = this_dir + os.sep + comp
os.system("sudo cp " + bin_file + " /usr/local/bin/.")

svc_file = this_dir + os.sep + 'postgrest.service'
util.replace('USER', util.get_user(), svc_file, True)
util.replace('RST_DIR', this_dir, svc_file, True)
sysd_dir = util.get_systemd_dir()
os.system("sudo cp " + svc_file + "  " + sysd_dir + os.sep + ".")
os.system("sudo systemctl daemon-reload")
os.system("sudo systemctl enable postgrest")

print("Starting Postgrest service")
os.system("sudo systemctl start  postgrest")
util.set_column("autostart", comp, "on")
util.set_column("svcname", comp, comp)

time.sleep(3)
os.system("sudo systemctl status postgrest --lines 25 --full --no-pager")
