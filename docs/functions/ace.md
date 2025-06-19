
## SYNOPSIS
    ./pgedge ace COMMAND

## DESCRIPTION
    The Active Consistency Engine of pgEdge.

## COMMANDS
    COMMAND is one of the following:
     mtree               # Use Merkle Trees for efficient table diffs.
     repset-diff         # Compare a repset across a cluster and produce a report showing any differences.
     schema-diff         # Compare a schema across a cluster and produce a report showing any differences.
     spock-diff          # Compare the spock metadata across a cluster and produce a report showing any differences.
     spock-exception-update# Update the Spock exception status for a specified cluster and node.
     start               # Start the ACE background scheduler and API.
     table-diff          # Compare a table across a cluster and produce a report showing differences, if any.
     table-repair        # Repair a table across a cluster by fixing data inconsistencies identified in a table-diff operation.
     table-rerun         # Rerun a table diff operation based on a previous diff file.
