The pgEdge NodeCtl (nc) Command Line Interface is a unified tool to
manage your Postgres eco-system of components

## Synopsis
```
nc [options] <command> <subcommand> [parameters]
```

Use nc command help for information on a specific command. 
Use nc help topics to view a list of available help topics.
The synopsis for each command shows its parameters and their usage.
Optional parameters are shown in square brackets.

## Commands
```
svc       - Service controller
um        - Update Manager
spock     - Spock configuration
lc        - Localhost Cluster
```

## svc - Service Control Subcommands
```
start     - Start server components
stop      - Stop server components
reload    - Reload server configuration files (without a restart)
restart   - Stop & then start server components
enable    - Enable a component
disable   - Disable a server server component from starting automatically
config    - Configure a component
init      - Initialize a component
```

## um - Update Manager Subcommands 
```
info      - Display OS or component information
update    - Retrieve new lists of components
install   - Install (or re-install) a component  
remove    - Un-install component   upgrade   - Perform an upgrade of a component
downgrade - Perform a downgrade of a component
clean     - Delete downloaded component files from local cache
status    - Display status of installed server components
list      - Display available/installed components 
```

## spock - Logical & Multi-Active Replication Subcommands
```

```

## lc - Local Cluster Subcommands
```
create   - Create an n-node local cluster
destroy  - Stop and then nuke a local cluster
command  - Run an (nc) command on one or all nodes of the local cluster
```

## Global Options
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
