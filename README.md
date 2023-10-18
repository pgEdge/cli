# pgEdge NodeCtl : Command Line Interface


# Summary
NODECTL is the pgEdge Command Line Interface (CLI) for managing components. 
It is licensed under the pgEdge Community License 1.0

# Configuring the Python Environment for Dev/Test
In order to run the Python code, a suitable POSIX environment is required. 
Python version 3.9 and later are currently supported. It is recommended that
a Python Virtual Environment is setup for this purpose, rather than using
the system Python environment. On Linux and Mac systems, the process is 
simple as follows:

Create a virtual environment in an appropriate directory. The last argument is the name of the environment; that can be changed as desired:

$ python3 -m venv venv

Now activate the virtual environment:

$ source venv/bin/activate

Some of the components used by NodeCtl require a very recent version of pip, so update that to the latest:

$ pip install --upgrade pip

# CLI Modules 
The modules are `um`, `service`, `spock`, `cluster`, `db`, `secure`, and `ace`.  

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
node-create          Define a node for spock
node-drop            Remove a spock node
node-alter-location  Set location details for spock node
node-list            Display node table
node-add-interface   Add a new node interafce
node-drop-interface  Delete a node interface
repset-create        Define a replication set
repset-alter         Modify a replication set
repset-drop          Remove a replication set
repset-add-table     Add table(s) to replication set
repset-remove-table  Remove table from replication set
repset-add-seq       Add a sequence to a replication set
repset-remove-seq    Remove a sequence from a replication set
repset-alter-seq     Change a replication set sequence
repset-list-tables   List tables in replication sets
sub-create           Create a subscription
sub-drop             Delete a subscription
sub-alter-interface  Modify an interface to a subscription
sub-enable           Make a subscription live
sub-disable          Put a subscription on hold and disconnect from provider
sub-add-repset       Add a replication set to a subscription
sub-remove-repset    Drop a replication set from a subscription
sub-show-status      Display the status of the subcription
sub-show-table       Show subscription tables
sub-sync             Synchronize a subscription
sub-resync-table     Resynchronize a table
sub-wait-for-sync    Pause until the subscription is synchronized
table-wait-for-sync  Pause until a table finishes synchronizing
```

## `db` Database Operations
```
health-check         Check if PG instance is accepting connections
metrics-check        Retrieve advanced DB & OS metrics
set-readonly         Turn PG read-only mode 'on' or 'off'
create               Create a database
```

## `cluster` Installation and configuration of a SPOCK cluster
```
local-create        Create a localhost test cluster of N pgEdge nodes on different ports
local-destroy       Stop and then nuke a cluster
remote-init         Initialize pgEdge on a remote cluster that you create & manage yourself
remote-reset        Reset pgEdge on a remote cluster
remote-import-def   Import a json cluster defintion file
command             Run nodectl command on one or all nodes of a cluster
app-install         Install an application such as NorthWind or pgBench
app-remove          Remove an application
```

## `secure` Interact with pgEdge Cloud services
```
config              Login nodeCtl with a pgEdge Cloud Account
list-cloud-acct     List all cloud account ids in a pgEdge Cloud Account
list-clusters       List all clusters in a pgEdge Cloud Account
cluster-status      Return info on a cluster in a pgEdge Cloud Account
list-nodes          List all nodes in a pgEdge Cloud Account cluster
import-cluster-def  Enable nodeCtl cluster commands on a pgEdge Cloud Cluster
get-cluster-id      Return the cluster id based on a cluster display name
get-node-id         Return the node id based on cluster and node display name
push-metrics        Coming Soon: push pgEdge Metrics to a specified target
create-cluster      Create a new Cloud Cluster based on json file
destroy-cluster     Delete a pgEdge Cloud Cluster
```

## `ace` Anti Chaos Engine
```
diff-tables         Compare tables in a cluster
diff-schemas        Compare Schema meta-data
diff-spock          Compare spock rules setup across cluster nodes
```

## Options
```
--json           Turn on JSON output
--debug          Turn on debug logging
--silent         Less noisy
--verbose or -v  More noisy
```
