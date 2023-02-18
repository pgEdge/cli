The pgEdge NodeCtl (nc) Command Line Interface is a unified tool to
manage your Postgres eco-system of components

##Synopsis
```
nc [options] <command> <subcommand> [parameters]
```

Use nc command help for information on a specific command. 
Use nc help topics to view a list of available help topics.
The synopsis for each command shows its parameters and their usage.
Optional parameters are shown in square brackets.

##Global Options
--debug Turn on debug logging.
--json  Turn on JSON output.

##Commands
  svc           : Service controller
  um            : UpdateManager
  spock         : Spock configuration
  lc            : LocalCluster support N - nodes on localhost
  pgbin         : Execute pgbin commands
  bckrst        : Backup & Restore commands




## Usage ##
```
```

## Informational Commands ################################################
```
  help      - Display help file
```

## Service Control Commands ##############################################
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

## Software Install & Update Commands ####################################
```
  info      - Display OS or component information
  update    - Retrieve new lists of components
  upgrade   - Perform an upgrade of a component
  install   - Install (or re-install) a component  
  remove    - Un-install component   
  clean     - Delete downloaded component files from local cache
  status    - Display status of installed server components
  list      - Display available/installed components 
```

## Options ##############################################################
```
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
