# PGEDGE NODECTL PATRONI-CLUSTER CONTROLLER
Installation and configuration of a pgEdge SPOCK cluster

## Synopsis
    ./nodectl patroni-cluster <command> [parameters] [options]   
     init-remote         # Initialize a patroni-cluster from json definition file of existing nodes.
     reset-remote        # Reset a patroni-cluster from json definition file of existing nodes.
     install-pgedge      # Install pgedge on cluster from json definition file nodes.
     nodectl-command     # Run 'nodectl' commands on one or 'all' nodes.
     patroni-command     # Run 'patronictl' command on a node
     etcd-command        # Run 'etcdctl' command on a node.
     print_config        # Print patroni-cluster json definition file information.
     validate-config     # Validate the JSON configuration file.

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

## Example cluster.json file
```
{
    "HAProxy": {
        "public_ip": "54.85.213.136",
        "local_ip": "54.85.213.136",
        "username": "pgedge",
        "ssh_key_path": "~/Downloads/t9-key"
    },
    "cluster": {
        "cluster": "nv",
        "is_local": "False",
        "create_dt": "2023-10-03",
        "db_name": "pgedge",
        "db_user": "postgres",
        "db_init_passwd": "pgedge",
        "replicator_user": "replicator",
        "replicator_password": "replicator",
        "os_user": "pgedge",
        "ssh_key": "~/Downloads/t9-key",
        "pg_ver": "16",
        "port": "5432",
        "path": "/home/pgedge/pgedge/",
        "cluster_init": {
            "initdb": {
                "encoding": "UTF8",
                "archive_mode": "on",
                "archive_command": "cp -f %p PGARCHIVE/%f"
            },
            "postgresql_conf": {
                "archive_mode": "on",
                "archive_mode2": "off",
                "unix_socket_directories": "/var/run/postgresql",
                "max_connections": 100,
                "max_wal_senders": 10,
                "archive_mode": "on",
                "archive_command": "cp -f %p PGARCHIVE/%f",
                "hot_standby": "on",
                "hot_standby_feedback": "on",
                "wal_level": "logical",
                "wal_sender_timeout": "5s",
                "max_worker_processes": 10,
                "max_replication_slots": 10,
                "max_wal_senders": 10,
                "shared_preload_libraries": "spock",
                "track_commit_timestamp": "on"
            },
            "pg_hba_conf": {
                "local all all": "trust",
                "host all all 0.0.0.0/0": "trust",
                "host replication replicator 0.0.0.0/0": "trust"
            }
        },
        "count": "3"
    },
    "nodes": [
        {
            "name": "node1",
            "public_ip": "3.80.73.43",
            "local_ip": "172.31.25.26",
            "primary": true,
            "bootstrap": true
        },
        {
            "name": "node2",
            "public_ip": "3.80.80.169",
            "local_ip": "172.31.25.98",
            "primary": true,
            "bootstrap": true
        },
        {
            "name": "node3",
            "public_ip": "52.72.218.10",
            "local_ip": "172.31.31.157",
            "primary": false,
            "bootstrap": true
        }
    ]
}
```
