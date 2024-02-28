## SYNOPSIS
    ./pgedge multicloud COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     list-providers      # List supported cloud providers.
     list-airports       # List airport codes & provider regions.
     list-sizes          # List available node sizes.
     list-keys           # List available SSH Keys (not working for Equinix).
     create-node         # Create a virtual machine (VM).
     list-nodes          # List virtual machines.
     start-node          # Start a VM.
     stop-node           # Stop a VM.
     reboot-node         # Reboot a VM.
     destroy-node        # Destroy a node.
     cluster-create      # Create a json config file for a remote cluster.
