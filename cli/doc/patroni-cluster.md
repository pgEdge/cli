## SYNOPSIS
    ./nodectl patroni-cluster COMMAND
 
## COMMANDS
   patroni-./nodectl cluster COMMAND

COMMANDS
    COMMAND is one of the following:
     init-remote         # Initialize a patroni-cluster from json definition file of existing nodes.
     reset-remote        # Reset a patroni-cluster from json definition file of existing nodes.
     install-pgedge      # Install pgedge on cluster from json definition file nodes.
     nodectl-command     # Run 'nodectl' commands on one or 'all' nodes.
     patroni-command     # Run 'patronictl' command on a node
     etcd-command        # Run 'etcdctl' command on a node.
     print_config        # Print patroni-cluster json definition file information.
     validate-config     # Validate the JSON configuration file.
