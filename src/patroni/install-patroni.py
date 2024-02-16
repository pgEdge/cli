#     Copyright (c)  2022-2024 PGEDGE  #

# combined_script.py

import os
import socket

class Util:
    @staticmethod
    def message(msg):
        print(msg)

class PatroniSetup:
    PATRONI_YAML = """
    scope: postgres
    namespace: /db/
    name: NODE_NAME
    replication_slot_name: NODE_NAME

    restapi:
      listen: 0.0.0.0:8008
      connect_address: IP_NODE:8008

    etcd3:
      host: IP_NODE:2379
      ttl: 30
      protocol: http

    bootstrap:
      dcs:
        ttl: 30
        loop_wait: 10
        retry_timeout: 10
        maximum_lag_on_failover: 1048576
      initdb:
        - encoding: UTF8
        - data-checksums
      postgresql:
        use_pg_rewind: true
        use_
    """

    @staticmethod
    def create_symlink():
        thisDir = os.path.dirname(os.path.realpath(__file__))
        Util.message("\n## creating '/usr/local/ptroni.py symlink' ########")
        source_path = f"{thisDir}/out/posix/staz/patroni.py"
        target_path = "/usr/local/patroni.py"

        try:
            os.symlink(source_path, target_path)
            print(f"Symlink created: {target_path} -> {source_path}")
        except OSError as e:
            print(f"Failed to create symlink: {e}")

    @staticmethod
    def write_patroni_yaml():
        # Get system's IP address
        ip_address = socket.gethostbyname(socket.gethostname())

        # Replace NODE_NAME with the system's IP address
        patroni_yaml_updated = PatroniSetup.PATRONI_YAML.replace("NODE_NAME", ip_address)

        # Write to /etc/patroni/patroni.yaml
        patroni_yaml_path = "/etc/patroni/patroni.yaml"
        try:
            with open(patroni_yaml_path, "w") as file:
                file.write(patroni_yaml_updated)
            print(f"Successfully wrote to {patroni_yaml_path}")
        except Exception as e:
            print(f"Failed to write to {patroni_yaml_path}: {e}")

if __name__ == "__main__":
    PatroniSetup.create_symlink()
    PatroniSetup.write_patroni_yaml()

