#!/usr/bin/env python3
# Copyright (c) 2022-2024 PGEDGE

import os
import subprocess
import socket
import util

thisDir = os.path.dirname(os.path.realpath(__file__))

# Function to execute system commands
def osSys(p_input, p_display=True):
    if p_display:
        print("# " + p_input)
    subprocess.run(p_input.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to create a symbolic link
def create_symlink():
    osSys("sudo rm -rf /usr/local/patroni.py")
    this_dir = os.getcwd()
    print("\n## Creating '/usr/local/patroni.py' symlink ##")
    source_path = os.path.join(this_dir, "out/posix/patroni/patroni.py")
    target_path = "/usr/local/patroni.py"
    osSys(f"sudo ln -sf {source_path} {target_path}")

# Function to write Patroni YAML configuration file
def write_patroni_yaml():
    # Get the system's IP address
    ip_address = socket.gethostbyname(socket.gethostname())
    usrUsr = f"{util.get_user()}:{util.get_user()}"

    osSys(f"sudo mkdir -p /etc/patroni/")
    osSys(f"sudo chown {usrUsr} /etc/patroni")

    conf_file = os.path.join(thisDir, "patroni.yaml")
    util.replace("IP_NODE", ip_address, conf_file, True)
    osSys(f"sudo cp {conf_file} /etc/patroni/")
    print(f"Patroni YAML file written with IP: {ip_address}")

def configure_patroni():
    osSys("/usr/local/patroni/patroni.py --version")
    osSys("/usr/local/patroni/patronictl.py version")
    osSys("sudo cp patroni.service /etc/systemd/system/")
    osSys("sudo systemctl daemon-reload")
    osSys("sudo systemctl enable patroni")

if __name__ == "__main__":
    create_symlink()
    write_patroni_yaml()
    configure_patroni()
