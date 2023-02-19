
## #### NODECTL CLI ######################################################
The pgEdge NodeCtl CLI is a cross-platform tool to manage your 
PostgreSQL eco-system of components.

## Synopsis
```
./nodectl <command> <subcommand> [parameters] [options] 
```

## Commands
```
help      - Displays this high level help file
info      - Display OS or component information
svc       - Service controller
um        - Update Manager
spock     - Spock configuration
pgedge    - pgEdge Installation & Configuration
lc        - Localhost Cluster
```

## svc - Service Control Subcommands
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

## um - Update Manager Subcommands 
```
list      - Display available/installed components 
update    - Retrieve new lists of components
install   - Install (or re-install) a component  
remove    - Un-install component
upgrade   - Perform an upgrade of a component
downgrade - Perform a downgrade of a component
clean     - Delete downloaded component files from local cache
```

## spock - Logical & Multi-Active Replication Subcommands
```
create-node                            - Create a spock node
create-replication-set                 - Define a replication set
create-subscriptiion                   - Create a subscription
show-subscription-status               - Display the status of the subcription
show-subscription-table                - Display subscription table(s)
alter-subscription-add-replication-set - Add replication set to a subscription
wait-for-subscription-sync-complete    - Pause until subscription is synched
get-pii-cols                           - Retrieve the columns identified as PII
get-replication-tables                 - Show the replication tables
replication-set-add-table              - Add a table[s] to a replication set
health-check                           - Check if PG is accepting connections
metrics-check                          - Retrieve OS & DB metrics
```

## lc - Local Cluster Subcommands
```
create   - Create an n-node local cluster
destroy  - Stop and then nuke a local cluster
command  - Run `nodectl` command on one or all nodes of the local cluster
```

## Options
```
--debug Turn on debug logging.
--json  Turn on JSON output.
--autostart
--start
--silent
--verbose or -v
--rm-data (remove the data directory after un-installing server)
 -y  (accept default parameter (such as auto generated password)
 -U  superuser
 -P  superuser password (only used during install-pgedge)
 -d  database
```
