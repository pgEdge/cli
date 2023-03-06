# PGEDGE NODECTL CLUSTER CONTROLLER
Installation and configuration of a pgEdge SPOCK cluster

## Synopsis
    ./nodectl spock <command> [parameters] [options]   

[**create-local**](doc/cluster-create-local.md)   - Create local cluster of N pgEdge nodes on different ports<br>
[**destroy**](doc/cluster-destroy.md)             - Stop and then nuke a cluster<br>
[**validate**](doc/cluster-validate.md)           - Validate a remote cluster configuration<br>
[**init**](doc/cluster-init.md)                   - Initialize a remote cluster for SPOCK<br>
[**command**](doc/cluster-command.md)             - Run `nodectl` command on one or all nodes of a cluster<br>
[**diff-tables**](doc/cluster-diff-tables.md)     - Compare table on different cluster nodes<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

