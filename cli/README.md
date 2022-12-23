# README for IO #

IO is an API for management of a Postgres eco-system of components

## Usage ##
```
io command [component] [options]
```

## Informational Commands ##
```
  help      - Display help file
  info      - Display OS or component information
  status    - Display status of installed server components
  list      - Display available/installed components 
```

## Service Control Commands ##
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

## Software Install & Update Commands ##
```
  update    - Retrieve new lists of components
  upgrade   - Perform an upgrade of a component
  install   - Install (or re-install) a component  
  remove    - Un-install component   
  clean     - Delete downloaded component files
```
