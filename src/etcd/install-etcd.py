#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #
import os
import sys
import util
import subprocess

thisDir = os.path.dirname(os.path.realpath(__file__))
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

os.chdir(f"{thisDir}")

def copy_etcd():
    util.osSys("sudo rm -rf /usr/local/etcd")
    source_path = thisDir
    target_path = "/usr/local/etcd/"
    util.osSys(f"sudo cp -rf {source_path} {target_path}")

def configure_etcd():
    util.osSys("pip install python-etcd")
    util.osSys("/usr/local/etcd/etcd --version")
    util.osSys("/usr/local/etcd/etcdctl version")

    # Create necessary directories and users
    util.osSys("sudo rm -rf /var/lib/etcd")
    util.osSys("sudo mkdir -p /var/lib/etcd/")
    util.osSys("sudo mkdir -p /etc/etcd")
    util.osSys("sudo groupadd --system etcd")
    util.osSys("sudo useradd -s /sbin/nologin --system -g etcd etcd")

    # Set ownership
    util.osSys("sudo chown -R etcd:etcd /var/lib/etcd/")

    # Copy systemd service file and enable service
    util.osSys("sudo cp etcd.service /etc/systemd/system/")
    util.osSys("sudo systemctl daemon-reload")
    util.osSys("sudo systemctl enable etcd")

if __name__ == "__main__":
    copy_etcd()
    configure_etcd()

