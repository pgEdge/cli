#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #
import os
import sys
import util
import subprocess

def osSys(p_input, p_display=True):
    if p_display:
        print("# " + p_input)
    subprocess.run(p_input.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install_dependencies():
    """Install required dependencies."""
    osSys("sudo yum install -y golang haproxy")

def stop_etcd_service():
    """Stop the etcd service."""
    osSys("sudo systemctl stop etcd")

def copy_binaries():
    """Copy etcd binaries to /usr/local/bin/ and make them executable."""
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    osSys("sudo cp etcd /usr/local/bin/")
    osSys("sudo cp etcdctl /usr/local/bin/")
    osSys("sudo chmod +x /usr/local/bin/etcd*")

def configure_etcd():
    """Configure etcd."""
    osSys("etcd --version")
    osSys("etcdctl version")

    # Create necessary directories and users
    osSys("sudo mkdir -p /var/lib/etcd/")
    osSys("sudo mkdir -p /etc/etcd")
    osSys("sudo groupadd --system etcd")
    osSys("sudo useradd -s /sbin/nologin --system -g etcd etcd")

    # Set ownership
    osSys("sudo chown -R etcd:etcd /var/lib/etcd/")

    # Copy systemd service file and enable service
    osSys("sudo cp etcd.service /etc/systemd/system/")
    osSys("sudo systemctl daemon-reload")
    osSys("sudo systemctl enable etcd")

if __name__ == "__main__":
    install_dependencies()
    stop_etcd_service()
    copy_binaries()
    configure_etcd()

