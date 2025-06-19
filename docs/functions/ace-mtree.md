
## SYNOPSIS
    ./pgedge ace mtree COMMAND

## DESCRIPTION
    Use Merkle Trees for efficient table diffs.

## COMMANDS
    COMMAND is one of the following:
     build               # Builds a new Merkle tree for a table.
     init                # Initialises the database with necessary objects for Merkle trees.
     table-diff          # Compares Merkle trees of a table across cluster nodes.
     teardown            # Removes Merkle tree objects.
     update              # Updates an existing Merkle tree.
