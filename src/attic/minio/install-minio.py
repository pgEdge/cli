#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #

import util

thisDir = os.path.dirname(os.path.realpath(__file__))
usr=minio
exe=minio
binDir=/usr/local/bin


def copy_minio():
    util.osSys(f"sudo rm -f {binDir}/minio")
    util.osSys(f"sudo cp {exe} {binDir}/.")


def configure_minio():
    util.osSys(f"{binDir}/{exe} --version")

    # Create necessary directories and users
    util.osSys(f"sudo touch /etc/defaut/{exe}"
    util.osSys(f"sudo groupadd -r {usr}")
    util.osSys(f"sudo useradd -M -r -g {usr} {usr}")

    # Set ownership
    util.osSys(f"sudo chown -R {usr}:{usr}  /etcd/default/{exe}")

    # Copy systemd service file and enable service
    util.osSys("sudo cp {exe}.service /etc/systemd/system/.")
    util.osSys("sudo systemctl daemon-reload")
    util.osSys("sudo systemctl enable minio")

if __name__ == "__main__":
    copy_minio()
    configure_minio()

