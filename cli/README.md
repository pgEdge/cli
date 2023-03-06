# NODECTL
NODECTL is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
`um`, `service`, `spock`, `cluster`.

We are licensed under the pgEdge Community License 1.0

## Synopsis
<pre>
./nodectl <module> <command> [parameters] [options] 
</pre>

## `um` - Update Manager commands 
<pre>
<a href=nodectl-um-list.md>list</a>               # Display available/installed components 
<a href=nodectl-um-update.md>update</a>             # Retrieve new list of components & update nodectl
<a href=nodectl-um-install.md>install</a>            # Install a component (eg pg15, spock, postgis, etc)
<a href=nodectl-um-remove.md>remove</a>             # Un-install component
<a href=nodectl-um-upgrade.md>upgrade</a>            # Perform an upgrade of a component
<a href=nodectl-um-clean.md>clean</a>              # Delete downloaded component files from local cache
</pre>

## `service` - Service control commands
<pre>
start              # Start server components
stop               # Stop server components
status             # Display status of installed server components
reload             # Reload server config files (without a restart)
restart            # Stop & then start server components
enable             # Enable a server component
disable            # Disable component from starting automatically
config             # Configure a component
init               # Initialize a component
</pre>

## `spock` - Logical and Multi-Active PostgreSQL node configuration
<pre>
install            # Install PG and configure with SPOCK extension
validate           # Check pre-req's for advanced commands
tune               # Tune for this configuration
create-node        # Name this spock node
create-repset      # Define a replication set
create-sub         # Create a subscription
repset-add-table   # Add table to a replication set
sub-add-repset     # Add replication set to a subscription
show-sub-status    # Display the status of the subcription
show-sub-table     # Display subscription table(s)
wait-for-sub-sync  # Pause until subscription is synch'ed
health-check       # Check if PG is accepting connections
metrics-check      # Retrieve advanced DB & OS metrics
</pre>

## `cluster` - Installation and configuration of a pgEdge SPOCK cluster
<pre>
create-local       # Create local cluster of N pgEdge nodes on different ports
destroy            # Stop and then nuke a cluster
validate           # Validate a remote cluster configuration
init               # Initialize a remote cluster for SPOCK
command            # Run `nodectl` command on one or all nodes of a cluster
diff-tables        # Compare table on different cluster nodes
</pre>

## Options
<pre>
--json             # Turn on JSON output
--debug            # Turn on debug logging
--silent           # Less noisy
--verbose or -v    # More noisy
</pre>
