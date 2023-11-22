# PGEDGE CTL CLI
CTL is the pgEdge Command & Control Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
UM, SERVICE, SPOCK, CLUSTER, & ACE.

We are licensed under the pgEdge Community License v1.0

## Synopsis
    ./ctl <module> <command> [parameters] [options] 

## um - Update Manager commands
[**list**](doc/um-list.md) - Display available/installed components<br>
[**update**](doc/um-update.md)  - Retrieve new list of components & update ctl<br>
[**install**](doc/um-install.md) - Install a component (eg pg16, spock32, postgis, ...)<br>
[**remove**](doc/um-remove.md) - Un-install component<br>
[**upgrade**](doc/um-upgrade.md) - Perform an upgrade of a component<br>
[**clean**](doc/um-clean.md) - Delete downloaded component files from local cache<br>


## service - Service control commands
[**start**](service-start.md)                 - Start server components<br>
[**stop**](doc/service-stop.md)               - Stop server components<br>
[**status**](doc/service-status.md)           - Display status of installed server components<br>
[**reload**](doc/service-reload.md)           - Reload server config files (without a restart)<br>
[**restart**](doc/service-restart.md)         - Stop & then start server components<br>
[**enable**](doc/service-enable.md)           - Enable a server component<br>
[**disable**](doc/service-disable.md)         - Disable component from starting automatically<br>
[**config**](doc/service-config-.md)          - Configure a component<br>
[**init**](doc/service-init.md)               - Initialize a component<br>

## spock - Logical and Multi-Active PostgreSQL node configuration
[**install**](doc/spock-install.md)             - Install PG and configure with SPOCK extension<br>
[**validate**](doc/spock-validate.md)           - Check pre-req's for advanced commands<br>
[**tune**](doc/spock-tune.md)                   - Tune for this configuration<br>
[**create-node**](doc/spock-create-node.md)     - Name this spock node<br>
[**create-repset**](doc/spock-create-repset.md) - Define a replication set<br>
[**create-sub**](doc/spock-create-sub.md)       - Create a subscription<br>
[**repset-add-table**](doc/spock-repset-add-table.md)  - Add table to a replication set<br>
[**sub-add-repset**](doc/spock-sub-add-repset.md)     - Add replication set to a subscription<br>
[**show-sub-status**](spock-show-sub-status.md)        - Display the status of the subcription<br>
[**show-sub-table**](doc/spock-show-sub-table.md)      - Display subscription table(s)<br>
[**spock-wait-for-sub-sync**](doc/spock-wait-for-sub-sync.md)  - Pause until subscription is synched<br>
[**health-check**](doc/spock-health-check.md)          - Check if PG is accepting connections<br>
[**metrics-check**](doc/spock-metrics-check.md)        - Retrieve advanced DB & OS metrics<br>

## cluster - Installation and configuration of a pgEdge SPOCK cluster
[**local-create**](doc/cluster-local-create.md)   - Create local cluster of N pgEdge nodes on different ports<br>
[**local-destroy**](doc/cluster-local-destroy.md) - Stop and then nuke a cluster<br>
[**remote-init**](doc/cluster-remote-init.md)     - Initialize a remote cluster for SPOCK<br>
[**remote-reset**](doc/cluster-remote-reset.md)   - Reset a remote cluster for SPOCK<br>
[**remote-import-def**](doc/cluster-remote-import-def.md)  - Import a JSON defintion file for a remote cluster<br>
[**command**](doc/cluster-command.md)             - Run `nodectl` command on one or all nodes of a cluster<br>
[**app-install**](doc/cluster-app-install.md)     - Install an application such as NorthWind or pgBench<br>
[**app-remove**](doc/cluster-app-remove.md)       - Remove an application<br>

## ace - The Anti Chaos Engine for a pgEdge SPOCK cluster
[**diff-tables**](doc/ace-diff-tables.md)         - Compare tables on different cluster nodes<br>
[**diff-schemas**](doc/ace-diff-schemas.md)       - Compare schemas on different cluster nodes<br>
[**diff-spock**](doc/ace-diff-spock.md)           - Compare `spock` setup on cluster nodes<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

