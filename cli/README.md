
# NODECTL
NODECTL is the pgEdge Node Control Command Line Interface (CLI).  It is a cross-platform tool
to manage your PostgreSQL eco-system of components.

## Synopsis
```
./nodectl <module> <command> [parameters] [options] 
```

## Modules
```
service   - Service control
um        - Update Manager

pgedge    - pgEdge installation & configuration
spock     - Logical & Multi-Active configuration
cluster   - Cluster setup & control 

help      - Displays this high level help file
info      - Display OS, machine & `nodectl` version info
```

## `service` - Service control commands
```
start     - Start server components
stop      - Stop server components
status    - Display status of installed server components
reload    - Reload server configuration files (without a restart)
restart   - Stop & then start server components
enable    - Enable a component
disable   - Disable a server server component from starting automatically
config    - Configure a component
init      - Initialize a component
```

## `um` - Update Manager commands 
```
list      - Display available/installed components 
update    - Retrieve new lists of components
install   - Install (or re-install) a component  
remove    - Un-install component
upgrade   - Perform an upgrade of a component
downgrade - Perform a downgrade of a component
clean     - Delete downloaded component files from local cache
```

## `pgedge` - Installation and configuration of a pgEdge node
```
pre-reqs  - Check and configure pre-reqs (for running SPOCK commands)
install   - Install a node
tune      - Tune postgres for the node size
remove    - Uninstall pgedge from this node
```

## `spock` - Logical & Multi-Active Replication commands
```
create-node          - Create a spock node
create-rep-set       - Define a replication set
create-sub           - Create a subscription
add-rep-set-table    - Add a table[s] to a replication set
add-rep-set-sub      - Add replication set to a subscription
show-sub-status      - Display the status of the subcription
show-sub-table       - Display subscription table(s)
wait-for-sub-sync    - Pause until subscription is synched
health-check         - Check if PG is accepting connections
metrics-check        - Retrieve OS & DB metrics
```

## `cluster` - Cluster setup & control
```
local     - Create an n-node local cluster
destroy   - Stop and then nuke a cluster
validate  - Validate a cluster configuration
init      - Initialize cluster for SPOCK
command   - Run `nodectl` command on one or all nodes of the cluster
diff      - Compare table on different nodes
```

## Options
```
--json    Turn on JSON output
--debug   Turn on debug logging
--silent
--verbose or -v
```
