import os
import component, util, startup 

comp = "postgrest"

MY_HOME = os.getenv('MY_HOME')
cmd = MY_HOME + os.sep + os.getenv("MY_CMD", "nc")

if os.getenv("isAutoStart", "") == "True":
  this_dir = os.path.dirname(os.path.realpath(__file__))
  svc_file = this_dir + os.sep + 'postgrest.service'
  util.replace('USER', util.get_user(), svc_file, True)
  util.replace('RST_DIR', this_dir, svc_file, True)
  sysd_dir = util.get_systemd_dir()
  os.system("sudo cp " + svc_file + "  " + sysd_dir + os.sep + ".")
  os.system("sudo systemctl daemon-reload")
  os.system("sudo systemctl enable postgrest")
  os.system("sudo systemctl start  postgrest")
  util.set_column("autostart", comp, "on")
  util.set_column("svcname", comp, comp)
