## SYNOPSIS
    ./pgedge ace COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     table-diff          # Efficiently compare tables across cluster using checksums and blocks of rows
     diff-schemas        # Compare Postgres schemas on different cluster nodes
     diff-spock          # Compare spock meta data setup on different cluster nodes
     table-repair        # Apply changes from a table-diff source of truth to destination table
     table-rerun         # Re-run differences on the results of a recent table-diff
     repset-diff         # Loop thru a replication-sets tables and run table-diff on them
