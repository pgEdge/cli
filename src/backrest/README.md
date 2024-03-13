# PostgreSQL Backup and Restore with pgBackRest

This guide provides instructions for installing PostgreSQL using the pgEdge CLI, configuring backups with pgBackRest, and restoring databases from backups. It covers creating a backup stanza, backup and restore operations.

## Prerequisites
Before proceeding, ensure that you have installed the pgEdge Platform. Refer to the pgEdge documentation for installation guidance. You will need to either navigate to your pgedge installation directory or specify the path to your pgEdge installation when executing the commands outlined below.

## Installation and Initial Configuration

1. Install PostgreSQL 16 using `pgedge`:

```bash
./pgedge install pg16 --start
```

2. Install pgBackRest and configure the backup environment. This step creates a stanza for pgBackRest. 

Use the following command to install pgBackRest and create the pgBackRest artifacts:

```bash
./pgedge install backrest
```

### Help

```sh
pgedge backrest 

SYNOPSIS
    pgedge backrest COMMAND

COMMANDS
    COMMAND is one of the following:
     backup              # Perform a backup using the specified backup tool and backup type,
                         # storing the backup at the specified backup path.
     restore             # Restore database from a specified backup or to a specific point in time.
     create_replica      # Create a replica by restoring from a backup and configure it. 
                         # If specified, perform PITR. Optionally, initiate a backup before creating the replica.
     list                # List backups using the configured backup tool.
     config              # List configuration parameter configured backup tool.
```

### Configuration
pgbackrest cab be configured using pgedge's cli by using the pgedge environment variables

```sh
pgedge set BACKUP STANZA pg16
```

This will set the stanza name pg16, similarly all of these can be configured using set commands.

```
pgedge backrest config
```

```
#######################################################################
#              BACKUP_TOOL: pgbackrest                             
#                   STANZA: pg16                                   
#                 DATABASE: postgres                               
#                  PG_PATH: /home/pgedge/dev/cli/out/posix/data/pg16
#              SOCKET_PATH: /tmp                                   
#                  PG_USER: pgedge                                  
#         REPO_CIPHER_TYPE: aes-256-cbc                            
#                REPO_PATH: /var/lib/pgbackrest                    
# REPO_RETENTION_FULL_TYPE: count                                  
#      REPO_RETENTION_FULL: 7                                      
#             PRIMARY_HOST: 127.0.0.1                              
#             PRIMARY_PORT: 5432                                   
#             PRIMARY_USER: pgedge                                  
#         REPLICA_PASSWORD: 123                                    
#     RECOVERY_TARGET_TIME:                                        
#             RESTORE_PATH: /home/pgedg/pg16                       
#               REPO1_TYPE: local                                  
#              BACKUP_TYPE: full                                   
#                S3_BUCKET:                                        
#                S3_REGION:                                        
#              S3_ENDPOINT:                                        
#######################################################################
```

```sh
pgedge backrest create-replica --help

SYNOPSIS
    backrest.py create-replica <flags>

DESCRIPTION
    Create a replica by restoring from a backup and configure it. If specified, perform PITR. Optionally, initiate a backup before creating the replica.

FLAGS
    -b, --backup_id=BACKUP_ID
        The ID of the backup to use for creating the replica. If not provided, the latest backup will be used unless do_backup is True.
    
    -r, --recovery_target_time=RECOVERY_TARGET_TIME
        The target time for PITR.
    
    -d, --do_backup=DO_BACKUP
        Whether to initiate a new backup before creating the replica. Defaults to False.
```



## Backup Information
To view detailed information about the backups, use the `backrest info` command:

```sh
bash-5.1$ ./pgedge backrest list
+---------------+------------------+---------------------+---------------------+-------------+-----------+---------------+-------------+
| Stanza Name   | Label            | Start Time          | End Time            | WAL Start   | WAL End   | Backup Type   | Size (GB)   |
+===============+==================+=====================+=====================+=============+===========+===============+=============+
| pg16          | 20240313-235959F | 2024-03-13 18:59:59 | 2024-03-13 19:00:02 | 0/2000028   | 0/2000138 | full          | 0.02 GB     |
+---------------+------------------+---------------------+---------------------+-------------+-----------+---------------+-------------+
| pg16          | 20240314-000023F | 2024-03-13 19:00:23 | 2024-03-13 19:00:26 | 0/4000028   | 0/4000100 | full          | 0.02 GB     |
+---------------+------------------+---------------------+---------------------+-------------+-----------+---------------+-------------+
| pg16          | 20240314-000614F | 2024-03-13 19:06:14 | 2024-03-13 19:06:17 | 0/6000028   | 0/6000100 | full          | 0.02 GB     |
+---------------+------------------+---------------------+---------------------+-------------+-----------+---------------+-------------+
| pg16          | 20240314-001937F | 2024-03-13 19:19:37 | 2024-03-13 19:19:39 | 0/8000028   | 0/8000100 | full          | 0.02 GB     |
+---------------+------------------+---------------------+---------------------+-------------+-----------+---------------+-------------+
```
## Conclusion
This document provides a step-by-step guide to using pgEdge to install PostgreSQL 16, configuring pgBackRest for backup and restore operations, and managing the backup lifecycle. By following these steps, you can ensure that your PostgreSQL databases are backed up securely and can be restored efficiently when necessary.




