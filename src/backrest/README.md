# PostgreSQL Backup and Restore with pgBackRest

This document outlines the steps to install PostgreSQL 16 with the pgedge CLI, configure backups with pgBackRest, and restore a database from a backup. The process includes creating a backup stanza, starting the backrest service, and managing backups and restores.

Before performing the steps that follow, you need to install pgEdge Platform.  For details, see the pgEdge documentation. Then, navigate into the `pgedge` directory, or specify the path to the pgedge installation to invoke the commands that follow. 

## Installation and Initial Configuration

1. Install PostgreSQL 16 using `pgedge`:

```bash
./pgedge install pg16 --start
```


2. Install pgBackRest and configure the backup environment. This step creates a stanza for pgBackRest and initiates the backup service to run in the background. A stanza is a configuration file that specifies your database location, connection information, a backup schedule, and other backup details. Backups will occur according to an installer-generated JSON schedule file; you can customize your schedule file to best suit your use. 

Use the following command to install pgBackRest and create the pgBackRest artifacts:

```bash
./pgedge install backrest
./pgedge config backrest
```

### Help 
```
bash-5.1$  ./pgedge backrest

SYNOPSIS
    backrest.py COMMAND

COMMANDS
    COMMAND is one of the following:
     create-replica      # pgedge: Create read-only replica, with an option for PITR
                           Usage: pgedge backrest create-replica --stanza=stanza --restore-path=<path> --set=<id> 
                           [--primary-host=<ip>] [--primary-port=<port>] [primary--user=<user>] 
                           [--replica-password=<password>] [--recovery-target-time=<time>]
     service-log         # pgedge: Get remote service log. Usage: pgedge backrest service-log
     service-status      # pgedge: Check service status. Usage: pgedge backrest service-status
     list-backups        # pgedge: List dynamic stanza name, start time, end time, WAL start,
                           and WAL end using pgbackrest info command. Usage: pgedge backrest list-backups
     annotate            # Add or modify backup annotation. pgedge backrest  annotate
     archive-get         # Get a WAL segment from the archive. pgedge backrest  archive-get
     archive-push        # Push a WAL segment to the archive. pgedge backrest  archive-push
     backup              # Backup a database cluster. pgedge backrest  backup
     check               # Check the configuration. pgedge backrest  check
     expire              # Expire backups that exceed retention. pgedge backrest  expire
     info                # Retrieve information about backups. pgedge backrest  info
     repo-get            # Get a file from a repository. pgedge backrest  repo-get
     repo-ls             # List files in a repository. pgedge backrest  repo-ls
     server              # pgBackRest server. pgedge backrest  server
     server-ping         # Ping pgBackRest server. pgedge backrest  server-ping
     stanza-create       # Create the required stanza data. pgedge backrest  stanza-create
     stanza-delete       # Delete a stanza. pgedge backrest  stanza-delete
     stanza-upgrade      # Upgrade a stanza. pgedge backrest  stanza-upgrade
     start               # Allow pgBackRest processes to run. pgedge backrest  start
     stop                # Stop pgBackRest processes from running. pgedge backrest  stop
     verify              # Verify contents of the repository. pgedge backrest  verify
     version             # Get version. pgedge backrest  version

```

### Managing a Backup Schedule

Use the following .json file as a starting point to configure your backup schedule.
```jason
{
  "jobs": [
    {   
      "type": "full",
      "schedule": {
        "daily": {
          "time": "01:00"
        },
        "weekly": {
          "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }
      }   
    },  
    {   
      "type": "incr",
      "interval": 60
    }   
  ]
}

This document outlines the backup strategy defined in the schedule file, which includes two types of backups: full and incremental. 

#### Full Backup Schedule

- **Type**: Full
  - A full backup captures the entire state of the database at the point in time it runs.

- **Daily Schedule**:
  - **Time**: 01:00 AM daily
    - Indicates a full backup is initiated every day at this specific time. The time is configurable to any preferred hour.

- **Weekly Schedule**:
  - **Days**: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    - Specifies that the daily full backup at 01:00 AM occurs every day of the week, ensuring daily coverage without any gaps. Days are configurable to limit full backups to specific days if necessary.

#### Incremental Backup Schedule

- **Type**: Incremental
  - An incremental backup only captures the changes made since the last backup (full or incremental), which saves space and can reduce backup time.

- **Interval**: 
  - 60 minutes
    - An incremental backup is triggered every hour, capturing changes since the last backup. This frequency aims to minimize data loss by ensuring recent changes are regularly backed up.

#### Configurability

- **Full Backups**: 
  - The execution time for full backups can be adjusted to any hour of the day to accommodate periods of low database activity or maintenance windows.

- **Incremental Backups**:
  - The interval for incremental backups can be customized based on the desired balance between backup frequency and resource usage.

#### Operation

- A daemon or scheduled task (`backrest daemon`) monitors the schedule file and initiates the respective backup operations according to the defined timings and intervals. This automated process facilitates regular data backup based on the configured schedule, minimizing manual intervention.

This backup strategy combines the thorough data protection of nightly full backups with the efficiency of hourly incremental backups, offering a comprehensive approach to database backup management.

```


## Monitoring Backups

To monitor the output of the `backrest` service, use the following command:

```bash
pgedge backrest service-log
```
The command returns output similar to:

<details>
<summary style="cursor:pointer; outline:none; font-weight:bold; border-bottom:1px solid #ccc;">Click to expand/collapse</summary>

<blockquote style="margin: 0 0 8px; padding: 5px 10px; border-left: 3px solid #ccc; background-color: #f9f9f9;">
```sh
Feb 16 21:42:00 nctl backrest.py[599125]: 2024-02-16 21:42:00.845 P00   INFO: backup command begin 2.50: --config=/etc/pgbackrest/pgbackrest.conf --exec-id=599125-3e60b385 --log-level-console=info --pg1-database=postgres --pg1-host=localhost --pg1-host-user=ibrar --pg1-path=/home/ibrar/dev/cli/out/posix/data/pg16 --pg1-socket-path=/tmp --pg1-user=ibrar --repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo1-path=/var/lib/pgbackrest --repo1-retention-full=7 --stanza=pg16 --type=full
Feb 16 21:42:01 nctl backrest.py[599125]: 2024-02-16 21:42:01.759 P00   INFO: execute non-exclusive backup start: backup begins after the next regular checkpoint completes
Feb 16 21:42:02 nctl backrest.py[599125]: 2024-02-16 21:42:02.263 P00   INFO: backup start archive = 000000010000000000000005, lsn = 0/5000028
Feb 16 21:42:02 nctl backrest.py[599125]: 2024-02-16 21:42:02.263 P00   INFO: check archive for prior segment 000000010000000000000004
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.390 P00   INFO: execute non-exclusive backup stop and wait for all WAL segments to archive
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.593 P00   INFO: backup stop archive = 000000010000000000000005, lsn = 0/5000100
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.596 P00   INFO: check archive for segment(s) 000000010000000000000005:000000010000000000000005
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.701 P00   INFO: new backup label = 20240216-214201F
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.719 P00   INFO: full backup size = 22.7MB, file total = 971
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.719 P00   INFO: backup command end: completed successfully (3879ms)
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.719 P00   INFO: expire command begin 2.50: --config=/etc/pgbackrest/pgbackrest.conf --exec-id=599125-3e60b385 --log-level-console=info --repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo1-path=/var/lib/pgbackrest --repo1-retention-full=7 --stanza=pg16
Feb 16 21:42:04 nctl backrest.py[599125]: 2024-02-16 21:42:04.720 P00   INFO: expire command end: completed successfully
```
</blockquote>

</details>

To check the status of backrest service file


```sh
pgedge backrest service-status
```


<details>
<summary style="cursor:pointer; outline:none; font-weight:bold; border-bottom:1px solid #ccc;">Click to expand/collapse</summary>
<blockquote style="margin: 0 0 8px; padding: 5px 10px; border-left: 3px solid #ccc; background-color: #f9f9f9;">

```
backrest.service - pgBackRest Backup Service
     Loaded: loaded (/etc/systemd/system/backrest.service; enabled; preset: disabled)
     Active: active (running) since Tue 2024-02-20 23:29:48 PKT; 5min ago
   Main PID: 656667 (python3)
      Tasks: 1 (limit: 22596)
     Memory: 16.7M
        CPU: 318ms
     CGroup: /system.slice/backrest.service
             └─656667 python3 /usr/bin/backrestd.py --config=/etc/pgbackrest/backrest.json --user=ibrar --stanza=pg15

Feb 20 23:31:01 nctl backrestd.py[656739]: 2024-02-20 23:31:01.734 P00   INFO: backup start archive = 000000010000000000000003, lsn = 0/3000028
Feb 20 23:31:01 nctl backrestd.py[656739]: 2024-02-20 23:31:01.734 P00   INFO: check archive for prior segment 000000010000000000000002
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.370 P00   INFO: execute non-exclusive backup stop and wait for all WAL segments to archive
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.571 P00   INFO: backup stop archive = 000000010000000000000003, lsn = 0/3000138
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.575 P00   INFO: check archive for segment(s) 000000010000000000000003:000000010000000000000003
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.679 P00   INFO: new backup label = 20240220-233101F
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.691 P00   INFO: full backup size = 22.6MB, file total = 969
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.691 P00   INFO: backup command end: completed successfully (3360ms)
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.691 P00   INFO: expire command begin 2.50: --config=/etc/pgbackrest/pgbackrest.conf --exec-id=656739-c948c229 --log-level-console=info --repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-2>
Feb 20 23:31:03 nctl backrestd.py[656739]: 2024-02-20 23:31:03.692 P00   INFO: expire command end: completed successfully (1ms)
```

</blockquote>

</details>


## Backup Information
To view detailed information about the backups, use the `backrest info` command:

```sh
+---------------+-----------------------------------+---------------------+---------------------+-------------+-----------+---------------+----------+
| Stanza Name   | Label                             | Start Time          | End Time            | WAL Start   | WAL End   | Backup Type   |     Size |
+===============+===================================+=====================+=====================+=============+===========+===============+==========+
| pg16          | 20240308-235101F                  | 08-03-2024 18:51:01 | 08-03-2024 18:51:04 | 0/3000028   | 0/3000138 | full          | 23825190 |
+---------------+-----------------------------------+---------------------+---------------------+-------------+-----------+---------------+----------+
| pg16          | 20240309-000201F                  | 08-03-2024 19:02:01 | 08-03-2024 19:02:07 | 0/6000028   | 0/6000138 | full          | 23813043 |
+---------------+-----------------------------------+---------------------+---------------------+-------------+-----------+---------------+----------+
| pg16          | 20240309-000201F_20240309-000302I | 08-03-2024 19:03:02 | 08-03-2024 19:03:04 | 0/8000028   | 0/8000100 | incr          | 23813043 |
+---------------+-----------------------------------+---------------------+---------------------+-------------+-----------+---------------+----------+
| pg16          | 20240309-000201F_20240309-000506I | 08-03-2024 19:05:06 | 08-03-2024 19:05:07 | 0/A000028   | 0/A000100 | incr          | 23813043 |
+---------------+-----------------------------------+---------------------+---------------------+-------------+-----------+---------------+----------+
```

## Create read-only replica

```sh
pgedge backrest create-replica --stanza=pg16 --restore-path=/home/ibrar/test --backup_id=20240308-235101F
#   /home/ibrar/dev/cli/out/posix/backrest/backrest.py create-replica --stanza=pg16 --restore-path=/home/ibrar/test --backup_id=20240308-235101F
2024-03-09 00:06:36.128 P00   INFO: restore command begin 2.50: --delta --exec-id=892533-f16f1bd7 --log-level-console=info --pg1-path=/home/ibrar/test --repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo1-path=/var/lib/pgbackrest --set=20240308-235101F --stanza=pg16
2024-03-09 00:06:36.131 P00   INFO: repo1: restore backup set 20240308-235101F, recovery will start at 2024-03-08 23:51:01
2024-03-09 00:06:36.131 P00   INFO: remap data directory to '/home/ibrar/test'
2024-03-09 00:06:36.131 P00   INFO: remove invalid files/links/paths from '/home/ibrar/test'
2024-03-09 00:06:36.357 P00   INFO: write updated /home/ibrar/test/postgresql.auto.conf
2024-03-09 00:06:36.358 P00   INFO: restore global/pg_control (performed last to ensure aborted restores cannot be started)
2024-03-09 00:06:36.358 P00   INFO: restore size = 22.7MB, file total = 972
2024-03-09 00:06:36.359 P00   INFO: restore command end: completed successfully (232ms)
Backup 20240308-235101F successfully restored to /home/ibrar/test.
Configurations modified to configure as replica. standby.signal file created.
Make sure your pg_hba.conf is configured to allow connection from this IP
```

## Restoring from Backup
To restore a database from a backup, use the following command, specifying the stanza, restore type, and target date:

```sh
./pgedge backrest --stanza=pg16 --type=time --target="2024-16-02" restore
```

As pgBackRest restores your database, relevant information is displayed:

```sh

2024-02-16 21:54:03.096 P00   INFO: restore command begin 2.50: --exec-id=599613-ffb7411f --log-level-console=info --pg1-path=/home/ibrar/data --repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo1-path=/var/lib/pgbackrest --stanza=pg16
2024-02-16 21:54:03.100 P00   INFO: repo1: restore backup set 20240216-214201F, recovery will start at 2024-02-16 21:42:01
2024-02-16 21:54:03.100 P00   INFO: remap data directory to '/home/ibrar/data'
2024-02-16 21:54:03.457 P00   INFO: write updated /home/ibrar/data/postgresql.auto.conf
2024-02-16 21:54:03.457 P00   INFO: restore global/pg_control (performed last to ensure aborted restores cannot be started)
2024-02-16 21:54:03.458 P00   INFO: restore size = 22.7MB, file total = 971
2024-02-16 21:54:03.458 P00   INFO: restore command end: completed successfully (363ms)
```

## Post-Restore Configuration
After restoring from a backup, you must update the `postgresql.auto.conf` file to enable archive mode and set the archive command:

```sh
archive_mode = 'on'
archive_command = 'pgbackrest --stanza=pg16 archive-push %p'
```
Additionally, you may need to configure `recovery_target` settings to control the restore process further.

## Conclusion
This document provides a step-by-step guide to using pgEdge to install PostgreSQL 16, configuring pgBackRest for backup and restore operations, and managing the backup lifecycle. By following these steps, you can ensure that your PostgreSQL databases are backed up securely and can be restored efficiently when necessary.




