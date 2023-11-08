import util 

comp = "firewalld"

util.echo_cmd(f"sudo systemctl start {comp}")

