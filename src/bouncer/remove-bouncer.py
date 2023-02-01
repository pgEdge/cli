import os
import component, util, startup 

comp = "bouncer"
autostart =  util.get_column("autostart", comp)
if autostart == "on":
  os.system("sudo systemctl stop    bouncer")
  os.system("sudo systemctl disable bouncer")

  sysd_dir = util.get_systemd_dir()
  os.system("sudo rm -f " + sysd_dir + os.sep + "bouncer.service")

  os.system("sudo systemctl daemon-reload")

