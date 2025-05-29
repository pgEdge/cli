
## SYNOPSIS
    ./pgedge ace COMMAND

## COMMANDS
    COMMAND is one of the following:
     table-diff          # Compare a table across a cluster and produce a report showing any differences.
     table-repair        # Repair a table across a cluster by fixing data inconsistencies identified in a table-diff operation.
     table-rerun         # Reruns a table diff operation based on a previous diff file.
     repset-diff         # Compare a repset across a cluster and produce a report showing any differences.
     schema-diff         # Compare a schema across a cluster and produce a report showing any differences.
     spock-diff          # Compare the spock metadata across a cluster and produce a report showing any differences.
     spock-exception-update# Updates the Spock exception status for a specified cluster and node.
     start               # Start the ACE background scheduler and API.
