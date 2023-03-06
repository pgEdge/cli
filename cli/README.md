# NODECTL
NODECTL is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
UM, SERVICE, SPOCK, and CLUSTER.

We are licensed under the pgEdge Community License 1.0

## Synopsis
    ./nodectl <module> <command> [parameters] [options] 

## um - Update Manager commands
[**list**](doc/um-list.md) - Display available/installed components<br>
[**update**](doc/um-update.md)  - Retrieve new list of components & update nodectl<br>
[**install**](doc/um-install.md) - Install a component (eg pg15, spock, postgis, etc)<br>
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
<a href=doc/spock-install.md>install</a>            # Install PG and configure with SPOCK extension<br>
<a href=doc/spock-validate.md>validate</a>           # Check pre-req's for advanced commands<br>
<a href=doc/spock-tune.md>tune</a>               # Tune for this configuration<br>
<a href=doc/spock-create-node.md>create-node</a>        # Name this spock node<br>
<a href=doc/spock-create-repset.md>create-repset</a>      # Define a replication set<br>
<a href=doc/spock-create-sub.md>create-sub</a>         # Create a subscription<br>
<a href=doc/spock-repset-add-table.md>repset-add-table</a>   # Add table to a replication set<br>
<a href=doc/spock-sub-add-repset.md>sub-add-repset</a>     # Add replication set to a subscription<br>
<a href=doc/spock-show-sub-status.md>show-sub-status</a>    # Display the status of the subcription<br>
<a href=doc/spock-show-sub-table.md>show-sub-table</a>     # Display subscription table(s)<br>
<a href=doc/spock-wait-for-sub-sync.md>wait-for-sub-sync</a>  # Pause until subscription is synched<br>
<a href=doc/spock-health-check.md>health-check</a>       # Check if PG is accepting connections<br>
<a href=doc/spock-metrics-check.md>metrics-check</a>      # Retrieve advanced DB & OS metrics<br>

## cluster - Installation and configuration of a pgEdge SPOCK cluster
<a href=doc/cluster-create-local.md>create-local</a>       # Create local cluster of N pgEdge nodes on different ports<br>
<a href=doc/cluster-destroy.md>destroy</a>            # Stop and then nuke a cluster<br>
<a href=doc/cluster-validate.md>validate</a>           # Validate a remote cluster configuration<br>
<a href=doc/cluster-init.md>init</a>               # Initialize a remote cluster for SPOCK<br>
<a href=doc/cluster-command.md>command</a>            # Run `nodectl` command on one or all nodes of a cluster<br>
<a href=doc/cluster-diff-tables.md>diff-tables</a>        # Compare table on different cluster nodes<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

