
## SYNOPSIS
    ./pgedge ace mtree build CLUSTER_NAME TABLE_NAME <flags>

## DESCRIPTION
    Builds a new Merkle tree for a table.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster.
    TABLE_NAME
        Schema-qualified table name.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database.
    
    -a, --analyse=ANALYSE
        Run ANALYZE on the table.
    
    --recreate_objects=RECREATE_OBJECTS
        Drop and recreate Merkle tree objects.
    
    -b, --block_size=BLOCK_SIZE
        Rows per leaf block.
    
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Max CPU for parallel operations.
    
    -w, --write_ranges=WRITE_RANGES
        Write block ranges to a JSON file.
    
    --ranges_file=RANGES_FILE
        Path to a file with pre-computed ranges.
    
    -n, --nodes=NODES
        Comma-separated subset of nodes.
    
    -q, --quiet_mode=QUIET_MODE
        Suppress output.
    
    -o, --override_block_size=OVERRIDE_BLOCK_SIZE
        Allow unsafe block size.
    
