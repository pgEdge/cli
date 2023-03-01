# NODECTL
NODECTL is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
`um`, `service`, `spock`, `cluster`.

We are licensed under the [pgEdge Community License 1.0](PGEDGE-COMMUNITY-LICENSE.md)

## Synopsis
```
./nodectl <module> <command> [parameters] [options] 
```

## `um` - Update Manager commands 
```
list               # Display available/installed components 
update             # Retrieve new list of components & update nodectl
install            # Install a component (eg pg15, spock, postgis, etc)
remove             # Un-install component
upgrade            # Perform an upgrade of a component
clean              # Delete downloaded component files from local cache
```

## `service` - Service control commands
```
start              # Start server components
stop               # Stop server components
status             # Display status of installed server components
reload             # Reload server configuration files (without a restart)
restart            # Stop & then start server components
enable             # Enable a component
disable            # Disable server component from starting automatically
config             # Configure a component
init               # Initialize a component
```

## `spock` - Logical and Multi-Active PostgreSQL node configuration
```
install            # Install Postgres and configure with the SPOCK extension
validate           # Validate Pre-Req's for running advanced commands
tune               # Tune for this configuration
create-node        # Name this spock node
create-repset      # Define a replication set
create-sub         # Create a subscription
add-table-repset   # Add table[s] to a replication set
add-repset-sub     # Add replication set to a subscription
show-sub-status    # Display the status of the subcription
show-sub-table     # Display subscription table(s)
wait-for-sub-sync  # Pause until subscription is synched
health-check       # Check if PG is accepting connections
metrics-check      # Retrieve OS & DB metrics
```

## `cluster` - Installation and configuration of a pgEdge SPOCK cluster
```
create-local       # Create local cluster of N pgEdge nodes on different ports
destroy            # Stop and then nuke a cluster
validate           # Validate a remote cluster configuration
init               # Initialize a remote cluster for SPOCK
command            # Run `nodectl` command on one or all nodes of a cluster
diff-tables        # Compare table on different cluster nodes
```

## Options
```
--json             # Turn on JSON output
--debug            # Turn on debug logging
--silent           # Less noisy
--verbose or -v    # More noisy
```
