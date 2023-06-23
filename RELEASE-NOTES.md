# pgedge/nodectl - Release Notes

## done so far for 23.120 as of Jun23
  - bump pglogical to 2.4.3 (for testing only)
  - improve INFO layout whilst showing the unique-id

## scheduled for 23.120++
  - add support for pljava-pg15 & -pg16 (cannot find libjvm17  setting from util.get_jvm_location)
  - get latest pgcat2 & postgrest and make work for arm9 and el9
  - make `cluster create-remote` work with same logic as `create-local`
  - add test support for patron4, etcd, haproxy

########################################################
## done for 23.119 as of 2023-0623
  - bump postgis to v3.3.3
  - scrub passwd from logs
  - fix a hanging regression when NOT in an EC2 kind of VM

## done for 23.118 2023-06-22
  - improve ssh support for 'cluster create-local'
  - add devel/setup support for zookeeper & patroni
  - stub out starfleet support
  - add warning when not EL9+ or Ubuntu 22.04+
  - add cloud metadata to INFO command (region, az, instance_id, account_id, flavor)
  - new version of spock 3.1.3 supporting double update bug fix and other.

## done for 23.117  2023-06-08:
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

