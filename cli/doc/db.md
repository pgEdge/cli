## SYNOPSIS
    ./nodectl db COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     create              # Create a pg db with spock installed into it.
     set-guc             # Set GUC
     show-guc            # Show GUC
     dump                # Dump a database, schema, object from the source dsn to a file
     restore             # Restore a database, schema, object from a file to the target_dsn
     migrate             # Migrate a database, schema, object from a source_dsn to the target_dsn
