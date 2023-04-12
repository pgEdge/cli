# pgEdge NodeCtl : Command Line Interface

NODECTL is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
`um`, `service`, `spock`, and `cluster`.  We are licensed under the 
pgEdge Community License 1.0

## Synopsis
    ./nodectl <module> <command> [parameters] [options] 

## `um` Update Manager commands
```
list                Display available/installed components
update              Retrieve new list of latest components & update nodectl
install             Install a component (eg pg15, spock, postgis)
remove              Un-install component
upgrade             Perform an upgrade of a component
clean               Delete downloaded component files from local cache
```

## `service` Service control commands
```
start               Start server components
stop                Stop server components
status              Display status of installed server components
reload              Reload server config files (without a restart)
restart             Stop & then start server components
enable              Enable a server component
disable             Disable component from starting automatically
config              Configure a component
init                Initialize a component
```

## `spock` Logical and Multi-Active PostgreSQL node configuration
```
install             Install PG and configure with SPOCK extension
validate            Check pre-req's for advanced commands
tune                Tune for this configuration
node-create         Name this spock node
node-drop.          Remove node row
repset-create       Define a replication set
repset-drop         Remove replication set
repset-add-table    Add table(s) to a replication set
repset-remove-table Remove table from replication set
repset-list-tables  List tables in replication sets
sub-create          Create a subscription
sub-drop            Remove subscription
sub-add-respset     Add replication set to a subscription
sub-show-status     Display the status of the subcription
sub-show-table      Display subscription table(s)
sub-wait-for-sync   Pause until subscription is synched
health-check        Check if PG is accepting connections
metrics-check       Retrieve advanced DB & OS metrics
set-readonly        Turn cluster databases read-only mode 'on' or 'off'
```

## `cluster` Installation and configuration of a SPOCK cluster
```
create-local        Create local cluster of N pgEdge nodes on different ports
destroy             Stop and then nuke a cluster
validate            Validate a remote cluster configuration
init                Initialize a remote cluster for SPOCK
command             Run nodectl command on one or all nodes of a cluster
diff-tables         Compare table on different cluster nodes
```

## Options
```
--json           Turn on JSON output
--debug          Turn on debug logging
--silent         Less noisy
--verbose or -v  More noisy
```

