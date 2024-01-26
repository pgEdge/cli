# CLI for Cluster control
Installation and configuration of a pgEdge SPOCK cluster

## Synopsis
    ./pgedge cluster <command> [parameters] [options]   

[**local-create**](doc/cluster-local-create.md)   - Create a localhost test cluster of N pgEdge nodes on different ports.<br>
[**local-destroy**](doc/cluster-local-destroy.md) - Stop and then nuke a localhost cluster.<br>
[**remote-init**](doc/cluster-remote-init.md)     - Configure a test SSH cluster from a JSON cluster definition file.<br>
[**remote-reset**](doc/cluster-remote-reset.md)   - Reset a test SSH cluster.<br>
[**remote-import-def**](doc/cluster-remote-import-def.md)  - Import a cluster definition file so we can work with it like a pgEdge cluster.<br>
[**command**](doc/cluster-command.md)             - Run `nodectl` command on one or all nodes of a cluster.<br>
[**app-install**](doc/cluster-app-install.md)     - Install an application such as NorthWind or pgBench.<br>
[**app-remove**](doc/cluster-app-remove.md)       - Remove an application.<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

## Example cluster.json file
```
{
  "cluster": "cl1",
  "create_dt": "2023-06-08",
  "db_name": "lcdb",
  "db_user": "lcdb",
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
