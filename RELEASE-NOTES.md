# pgEdge Platform Release Notes #############


## done for 23.130 as of 2023-09-21
  - new `app` cli is code complete
  - refactor `pgbench.py` & `northwind.py` to use `app.py` where appropriate
  - app.run_northwind() now supports Rate & Time same as run_pgbench()
  - on `install pgedge` tune the db before install spock so it benefits from restart
  - bump postgrest to 11.2.0
  - bump hintplan and add support for pg16
  - add support for pg16 to plv8 3.2.0
  - dramatic improvements to ACE as it is polished pre GA
  - update nclibs with new ACE reqmnts (tqdm & ordered-set)
  - welcome pg17dev & spock32dev
  - quite down new lbzip2 output 


## done for 23.129 on 2023-09-14
  - leverage lbzip2, if present, to dramatically speed installation
  - improve Dockerfile.el9 to install lbzip2
  - bump spock to 3.1.6 GA
  - bump pg16 to 16.0 for GA
  - bump oraclefdw 2.6.0 and add support for pg16
  - bump partman to 4.7.4 and add support for pg16
  - continuous improvements in quality & quantity of test scripts (thank u Susan and team)
  - fix northwind schema and data to use numeric(9,2) for prices & double for discount (was using real)
  - add support to pg16 for pgCron & pgAudit
  - bump plprofiler to 4.2.4 and support pg15 & pg16
  - bump pgVector, PostGIS, TimescaleDB, & Orafce  to latest versions 
  - rename the cluster CLI local & remote commands for consistency
  - move the new 'spock db-create` command to `db create`
  - move new 'pool' cli commands to `db pool-`
  - fix northwind demo to work with nodes that default to port 5432
  - start with first avail port after 6432 for port1 in cluster.create-local()
  - improve db-create to return json & generate a passwd if not supplied


## done for 23.128 on 2023-08-29
  - bump pg16 to rc1 
  - spock to 3.1.5 (with new security roles defined & diff2 backpatch to pg15)
  - improve efficiency of `ace diff-tables` to handle massive tables w blocks of checksums
  - bump pgcat to 1.1.1 & make available for dev and test
  - add support for plv8 3.2.0 for dev and test
  - fixed a tricky problem (reported by susan) when adding tables to a repset  w/ a wildcard (cady)
  - Fix missing static lib for uuid-ossp in pg15 & pg16 builds
  - 2nd pass at implementing spock.db_create() for supporting Dev Edition reqmnts 
  - WIP: refactor install-pgedge.py to use spock.db_create()
  - 2nd pass and document `secure` CLI (cady)
  - WIP: Windoze compatibility for `secure` & `cluster` CLI commands


## done for 23.127 on 2023-08-10
  - add support for pg16beta3 & bumped versions of pg11 thru pg15
  - add 'secure' api for interacting with pgEdge Cloud services
  - add 'requests' & 'awscli' as default nclibs
  - enhance northwind app to use schema 'northwind' rather than defaulting to 'public'
  - the basic cluster.import_remote_def() now works
  - spock.repset_add_table() only throws WARNING when table cannot be added
  - create a good dev baseline for etcd & patroni installs
  - create a good dev baseline for pgcat (throwing a sed error)
  - get devel scripts for start & stop http.server out of base directory & into devel 


## done for 23.126 on 2023-08-03
  - improve devel/setup doc & completeness
  - add support for `./nc psql 99 -f`
  - confirm 'cluster app-install northwind' works fully
  - drop unused from spock.py {validate(), tune() & install()}
  - fix regression in spock.repset_add_tables() for wildcards
  - soften bad_os warning
  - fix bug where `./nc tune` setting working_mem to 0 GB
  - 'install pgedge' now supports parms --with-patroni, --with-backrest & --with-cat
  - bump backrest from 2.46 to 2.47
  - fix install/remove for backrest not to assume pg15
  - bump plv8 to 3.2.0


## done for 23.125 as of 2023-07-31
  - bump postgis to v3.3.4
  - add pgvector-0.4.4 as an extension for pg15 & pg16
  - bump plprofiler to 4.2.2 and add support for pg16
  - more adding support for northwind (just like pgbench) as a demo/test app
  - begin adding support for cluster.import_remote_def()
  - begin adding util.wait_pg_ready()
  - begin adding support for pgbench_check

## done for 23.124 as of 2023-07-21
  - fix upgrade to 23.124 to re-install nclibs
  - fix regression on supprting ubu22-amd
  - fix spock.metrics_check() slot name
  - add support for ubu22-arm

## done for 23.123 as of 2023-07-20
  - fix race condition when initialiong cluster in Docker
  - improvements to autostarting PG for Docker
  - incremental improvements and fixes to spock.py (thank u cady)
  - remove speculative doc support for Amazon Linux 2023 (adding it back is "coming soon")
  - add 1st pass northwind as a demo/test app (alongside pgbench)
  - remove runNC() & validate() from cluster.py
  - improve cluster.command() to work with local and remote
  - improve lag monitoring & expose via spock.metrics_check()

## done for 23.122 on 2023-07-18
  - install platform specific `nclibs` and support running  on el9-amd, el9-arm, ubu22-amd & osx-amd/arm
  - bump spock to 3.1.4 (bug fixes)
  - document 'service init' & 'service config' commands as internal use only
  - ensure 'cluster create-local':
       defaults to pg16, but allows for --pg=15 override
       allows for -U, -P and -d overrides from command line
  - fix race-condition in docker compose code
  - ensure 'cluster remote-init' and 'cluster create-local' commands and working in parity 
      & with shared codebase
  - get to codeComplete for `cluster remote-init`
  - get to codeComplete for `cluster remote-reset`
  - improve flexibility of `cluster.runNC()` to handle passwordless ssh without certificates
  - improve `cluster.echo_cmd()` to handle remote ssh when os_user is presented
  - verify `cluster.echo_cmd()` handles remote ssh when ssh_key is present

## done for 23.121 on 2023-06-30
  - fix regression to allow core PG functionality to use Python 3.6+ (not require Python 3.9+)
  - improve `ace diff-tables` error handling and re-factor for going fwd
  - make 1st and 2nd passes at `cluster remote-init`
  - bump orafce to v4.3.0
  - bump curl to v2.1.1

## done for 23.120 on 2023-06-29
  - bump pg16beta1 to pg16beta2
  - improve `ace diff-tables` to optionally use checksums
  - basic v1.0 of nodectl-mqtt avaialble in dev\test mode
  - get latest pgcat & postgrest and make work for arm9 and el9 in dev\test
  - bump pglogical to v2.4.3 (for testing only)
  - improve `info` layout whilst showing `cloud-init query` (if available)
  - improve `install.py` with an `update --silent` & `info` command at end

## done for 23.119 on 2023-06-23
  - fix spock bug resulting from multiple updates in same transaction.
  - bump postgis to v3.3.3
  - scrub passwd from logs
  - fix a hanging regression when NOT in an EC2 kind of VM

## done for 23.118 on 2023-06-22
  - improve ssh support for `cluster create-local`
  - add devel/setup support for zookeeper & patroni
  - stub out starfleet support
  - add warning when not EL9+ or Ubuntu 22.04+
  - add cloud metadata to INFO command (region, az, instance_id, account_id, flavor)
  - new version of spock 3.1.3 supporting double update bug fix and other.

## done for 23.117 on 2023-06-08:
  - fix broken LLVM support in pg15.3-2 & pg16beta1-2
  - default `install pgedge` to pg16
  - improve support for docker-compose
  - these release notes
  - add support for hypopg-pg15/16
  - add support for timescaledb-pg15
  - add support for postgis-pg15
  - fix several error message typos (thank u Susan)
  - switch from using JDK11 to JDK17
  - wip `cluster create-local` use passwordless ssh on localhost


## done for 23.116 on 2023-05-20
  - `cluster create-local`
  - add support for pg16 beta1


## done for 23.115 on 2023-05-15
  - add support for pg16-dev3

