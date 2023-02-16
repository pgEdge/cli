
NodeCtl (nc) is a CLI for management of a Postgres eco-system of components

## Usage ##
```
nc command [component] [options]
```

## Informational Commands ################################################
```
  help      - Display help file
  info      - Display OS or component information
  status    - Display status of installed server components
  list      - Display available/installed components 
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
  update    - Retrieve new lists of components
  upgrade   - Perform an upgrade of a component
  install   - Install (or re-install) a component  
  remove    - Un-install component   
  clean     - Delete downloaded component files from local cache
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


# LOCAL-CLUSTER

## SYNOPSIS
```
  ./nc local-cluster COMMAND
```

## COMMANDS 
```
  COMMAND is one of the following **bold
```

### create
```
   Create a local cluster that runs N instances of pgEdge each running PG on a different port.
```

### destroy
```
   Stop each node of a local-cluster and then delete all of it.
```

 ### command
```   
  Run './nc' commands on one or 'all' nodes.
```

# ================================================

# LOCAL-CLUSTER CREATE

## SYNOPSIS 
```  
  ./nc local-cluster create CLUSTER_NAME NUM_NODES
```

## DESCRIPTION 
```  
  Create a local cluster that runs N instances of pgEdge each running PG on a different port.
```

## POSITIONAL ARGUMENTS 
```  
  CLUSTER_NAME NUM_NODES
```

## FLAGS 
```-U, --User=USER Default: 'lcusr' 
   -P, --Passwd=PASSWD Default: 'lcpasswd' 
   -d, --db=DB Default: 'lcdb' 
   --port1=PORT1 Default: 6432 
   --pg=PG Default: '15' 
   -b, --base_dir=BASE_DIR Default: 'cluster'
```
