import os
import component, util, startup 

comp = "bouncer"

MY_HOME = os.getenv('MY_HOME')
ini_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'pgbouncer.ini'
util.replace('MY_HOME', MY_HOME, ini_file, True)
component.init_comp(comp, 'pgbouncer.pid')

cmd = MY_HOME + os.sep + os.getenv("MY_CMD", "nc")
if os.getenv("isAutoStart", "") == "True":
  this_dir = os.path.dirname(os.path.realpath(__file__))
  svc_file = this_dir + os.sep + 'bouncer.service'
  util.replace('USER', util.get_user(), svc_file, True)
  util.replace('BOUNCE_DIR', this_dir, svc_file, True)
  sysd_dir = util.get_systemd_dir()
  os.system("sudo cp " + svc_file + "  " + sysd_dir + os.sep + ".")
  os.system("sudo systemctl daemon-reload")
  os.system("sudo systemctl enable bouncer")
  os.system("sudo systemctl start  bouncer")
  util.set_column("autostart", comp, "on")
  util.set_column("svcname", comp, comp)
