# pgEdge Platform Release Notes #############

## to do's for 23.126 and beyond
  - add support for pljava-pg15 & -pg16 (cannot find libjvm17  setting from util.get_jvm_location)
  - add support for plv8-3.2beta1-pg15
  - improve test support for patroni, etcd, haproxy
  - improve efficiency of `ace diff-tables` to handle massive tables w blocks of checksums
  - fix port numbers in cluster.create-local() (env & .json)
  - replicate ddl automagically to the spock.replicate_ddl commanf if ddl_entry_point = yes
  - test json fields for replication
  - ./nc secure init and nightly exports
  - install pooling by default

## done for 23.126 as of 2023-08-01
  - improve devel/setup doc & completeness
  - add support for `./nc psql 99 -f`
  - drop unused from spock.py {validate(), tune() & install()}
  - fix regression in spock.repset_add_tables() for wildcards
  - soften bad_os warning
  - fix bug where `./nc tune` setting working_mem to 0 GB


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

## done for 23.122 as of 2023-07-18
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

## done for 23.121 as of 2023-06-30
  - fix regression to allow core PG functionality to use Python 3.6+ (not require Python 3.9+)
  - improve `ace diff-tables` error handling and re-factor for going fwd
  - make 1st and 2nd passes at `cluster remote-init`
  - bump orafce to v4.3.0
  - bump curl to v2.1.1

## done for 23.120 as of 2023-06-29
  - bump pg16beta1 to pg16beta2
  - improve `ace diff-tables` to optionally use checksums
  - basic v1.0 of nodectl-mqtt avaialble in dev\test mode
  - get latest pgcat2 & postgrest and make work for arm9 and el9 in dev\test
  - bump pglogical to v2.4.3 (for testing only)
  - improve `info` layout whilst showing `cloud-init query` (if available)
  - improve `install.py` with an `update --silent` & `info` command at end

## done for 23.119 as of 2023-06-23
  - fix spock bug resulting from multiple updates in same transaction.
  - bump postgis to v3.3.3
  - scrub passwd from logs
  - fix a hanging regression when NOT in an EC2 kind of VM

## done for 23.118 as of 2023-06-22
  - improve ssh support for `cluster create-local`
  - add devel/setup support for zookeeper & patroni
  - stub out starfleet support
  - add warning when not EL9+ or Ubuntu 22.04+
  - add cloud metadata to INFO command (region, az, instance_id, account_id, flavor)
  - new version of spock 3.1.3 supporting double update bug fix and other.

## done for 23.117 as of 2023-06-08:
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


## done for 23.116 as of 2023-05-20
  - `cluster create-local`
  - add support for pg16 beta1


## done for 23.115 as of 2023-05-15
  - add support for pg16-dev3

