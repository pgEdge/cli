import os
import component, util, startup 

comp = "postgrest"
autostart =  util.get_column("autostart", comp)
if autostart == "on":
  os.system("sudo systemctl stop    postgrest")
  os.system("sudo systemctl disable postgrest")

  sysd_dir = util.get_systemd_dir()
  os.system("sudo rm -f " + sysd_dir + os.sep + "postgrest.service")

  os.system("sudo systemctl daemon-reload")

