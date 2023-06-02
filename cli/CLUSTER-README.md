# PGEDGE NODECTL CLUSTER CONTROLLER
Installation and configuration of a pgEdge SPOCK cluster

## Synopsis
    ./nodectl spock <command> [parameters] [options]   

[**create-local**](doc/cluster-create-local.md)   - Create a localhost test cluster of N pgEdge nodes on different ports.<br>
[**create-remote**](doc/cluster-create-remote.md) - Coming soon! Provision a test SSH cluster from a JSON def file.<br>
[**create-cloud**](doc/cluster-create-cloud.md) - Coming soon! Provision a secure global cluster in the Cloud using your own account.<br>
[**validate**](doc/cluster-validate.md)           - Validate a remote cluster json config file you have manually setup<br>
[**destroy**](doc/cluster-destroy.md)             - Stop and then nuke a cluster<br>
[**init**](doc/cluster-init.md)                   - Initialize a remote cluster for SPOCK<br>
[**command**](doc/cluster-command.md)             - Run `nodectl` command on one or all nodes of a cluster<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

