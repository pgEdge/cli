# CLI Functions

## standalone commands

| Command | Description |
|---------|-------------|
| [`setup`](functions/setup.md) | Install a pgEdge node (including PostgreSQL, spock, and snowflake-sequences) |
| [`upgrade-cli`](functions/upgrade-cli.md) | Upgrade pgEdge CLI to latest stable version |

## ace module commands

| Command | Description |
|---------|-------------|
| [`ace table-diff`](functions/ace-table-diff.md) | Compare a table across a cluster and produce a report showing any differences. |
| [`ace table-repair`](functions/ace-table-repair.md) | Repair a table across a cluster by fixing data inconsistencies identified in a table-diff operation. |
| [`ace table-rerun`](functions/ace-table-rerun.md) | Reruns a table diff operation based on a previous diff file. |
| [`ace repset-diff`](functions/ace-repset-diff.md) | Compare a repset across a cluster and produce a report showing any differences. |
| [`ace schema-diff`](functions/ace-schema-diff.md) | Compare a schema across a cluster and produce a report showing any differences. |
| [`ace spock-diff`](functions/ace-spock-diff.md) | Compare the spock metadata across a cluster and produce a report showing any differences. |
| [`ace spock-exception-update`](functions/ace-spock-exception-update.md) | Updates the Spock exception status for a specified cluster and node. |
| [`ace start`](functions/ace-start.md) | Start the ACE background scheduler and API |

## cluster module commands

| Command | Description |
|---------|-------------|
| [`cluster json-validate`](functions/cluster-json-validate.md) | Validate and update a cluster configuration JSON file. |
| [`cluster json-create`](functions/cluster-json-create.md) | Create a cluster configuration JSON file based on user input. |
| [`cluster json-template`](functions/cluster-json-template.md) | Create a template for a cluster configuration JSON file. |
| [`cluster init`](functions/cluster-init.md) | Initialize a cluster via cluster configuration JSON file. |
| [`cluster list-nodes`](functions/cluster-list-nodes.md) | List all nodes in the cluster. |
| [`cluster add-node`](functions/cluster-add-node.md) | Add a new node to a cluster |
| [`cluster remove-node`](functions/cluster-remove-node.md) | Remove a node from a cluster |
| [`cluster replication-begin`](functions/cluster-replication-begin.md) | Add all tables to the default replication set on every node. |
| [`cluster replication-check`](functions/cluster-replication-check.md) | Check and display the replication status for a given cluster. |
| [`cluster add-db`](functions/cluster-add-db.md) | Add a database to an existing pgEdge cluster. |
| [`cluster remove`](functions/cluster-remove.md) | Remove a cluster. |
| [`cluster command`](functions/cluster-command.md) | Run './pgedge' commands on one or all nodes in a cluster. |
| [`cluster ssh`](functions/cluster-ssh.md) | Establish an SSH session into the specified node of a cluster. |
| [`cluster app-install`](functions/cluster-app-install.md) | Install a test application on all nodes in the cluster. |
| [`cluster app-remove`](functions/cluster-app-remove.md) | Remove a test application from all nodes in the cluster. |
| [`cluster app-concurrent-index`](functions/cluster-app-concurrent-index.md) | Create a concurrent index on a table column in a database. |

## db module commands

| Command | Description |
|---------|-------------|
| [`db create`](functions/db-create.md) | Create a database owned by a specific user |
| [`db guc-set`](functions/db-guc-set.md) | Set GUC |
| [`db guc-show`](functions/db-guc-show.md) | Show GUC |
| [`db set-readonly`](functions/db-set-readonly.md) | Turn PG read-only mode 'on' or 'off'. |
| [`db test-io`](functions/db-test-io.md) | Use the 'fio' Flexible IO Tester on pg data directory |

## localhost module commands

| Command | Description |
|---------|-------------|
| [`localhost cluster-create`](functions/localhost-cluster-create.md) | Create localhost cluster of N pgEdge nodes on different ports. |
| [`localhost cluster-destroy`](functions/localhost-cluster-destroy.md) | Stop and then nuke a localhost cluster. |

## service module commands

| Command | Description |
|---------|-------------|
| [`service start`](functions/service-start.md) | Start server components |
| [`service stop`](functions/service-stop.md) | Stop server components |
| [`service status`](functions/service-status.md) | Display running status of server components |
| [`service restart`](functions/service-restart.md) | Stop & then start server components |
| [`service reload`](functions/service-reload.md) | Reload server configuration files (without a restart) |
| [`service enable`](functions/service-enable.md) | Enable a server component to start automatically |
| [`service disable`](functions/service-disable.md) | Disable a server component from starting automatically |
| [`service config`](functions/service-config.md) | Configure a component |
| [`service init`](functions/service-init.md) | Initialize a component |

## spock module commands

| Command | Description |
|---------|-------------|
| [`spock node-create`](functions/spock-node-create.md) | Define a node for spock. |
| [`spock node-drop`](functions/spock-node-drop.md) | Remove a spock node. |
| [`spock node-alter-location`](functions/spock-node-alter-location.md) | Set location details for spock node. |
| [`spock node-list`](functions/spock-node-list.md) | Display node table. |
| [`spock node-add-interface`](functions/spock-node-add-interface.md) | Add a new node interface. |
| [`spock node-drop-interface`](functions/spock-node-drop-interface.md) | Delete a node interface. |
| [`spock repset-create`](functions/spock-repset-create.md) | Define a replication set. |
| [`spock repset-alter`](functions/spock-repset-alter.md) | Modify a replication set. |
| [`spock repset-drop`](functions/spock-repset-drop.md) | Remove a replication set. |
| [`spock repset-add-table`](functions/spock-repset-add-table.md) | Add table(s) to a replication set. |
| [`spock repset-remove-table`](functions/spock-repset-remove-table.md) | Remove table from replication set. |
| [`spock repset-add-partition`](functions/spock-repset-add-partition.md) | Add a partition to a replication set. |
| [`spock repset-remove-partition`](functions/spock-repset-remove-partition.md) | Remove a partition from a replication set. |
| [`spock repset-list-tables`](functions/spock-repset-list-tables.md) | List tables in replication sets. |
| [`spock sub-create`](functions/spock-sub-create.md) | Create a subscription. |
| [`spock sub-drop`](functions/spock-sub-drop.md) | Delete a subscription. |
| [`spock sub-alter-interface`](functions/spock-sub-alter-interface.md) | Modify an interface to a subscription. |
| [`spock sub-enable`](functions/spock-sub-enable.md) | Make a subscription live. |
| [`spock sub-disable`](functions/spock-sub-disable.md) | Put sub on hold & disconnect from provider. |
| [`spock sub-add-repset`](functions/spock-sub-add-repset.md) | Add a replication set to a subscription. |
| [`spock sub-remove-repset`](functions/spock-sub-remove-repset.md) | Drop a replication set from a subscription. |
| [`spock sub-show-status`](functions/spock-sub-show-status.md) | Display the status of the subscription. |
| [`spock sub-show-table`](functions/spock-sub-show-table.md) | Show subscription tables. |
| [`spock sub-resync-table`](functions/spock-sub-resync-table.md) | Resynchronize a table. |
| [`spock sub-wait-for-sync`](functions/spock-sub-wait-for-sync.md) | Pause until the subscription is synchronized. |
| [`spock table-wait-for-sync`](functions/spock-table-wait-for-sync.md) | Pause until a table finishes synchronizing. |
| [`spock replicate-ddl`](functions/spock-replicate-ddl.md) | Replicate DDL through replication set(s). |
| [`spock sequence-convert`](functions/spock-sequence-convert.md) | Convert sequence to snowflake sequence. |
| [`spock health-check`](functions/spock-health-check.md) | Check if PG instance is accepting connections. |
| [`spock metrics-check`](functions/spock-metrics-check.md) | Retrieve advanced DB & OS metrics. |
| [`spock set-readonly`](functions/spock-set-readonly.md) | DEPRECATED: use db.set_readonly() instead |

## um module commands

| Command | Description |
|---------|-------------|
| [`um list`](functions/um-list.md) | Display available/installed components |
| [`um update`](functions/um-update.md) | Update with a new list of available components |
| [`um install`](functions/um-install.md) | Install a component |
| [`um remove`](functions/um-remove.md) | Uninstall a component |
| [`um upgrade`](functions/um-upgrade.md) | Perform an upgrade to a newer version of a component |
| [`um clean`](functions/um-clean.md) | Delete downloaded component files from local cache |
| [`um verify-metadata`](functions/um-verify-metadata.md) | Display component metadata from the local store |
| [`um download`](functions/um-download.md) | Download a component into local cache (without installing it) |

