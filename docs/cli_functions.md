# CLI Functions

#### ACE Commands
Commands in the `ace` module include:

| Command  | Description |
|----------|-------------|
| [repset-diff](functions/ace-repset-diff.md) | Loop thru a replication-set's tables and run table-diff on them. |
| [schema-diff](functions/ace-schema-diff.md) | Compare PostgreSQL schemas on different cluster nodes. |
| [spock-diff](functions/ace-spock-diff.md) | Compare spock meta data setup on different cluster nodes. |
| [table-diff](functions/ace-table-diff.md) | Efficiently compare tables across cluster using checksums and blocks of rows. |
| [table-repair](functions/ace-table-repair.md) | Apply changes from a table-diff source of truth to destination table. |
| [table-rerun](functions/ace-table-rerun.md) | Re-run differences on the results of a recent table-diff. |

#### Cluster Installation and Configuration Commands
Commands in the `cluster` module include:

| Command  | Description
|----------|-------------
| [add-node](functions/cluster-add-node.md) | Adds a new node to a cluster, copying configuration details from a specified source node.
| [app-install](functions/cluster-app-install.md) | Install a test application (`pgbench` or `Northwind`).
| [app-remove](functions/cluster-app-remove.md)  | Remove a test application (`pgbench` or `Northwind`) from cluster.
| [command](functions/cluster-command.md) | Run a `pgedge` command on one or all nodes of a cluster.
| [init](functions/cluster-init.md) | Install pgEdge on each node, create the initial database, install Spock,and create all Spock nodes and subscriptions.
| [json-template](functions/cluster-json-template.md) | Create a .json file template to define a cluster that resides on remote hosts.
| [json-validate](functions/cluster-json-validate.md) | Check the validity of a .json file.
| [list-nodes](functions/cluster-list-nodes.md) | List all nodes in the cluster.
| [remove-node](functions/cluster-remove-node.md) | Remove a node from the cluster.
| [remove](functions/cluster-remove.md) | Remove a cluster. This will remove spock subscriptions and nodes, and then stop PostgreSQL on each node. If the flag force is set to `true`, then it will also remove the pgedge directory on each node.
| [replication-begin](functions/cluster-replication-begin.md) | Add all tables in the database to replication on every node.
| [replication-check](functions/cluster-replication-check.md) | Print replication status about every node.

#### Logical and Multi-Active PostgreSQL Node Configuration Commands
Commands in the `spock` module include:

| Command  | Description
|----------|-------------
| [health-check](functions/spock-health-check.md) | Check to see if the PostgreSQL instance is accepting connections.
| [metrics-check](functions/spock-metrics-check.md) | Retrieve advanced database and operating system metrics.
| [node-add-interface](functions/spock-node-add-interface.md) | Add a new node interface.
| [node-alter-location](functions/spock-node-alter-location.md) | Set location details for a spock node.
| [node-create](functions/spock-node-create.md) | Define a node for spock.
| [node-drop](functions/spock-node-drop.md) | Remove a spock node.
| [node-drop-interface](functions/spock-node-drop-interface.md) | Delete a node interface.
| [node-list](functions/spock-node-list.md) | Display a table listing the current nodes.
| [replicate-ddl](functions/spock-replicate-ddl.md) | Enable DDL replication.
| [repset-add-partition](functions/spock-repset-add-partition.md) | Add a partition to a replication set.
| [repset-add-seq](functions/spock-repset-add-seq.md) | Add a sequence to a replication set.
| [repset-add-table](functions/spock-repset-add-table.md) | Add table(s) to replication set.
| [repset-alter](functions/spock-repset-alter.md) | Modify a replication set.
| [repset-create](functions/spock-repset-create.md) | Define a replication set.
| [repset-drop](functions/spock-repset-drop.md) | Remove a replication set.
| [repset-list-tables](functions/spock-repset-list-tables.md) | List tables in replication sets.
| [repset-remove-partition](functions/spock-repset-remove-partition.md) | Remove a partition from the replication set that the parent table is a part of.
| [repset-remove-seq](functions/spock-repset-remove-seq.md) | Remove a sequence from a replication set.
| [repset-remove-table](functions/spock-repset-remove-table.md) | Remove table from replication set.
| [sequence-convert](functions/spock-sequence-convert.md) | Convert sequence(s) to snowflake sequences. 
| [set-readonly](functions/spock-set-readonly.md) | Turn PostgreSQL read-only mode 'on' or 'off'.
| [sub-add-repset](functions/spock-sub-add-repset.md) | Add a replication set to a subscription.
| [sub-alter-interface](functions/spock-sub-alter-interface.md) | Modify an interface to a subscription.
| [sub-create](functions/spock-sub-create.md) | Create a subscription.
| [sub-disable](functions/spock-sub-disable.md) | Put a subscription on hold and disconnect from provider.
| [sub-drop](functions/spock-sub-drop.md) | Delete a subscription.
| [sub-enable](functions/spock-sub-enable.md) | Make a subscription live.
| [sub-remove-repset](functions/spock-sub-remove-repset.md) | Drop a replication set from a subscription.
| [sub-resync-table](functions/spock-sub-resync-table.md) | Resynchronize a table.
| [sub-show-status](functions/spock-sub-show-status.md) | Display the status of the subcription.
| [sub-show-table](functions/spock-sub-show-table.md) | Show subscription tables.
| [sub-wait-for-sync](functions/spock-sub-wait-for-sync.md) | Pause until the subscription is synchronized.
| [table-wait-for-sync](functions/spock-table-wait-for-sync.md) | Pause until a table finishes synchronizing.





#### DB Commands

Commands in the `DB` module include:

| Command  | Description
|----------|-------------
| [guc-create](functions/db-create.md) | To create a database owned by a specific user.
| [guc-set](functions/db-guc-set.md) | Set a GUC value in a PostgreSQL database.
| [guc-show](functions/db-guc-show.md) | Show the current value of a GUC in a PostgreSQL database.

#### Service Control Commands
Commands in the `service` module include:

| Command  | Description
|----------|-------------
| [config](functions/service-config.md) | Configure a component.
| [disable](functions/service-disable.md) | Disable component from starting automatically.
| [enable](functions/service-enable.md) | Enable a server component.
| [init](functions/service-init.md) | Initialize a component.
| [reload](functions/service-reload.md) | Reload server config files (without performing a restart).
| [restart](functions/service-restart.md) | Stop and then start server components.
| [start](functions/service-start.md) | Start server components.
| [status](functions/service-status.md) | Display the status of installed server components.
| [stop](functions/service-stop.md) | Stop a server component.

#### Update Manager Commands

Commands in the `um` module include:

| Command  | Description
|----------|-------------
| [clean](functions/um-clean.md)   | Delete downloaded component files from the local cache.
| [install](functions/um-install.md) | Install a component (for example, `pg16`, `spock`, `postgis`).
| [list](functions/um-list.md) | Display the available and/or installed components.
| [remove](functions/um-remove.md)  | Un-install component (for example, `pg16`, `spock`, `postgis`).
| [update](functions/um-update.md) | Retrieve new list of latest components and update `pgedge`.
| [upgrade](functions/um-upgrade.md) | Perform an upgrade of a component.

