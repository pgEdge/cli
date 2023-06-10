# pgedge/nodectl - Release Notes

## Completed so far in 23.118 as of 2023-06-09
  - improve ssh support for 'cluster create-local'
  - add devel/setup support for zookeeper & patroni
  - stub out starfleet support
  - add bad-os-warning when not EL9+ or Ubuntu 22.04+


## scheduled for 23.118++
  - add support for pljava-pg15 & -pg16 (cannot find libjvm17  setting from util.get_jvm_location)
  - get latest pgcat2 & postgrest and make work for arm9 and el9
  - make `cluster create-remote` work with same logic as `create-local`
  - add test support for kafka, & patroni
  - add test support for pgcat & fs (failover-slots)
  - add devel/setup support for confluent/kafka


########################################################

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







