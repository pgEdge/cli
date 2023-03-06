# NODECTL
NODECTL is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
`um`, `service`, `spock`, `cluster`.

We are licensed under the pgEdge Community License 1.0

## Synopsis
* ./nodectl <module> <command> [parameters] [options] 


## `um` - Update Manager commands 
[**list**](doc/um-list.md) - *Display available/installed components* \
[**update**]()             - *Retrieve new list of components & update nodectl* \
  
<a href=doc/um-list.md>list</a>               # Display available/installed components 
<a href=doc/um-update.md>update</a>             # Retrieve new list of components & update nodectl
<a href=doc/um-install.md>install</a>            # Install a component (eg pg15, spock, postgis, etc)
<a href=doc/um-remove.md>remove</a>             # Un-install component
<a href=doc/um-upgrade.md>upgrade</a>            # Perform an upgrade of a component
<a href=doc/um-clean.md>clean</a>              # Delete downloaded component files from local cache
</pre>

## `service` - Service control commands
<pre>
<a href=doc/service-start.md>start</a>              # Start server components
<a href=doc/service-stop.md>stop</a>               # Stop server components
<a href=doc/service-status.md>status</a>             # Display status of installed server components
<a href=doc/service-reload.md>reload</a>             # Reload server config files (without a restart)
<a href=doc/service-restart.md>restart</a>            # Stop & then start server components
<a href=doc/service-enable.md>enable</a>             # Enable a server component
<a href=doc/service-disable.md>disable</a>            # Disable component from starting automatically
<a href=doc/service-config-.md>config</a>             # Configure a component
<a href=doc/service-init.md>init</a>               # Initialize a component
</pre>

## `spock` - Logical and Multi-Active PostgreSQL node configuration
<pre>
<a href=doc/spock-install.md>install</a>            # Install PG and configure with SPOCK extension
<a href=doc/spock-validate.md>validate</a>           # Check pre-req's for advanced commands
<a href=doc/spock-tune.md>tune</a>               # Tune for this configuration
<a href=doc/spock-create-node.md>create-node</a>        # Name this spock node
<a href=doc/spock-create-repset.md>create-repset</a>      # Define a replication set
<a href=doc/spock-create-sub.md>create-sub</a>         # Create a subscription
<a href=doc/spock-repset-add-table.md>repset-add-table</a>   # Add table to a replication set
<a href=doc/spock-sub-add-repset.md>sub-add-repset</a>     # Add replication set to a subscription
<a href=doc/spock-show-sub-status.md>show-sub-status</a>    # Display the status of the subcription
<a href=doc/spock-show-sub-table.md>show-sub-table</a>     # Display subscription table(s)
<a href=doc/spock-wait-for-sub-sync.md>wait-for-sub-sync</a>  # Pause until subscription is synch'ed
<a href=doc/spock-health-check.md>health-check</a>       # Check if PG is accepting connections
<a href=doc/spock-metrics-check.md>metrics-check</a>      # Retrieve advanced DB & OS metrics
</pre>

## `cluster` - Installation and configuration of a pgEdge SPOCK cluster
<pre>
<a href=doc/cluster-create-local.md>create-local</a>       # Create local cluster of N pgEdge nodes on different ports
<a href=doc/cluster-destroy.md>destroy</a>            # Stop and then nuke a cluster
<a href=doc/cluster-validate.md>validate</a>           # Validate a remote cluster configuration
<a href=doc/cluster-init.md>init</a>               # Initialize a remote cluster for SPOCK
<a href=doc/cluster-command.md>command</a>            # Run `nodectl` command on one or all nodes of a cluster
<a href=doc/cluster-diff-tables.md>diff-tables</a>        # Compare table on different cluster nodes
</pre>

## Options
<pre>
--json             # Turn on JSON output
--debug            # Turn on debug logging
--silent           # Less noisy
--verbose or -v    # More noisy
</pre>
