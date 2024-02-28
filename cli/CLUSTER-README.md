# CLI for Cluster control
Installation and configuration of a pgEdge SPOCK cluster

## Synopsis
    ./pgedge cluster <command> [parameters]

[**define-localhost**](doc/cluster-define-localhost.md)  - Create a json config file for a local cluster<br>
[**define-remote**](doc/cluster-define-remote.md)        - Create a template for a json config file for a remote cluster<br>
[**localhost-create**](doc/cluster-localhost-create.md)   - Create a localhost test cluster of N pgEdge nodes on different ports<br>
[**localhost-destroy**](doc/cluster-localhost-destroy.md) - Stop and then nuke a localhost cluster<br>
[**init**](doc/cluster-init.md)     - Initialize a cluster from json definition file of existing nodes<br>
[**remove**](doc/cluster-remove.md)   - Remove a test cluster from json definition file of existing nodes<br>
[**command**](doc/cluster-command.md)             - Run a CLI command on one or all nodes of a cluster<br>
[**app-install**](doc/cluster-app-install.md)     - Install an application such as NorthWind or pgBench<br>
[**app-remove**](doc/cluster-app-remove.md)       - Remove an applicatio.<br>

## Example cluster.json file
```
{
  "cluster": "cl1",
  "create_dt": "2023-06-08",
  "db_name": "lcdb",
  "db_user": "lcusr",
  "db_init_passwd": "lcpasswd",
  "os_user": "pgedge",
  "ssh_key": "~/key/abc123.key",
  "pg_ver": "15",
  "count": 2,
  "nodes": [
    {
      "nodename": "n1",
      "ip": "10.0.0.1",
      "port": 5432,
      "path": "~"
    },
    {
      "nodename": "n2",
      "ip": "10.0.0.2",
      "port": 5432,
      "path": "~"
    }
  ]
}
```
