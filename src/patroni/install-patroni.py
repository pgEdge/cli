#!/usr/bin/env python3
# Copyright (c) 2022-2025 PGEDGE

import os
import subprocess
import socket
import util

thisDir = os.path.dirname(os.path.realpath(__file__))
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

os.chdir(f"{thisDir}")

def copy_patroni():
    util.osSys("sudo rm -rf /usr/local/patroni/")
    source_path = thisDir
    target_path = "/usr/local/patroni/"
    util.osSys(f"sudo cp -rf {source_path} {target_path}")

def write_patroni_yaml():
    usrUsr = f"{util.get_user()}:{util.get_user()}"

    util.osSys(f"sudo mkdir -p /etc/patroni/")
    util.osSys(f"sudo chown {usrUsr} /etc/patroni")

def configure_patroni():
    util.osSys("pip install click")
    util.osSys("/usr/local/patroni/patroni.py --version")
    util.osSys("/usr/local/patroni/patronictl.py version")
    util.osSys("sudo cp patroni.service /etc/systemd/system/")

if __name__ == "__main__":
    copy_patroni()
    write_patroni_yaml()
    configure_patroni()
