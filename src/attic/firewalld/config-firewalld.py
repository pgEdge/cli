import os
import component, util, startup 

comp = "firewalld"

MY_HOME = os.getenv('MY_HOME')

cmd = MY_HOME + os.sep + os.getenv("MY_CMD", "nc")

util.echo_cmd(f"sudo dnf -y install {comp}")
util.echo_cmd(f"sudo systemctl enable {comp}") 
util.echo_cmd(f"sudo systemctl start {comp}")
util.echo_cmd(f"sudo systemctl status {comp}")

util.set_column("autostart", comp, "on")
util.set_column("svcname", comp, comp)
